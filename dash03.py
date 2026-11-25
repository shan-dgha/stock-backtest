"""
dash03.py —— pandas + PySide6 + pyqtgraph：可切换坐标轴的"数据看板"（v3）

相对 dashboard02.py 的改进：
  1. 启动时若同目录有 demo_data.csv 就自动载入（不用先点按钮）
     —— 用 BASE_DIR 拼绝对路径，所以不管从哪个目录运行都能找到
  2. 顶部多了「横轴 / 纵轴」两个下拉框，可以自己挑哪一列画图，
     换列时自动重画（不用改代码里写死的中文列名）
  3. 纵轴只列出数值列（pd.api.types.is_numeric_dtype 判断），避免选到文字列

窗口结构（上下可拖动分隔）：
    顶栏      按钮 + 文件名标签 + 横轴/纵轴下拉框
    上半部分  QTableWidget  数据表格（最多前 MAX_ROWS 行）
    下半部分  pg.PlotWidget 单条曲线（横轴列按数值处理，不行就退回行号）

运行：python dash03.py
依赖：pip install pandas pyqtgraph PySide6
"""

import os

import data_utils
import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,     # 应用主体，负责事件循环
    QWidget,          # 窗口底座
    QVBoxLayout,      # 垂直布局（外层：顶栏 + 分隔器）
    QHBoxLayout,      # 水平布局（顶栏内部）
    QSplitter,        # 可拖动分隔容器（上下分栏）
    QTableWidget,     # 表格控件
    QTableWidgetItem, # 表格单元格
    QPushButton,      # 按钮
    QLabel,           # 文本标签
    QComboBox,        # 下拉框（本文件用来选横轴/纵轴列）
    QFileDialog,      # 系统"打开文件"对话框
)

# ------------------------------------------------------------------ 路径与全局状态
# BASE_DIR = 本文件所在目录的绝对路径。
# __file__ 是本文件路径；abspath 补成绝对路径；dirname 取所在目录。
# 这样拼出来的 demo_data.csv 路径与"当前工作目录"无关，PyCharm 里点运行也不会找不到。
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEMO_PATH = os.path.join(BASE_DIR, "demo_data.csv")

# 表格最多只填这么多行：CSV 动辄几万行，逐格 setItem 会卡死界面
MAX_ROWS = 500

# 当前载入的数据表；None 表示还没载入（draw_chart 会先判空）
df = None


# ------------------------------------------------------------------ 界面搭建
# 注意：界面控件先创建，下面的业务函数在后面才定义，
# 但函数体要等"点击/选择"发生时才执行，那时这些名字都已经存在了。
app = QApplication([])   # 每个 Qt 程序必须有且只有一个

win = QWidget()
win.setWindowTitle("数据看板")
win.resize(1000, 700)    # 宽 1000、高 700 像素

btn_open = QPushButton("打开文件")
label_file = QLabel("未载入")
label_file.setStyleSheet("color:#666;")   # 灰色：表示"还没加载数据"，不抢眼

# 两个下拉框：分别选横轴列和纵轴列。
# setMinimumWidth 只是给个最小宽度，免得列名短的时候框太小点不着
cmb_x = QComboBox()
cmb_y = QComboBox()
cmb_x.setMinimumWidth(120)
cmb_y.setMinimumWidth(120)

# 顶栏：按钮 | 文件名（拉伸因子 1，吃掉剩余宽度）| 横轴标签+下拉 | 纵轴标签+下拉
top = QHBoxLayout()
top.addWidget(btn_open)
top.addWidget(label_file, 1)
top.addWidget(QLabel("横轴："))
top.addWidget(cmb_x)
top.addWidget(QLabel("纵轴："))
top.addWidget(cmb_y)

# 表格控件（内容稍后由 fill_table 填）
table = QTableWidget()

# 图表：白底 + 网格 + 一条曲线。
# 曲线对象先建好并留着，后面 draw_chart 只调用 setData 换数据，不重建
pg.setConfigOptions(antialias=True)
plot = pg.PlotWidget(background="w")
plot.showGrid(x=True, y=True, alpha=0.3)
curve = plot.plot([], [], pen=pg.mkPen("#2f6fed", width=2))   # 蓝色、2 像素

# 上下可拖动分隔：表格 / 图表；setSizes 只是初始像素高度比例
splitter = QSplitter(Qt.Orientation.Vertical)
splitter.addWidget(table)
splitter.addWidget(plot)
splitter.setSizes([300, 400])

# 最外层垂直布局：顶栏一行 + 分隔器占满剩余空间
layout = QVBoxLayout()
layout.addLayout(top)        # 嵌套一个水平布局
layout.addWidget(splitter)
win.setLayout(layout)


