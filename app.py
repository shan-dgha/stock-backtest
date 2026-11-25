"""
app.py —— 数据看板（面向对象版）：把 dash03.py 的"全局变量 + 平铺脚本"改成类

结构和 dash03.py 一一对应，区别只在组织方式：

    dash03.py（脚本式）              app.py（类式）
    ------------------------------  ----------------------------------
    模块级全局 df / win / table…    全部变成 MainWindow 的 self.xxx 属性
    load_file() / draw_chart()…     变成 MainWindow 的方法
    数据读写直接写在界面代码里       抽到 data_utils.py（纯数据层，不碰 Qt）
    顶部一气写到底                   拆成 __init__（初始化）+ build_ui（搭界面）

为什么要分成"数据层 / 界面层"：
    画图、取列名、把字符串列转数字这些逻辑，将来换界面（比如换到 Web）还能复用；
    界面代码里只剩"把算好的 x/y 塞给曲线"这种纯展示动作。
    这也是本项目的收尾版本：能跑、能读、能改。

运行：python app.py（同目录需有 demo_data.csv、data_utils.py）
依赖：pip install pandas numpy pyqtgraph PySide6
"""

import os

import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,     # 应用主体，负责事件循环
    QWidget,          # 窗口底座（MainWindow 继承它）
    QVBoxLayout,      # 垂直布局（外层）
    QHBoxLayout,      # 水平布局（顶栏）
    QSplitter,        # 可拖动分隔容器（上下分栏）
    QTableWidget,     # 表格控件
    QTableWidgetItem, # 表格单元格
    QPushButton,      # 按钮
    QLabel,           # 文本标签
    QComboBox,        # 下拉框（选横轴/纵轴列）
    QFileDialog,      # 系统"打开文件"对话框
)

# 自己写的模块放在第三组单独导入（PEP 8 习惯：标准库 / 第三方 / 本地 分开）
# 注意：这里 import 的是整个模块而不是 from data_utils import xxx，
# 是为了让调用处写成 data_utils.read_csv(...)，一眼能看出"这是数据层的活"
import data_utils

# BASE_DIR 用 __file__ 推出来，所以不管从哪个工作目录运行都能找到 demo_data.csv
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEMO_PATH = os.path.join(BASE_DIR, "demo_data.csv")

# 表格最多填这么多行：逐格 setItem 上万行会卡死界面
MAX_ROWS = 500


class MainWindow(QWidget):
    """整个看板窗口。每个实例自带一份数据（self.df）和一套控件，互不干扰。"""

    def __init__(self):
        # 必须先调父类构造：QWidget 的 C++ 对象是在这一步才真正创建出来的，
        # 不调 super().__init__() 后面所有 setWindowTitle / setLayout 都会崩
        super().__init__()

        # 先把 self.df 置为 None：build_ui 期间可能触发 draw_chart（下拉框变化），
        # 那时还没有数据，先在"属性一定存在"上兜底
        self.df = None

        self.setWindowTitle("数据看板")
        self.resize(1000, 700)   # 宽 1000、高 700 像素

        # 搭界面和载初值分成两件事：
        # build_ui 只管"把控件造出来 + 连好信号"，不碰数据；
        # 数据载入放在最后，因为要等控件都建好了才能往里填
        self.build_ui()
        if os.path.exists(DEMO_PATH):
            self.load_file(DEMO_PATH)

    def build_ui(self):
        """创建全部控件、组装布局、连接信号。

        注意控件都存成 self.xxx：因为 __init__ 返回后局部变量就没了，
        而后面 on_open / fill_table 还要用到按钮、标签、表格、曲线。
        （其实被塞进布局的控件由父控件在 C++ 侧持有所有权，不会消失；
          但要在方法里访问，就必须留一个 Python 侧的引用。）
        布局对象（top / splitter / layout）只在本次调用里用一次，
        所以可以是局部变量，不用挂到 self 上。
        """
        # ---- 顶部控件 ----
        self.btn_open = QPushButton("打开文件")
        self.label_file = QLabel("未载入")
        self.label_file.setStyleSheet("color:#666;")   # 灰色：还没载入数据

        self.cmb_x = QComboBox()
        self.cmb_y = QComboBox()
        self.cmb_x.setMinimumWidth(120)
        self.cmb_y.setMinimumWidth(120)

        # 顶栏：按钮 | 文件名（拉伸因子 1，吃掉剩余宽度）| 横轴 | 纵轴
        top = QHBoxLayout()
        top.addWidget(self.btn_open)
        top.addWidget(self.label_file, 1)
        top.addWidget(QLabel("横轴："))
        top.addWidget(self.cmb_x)
        top.addWidget(QLabel("纵轴："))
        top.addWidget(self.cmb_y)

        # ---- 表格 ----
        self.table = QTableWidget()

        # ---- 图表 ----
        pg.setConfigOptions(antialias=True)   # 抗锯齿，曲线不出毛刺
        self.plot = pg.PlotWidget(background="w")
        self.plot.showGrid(x=True, y=True, alpha=0.3)
        # 先建一条空曲线占住位置，后面 draw_chart 只 setData 换数据，不重建
        self.curve = self.plot.plot([], [], pen=pg.mkPen("#2f6fed", width=2))

        # ---- 上下可拖动分隔：表格 / 图表 ----
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(self.table)
        splitter.addWidget(self.plot)
        splitter.setSizes([300, 400])   # 只是初始像素比例，拖动后记住用户的比例

        # 最外层：顶栏一行 + 分隔器占满剩余空间
        layout = QVBoxLayout()
        layout.addLayout(top)        # 嵌套水平布局
        layout.addWidget(splitter)
        self.setLayout(layout)

        # ---- 信号连接放在最后：控件都建好了再连，槽函数里访问 self.xxx 才安全 ----
        # 传的是绑定方法（self.on_open），不带括号：事件发生时才调用
        self.btn_open.clicked.connect(self.on_open)
        # currentIndexChanged 会带一个 int 下标进来，draw_chart 的 index 参数就是接它的
        self.cmb_x.currentIndexChanged.connect(self.draw_chart)
        self.cmb_y.currentIndexChanged.connect(self.draw_chart)

    # ------------------------------------------------------------ 交互与刷新
    def on_open(self):
        """点【打开文件】：弹系统对话框选 CSV，选中后交给 load_file。"""
        # 第二个参数是"父窗口"，传 self 让对话框居中在本窗口并跟随它置顶
        path, _ = QFileDialog.getOpenFileName(self, "选择数据文件", "", "CSV 文件 (*.csv)")
        if path:
            self.load_file(path)

    def load_file(self, path):
        """读 CSV → 刷新文件名 → 表格 → 下拉框 → 曲线。

        注意这里不需要 global：数据挂在 self.df 上，实例方法直接改属性即可。
        这正是改成类以后最直接的收益——不再有"多个实例共用一份全局 df"的隐患。
        """
        try:
            # 具体怎么读 CSV 交给数据层，界面层不关心 pandas 的细节
            self.df = data_utils.read_csv(path)
        except Exception as e:
            self.label_file.setText(f"读取失败：{e}")
            return   # 读失败就提前退出，别拿 None 往下走
        self.label_file.setText(os.path.basename(path))   # 只显示文件名，不显示长路径
        self.fill_table()    # 1) 表格
        self.fill_combos()   # 2) 下拉框（列名依赖新数据，必须在画图前重填）
        self.draw_chart()    # 3) 曲线

    def fill_table(self):
        """把 self.df 的前 MAX_ROWS 行逐格写进表格。"""
        rows = min(len(self.df), MAX_ROWS)
        self.table.setRowCount(rows)
        self.table.setColumnCount(len(self.df.columns))
        # 列名统一由数据层转成字符串列表，省得界面层到处写 str()
        self.table.setHorizontalHeaderLabels(data_utils.column_names(self.df))
        for r in range(rows):
            for c in range(len(self.df.columns)):
                # iloc 按位置取值；单元格只收字符串，所以 str() 一下
                self.table.setItem(r, c, QTableWidgetItem(str(self.df.iloc[r, c])))

    def fill_combos(self):
        """按当前数据重填"横轴/纵轴"两个下拉框：横轴给全部列，纵轴只给数值列。"""
        names = data_utils.column_names(self.df)
        nums = data_utils.numeric_columns(self.df)   # 文字列画不出线，过滤掉

        # blockSignals：临时屏蔽 currentIndexChanged。
        # clear()/addItems() 会触发选中项变化，不屏蔽就会连着重画好几次，
        # 而且中间那一刻框是空的。改完再恢复。
        self.cmb_x.blockSignals(True)
        self.cmb_y.blockSignals(True)
        self.cmb_x.clear()
        self.cmb_y.clear()
        self.cmb_x.addItems(names)
        self.cmb_y.addItems(nums if nums else names)   # 没有数值列就退回全部列，至少不空
        self.cmb_x.blockSignals(False)
        self.cmb_y.blockSignals(False)

    def draw_chart(self, index=None):
        """按两个下拉框当前的选择重画曲线。

        index：currentIndexChanged(int) 带过来的新下标，这里用不到，
               但槽函数得能接收它，所以留个可选参数。
        """
        if self.df is None:   # 还没载入数据（启动阶段下拉框变化会走到这里）
            return
        xcol = self.cmb_x.currentText()   # currentText 拿"列名"，不是下标
        ycol = self.cmb_y.currentText()
        if not xcol or not ycol:
            return
        # 取 x/y 的规则（能转数字就用列值，否则退回行号）全在数据层里，
        # 界面层只负责"把算好的数据喂给曲线"
        x, y = data_utils.to_xy(self.df, xcol, ycol)
        self.plot.setLabel("left", ycol)   # 纵轴标题跟着列名走
        self.curve.setData(x, y)           # setData 是整体替换，不会叠出多条线


def main():
    """程序入口：先建 QApplication，再建窗口。

    顺序不能反：所有 Qt 控件都必须在 QApplication 之后创建。
    """
    app = QApplication([])      # 每个 Qt 程序有且只有一个，负责事件循环
    win = MainWindow()
    win.show()                  # 不调用它窗口不会出现
    app.exec()                  # 进入事件循环，窗口关闭后返回，脚本结束


# 只有直接运行本文件才执行 main()；
# 被别人 import 时不会弹窗口，方便以后复用它做测试
if __name__ == "__main__":
    main()