# ------------------------------------------------------------------ 业务函数
def on_open():
    """点击【打开文件】：弹系统文件对话框，选中后交给 load_file()。"""
    # 返回 (路径, 所用过滤器)；过滤器限定只列 .csv。取消时 path 是空串
    path, _ = QFileDialog.getOpenFileName(win, "选择数据文件", "", "CSV 文件 (*.csv)")
    if path:
        load_file(path)


def load_file(path):
    """读入 CSV → 刷新文件名标签 → 刷新表格 → 重填下拉框 → 重画曲线。"""
    # 要重新赋值模块级的 df，必须先 global 声明，否则会变成局部变量
    global df
    try:
        df = data_utils.read_csv(path)
    except Exception as e:
        # 读失败就把原因写进标签，然后提前 return，避免拿 None 去填表格
        label_file.setText(f"读取失败：{e}")
        return
    # 只显示文件名，不显示完整路径（路径太长会把顶栏撑开）
    label_file.setText(os.path.basename(path))
    fill_table()    # 1) 表格
    fill_combos()   # 2) 下拉框（列名依赖新数据，必须在画图前做）
    draw_chart()    # 3) 曲线


def fill_table():
    """把 df 的前 MAX_ROWS 行逐格写进 QTableWidget。"""
    # 取"实际行数"和"上限"里小的那个
    rows = min(len(df), MAX_ROWS)
    table.setRowCount(rows)
    table.setColumnCount(len(df.columns))
    # 表头与单元格只收字符串，所以统一 str() 一次
    table.setHorizontalHeaderLabels(data_utils.column_names(df))
    # 双重循环逐格填：r 行号、c 列号；iloc 按"位置"取值，不依赖列名
    for r in range(rows):
        for c in range(len(df.columns)):
            table.setItem(r, c, QTableWidgetItem(str(df.iloc[r, c])))


def fill_combos():
    """用当前 df 的列名重填两个下拉框：横轴给全部列，纵轴只给数值列。"""
    names = data_utils.column_names(df)
    # is_numeric_dtype 判断这一列是不是数字类型（int/float），
    # 文字列拿去做纵轴画不出线，所以过滤掉
    numeric = data_utils.numeric_columns(df)

    # blockSignals(True)：临时屏蔽 currentIndexChanged 信号。
    # 因为下面 clear()/addItems() 会触发选中项变化，不屏蔽的话会连着重画好几次，
    # 而且中间那一刻下拉框还是空的（draw_chart 会拿到空列名）。
    # 改完再 blockSignals(False) 恢复。
    cmb_x.blockSignals(True)
    cmb_y.blockSignals(True)
    cmb_x.clear()
    cmb_y.clear()
    cmb_x.addItems(names)
    cmb_y.addItems(numeric if numeric else names)   # 没有数值列就退回全部列，至少不空
    cmb_x.blockSignals(False)
    cmb_y.blockSignals(False)


def draw_chart(index=None):
    """按当前两个下拉框的选择重画曲线。

    参数 index：Qt 的 currentIndexChanged(int) 会带一个"新选中项的下标"，
    槽函数必须能接住它，所以这里留了个可选参数（用不到，只是用来接收）。
    """
    # 还没载入数据时直接返回（启动阶段下拉框变化会走到这里）
    if df is None:
        return

    xcol = cmb_x.currentText()   # 当前选中的列名（不是下标）
    ycol = cmb_y.currentText()
    if not xcol or not ycol:
        return

    # to_numeric + errors="coerce"：能转数字的转，转不了的变 NaN，
    # 这样即使选了文字列也不会抛异常（代价是画出来是断的/空的）

    x,y = data_utils.to_xy(df, xcol, ycol)

    # 横轴策略：整列都能转成数字就用它本身当 x（如日期序号、成交量）；
    # 只要有一个转不了（比如"日期"这种字符串），就退化成 0,1,2… 的行号


    # 纵轴标题跟着列名走，用户一眼知道在看哪一列
    plot.setLabel("left", ycol)
    # setData 是"整体替换"，反复调用不会叠出多条线；to_list() 把 Series 转成 list
    curve.setData(x, y)


# ------------------------------------------------------------------ 信号连接
# 信号与槽：传的是函数名本身（不带括号），事件发生时才调用
btn_open.clicked.connect(on_open)
# 下拉框换选项就重画。两个框都连到同一个 draw_chart，
# 它自己会去读两个框的当前值，所以不用区分是谁触发的
cmb_x.currentIndexChanged.connect(draw_chart)
cmb_y.currentIndexChanged.connect(draw_chart)

# 启动时若同目录有示例数据就自动载入；没有就等用户点【打开文件】
if os.path.exists(DEMO_PATH):
    load_file(DEMO_PATH)

win.show()     # 显示窗口（不调用它窗口不会出现）
app.exec()     # 进入事件循环，窗口关闭后脚本结束