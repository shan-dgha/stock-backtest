# Python / PySide6 学习速查（中文）

> 用途：替代 PyCharm 那个英文弹窗（Quick Documentation / Ctrl+Q）。
> 你截图里那个弹窗讲的是 **import 语句**，下面第 1 节就是它的中文版。

---

## 1. 弹窗在说什么：`import` 语句

**通用写法**

```text
import 模块 [as 别名]            # 可以逗号分隔写多个
from 模块 import 名字 [as 别名]   # 可以括号换行、逗号分隔
from 模块 import *
```

**基本 import（不带 from）分两步执行：**

1. **找到模块**，必要时加载并初始化它（就是把这个模块的代码跑一遍）；
2. **在当前命名空间绑定名字** —— 和赋值语句一样。带 `as` 就绑 `as` 后面的名字；不带 `as` 且是顶层模块，就用模块名；如果不是顶层模块（`import foo.bar.baz`），绑定的是最顶层的包 `foo`。

语句里用逗号写多个时，**每个子句各走一遍这两步**，等同于拆成几条独立的 import。

第一步失败有两种可能：模块根本找不到（`ModuleNotFoundError`），**或者** 模块找到了但在加载/初始化（执行模块代码）时出错。所以看到 import 报错先分清是哪一类。

**from 形式稍微复杂一些：**

1. 找到 from 后面的模块，必要时加载初始化；
2. 对 import 后面列的每个名字：先看模块里有没有这个属性 → 没有就尝试导入同名子模块再查一次 → 还没有就抛 `ImportError`；
3. 找到了就把引用放进当前命名空间，有 `as` 用 `as` 的名字。

**几条容易踩的规则**

- `import foo.bar.baz`：`foo`、`foo.bar`、`foo.bar.baz` 都被导入，但**只绑定了 `foo`**，想用 baz 得写全 `foo.bar.baz.xxx`。
- `from foo.bar import baz`：绑定的是 `baz` 这个名字（指向 `foo.bar.baz`）。
- `from 模块 import *`：**只允许在模块顶层**；写在函数或类里会直接 `SyntaxError`。它导入的是该模块的公有名字（有 `__all__` 就按 `__all__`，没有就取所有不以 `_` 开头的名字）。
- **相对导入的点号**：`.` 表示当前包，`..` 表示上一级包，`...` 再上一级。所以包里的模块写 `from . import mod`，等价于导入 `包.mod`。
- `import __future__` 只是普通 import；`from __future__ import ...` 才是"future 语句"，且必须放在文件最前面。

中文原文（官方，可以对照看）：
<https://docs.python.org/zh-cn/3/reference/simple_stmts.html#the-import-statement>

---

## 2. 你四个文件里出现的语法，中文对照

| 写法 | 中文说明 | 出现在 |
|---|---|---|
| `import sys` | 导入标准库 sys（命令行参数、解释器信息）。这里没用到，属于习惯性导入 | main / table_demo / dashboard |
| `import pandas as pd` | 导入 pandas 并起别名 `pd`，之后写 `pd.xxx` 即可 | data_test / table_demo / dashboard |
| `import pyqtgraph as pg` | 导入绘图库，别名 `pg` | dashboard |
| `from PySide6.QtWidgets import (…)` | 从 Qt 控件模块里取出指定类；括号+换行只是为了排版好看 | 全部 GUI 文件 |
| `from PySide6.QtCore import Qt` | 取 Qt 常量类，用来写 `Qt.Orientation.Vertical` | dashboard |
| `count = 0` | 模块级变量（全局变量） | main |
| `global count` | 在函数里声明"我要改的是外面那个 count"，不加就会新建局部变量并报 `UnboundLocalError` | main |
| `def on_click():` | 定义函数；这里作为"槽函数"（事件处理函数） | main |
| `f"你点了 {count} 次"` | f-string 格式化，`{}` 里直接写变量或表达式 | main |
| `button.clicked.connect(on_click)` | 信号与槽：把按钮点击信号连到函数。**传函数名不带括号**，带括号会立即执行 | main |
| `QApplication([])` | 创建应用对象，参数是命令行参数列表；一个程序只要一个 | 全部 GUI 文件 |
| `QWidget()` / `resize()` / `setWindowTitle()` | 窗口底座 / 设宽高 / 设标题 | 全部 GUI 文件 |
| `QHBoxLayout` / `QVBoxLayout` | 水平排列 / 垂直排列的布局；控件位置大小自动算 | main / table_demo |
| `QSplitter(Qt.Orientation.Vertical)` | 可拖动的分隔容器，这里上下分栏 | dashboard |
| `setLayout(layout)` | 把布局挂到窗口上 | 全部 GUI 文件 |
| `win.show()` | 显示窗口，不调用就不会出现 | 全部 GUI 文件 |
| `app.exec()` | 进入事件循环，等窗口关闭才继续往下走 | main / dashboard |
| `app.exec_()` | 同一个方法的旧写法，等价；已标记为将来会移除，建议改 `exec()` | table_demo |
| `pd.read_csv("demo_data.csv")` | 读 CSV 成 DataFrame；相对路径，要在 CSV 所在目录运行 | data_test / table_demo / dashboard |
| `df.shape` / `df.columns` | (行数, 列数) / 列名索引 | data_test |
| `df.head(3)` | 看前 3 行，默认 5 行 | data_test |
| `df["收盘"]` | 取一列，得到 Series；`.mean()` 求平均 | data_test |
| `df.iloc[r,c]` | 按**位置**取第 r 行第 c 列（`loc` 是按标签取） | table_demo / dashboard |
| `str(…)` | 转成字符串；表格单元格只接受字符串，pandas 数值不转会报类型错 | table_demo / dashboard |
| `QTableWidget()` | 表格控件；行列数要自己设 | table_demo / dashboard |
| `setHorizontalHeaderLabels([...])` | 设置表头文字，列表长度要等于列数 | table_demo / dashboard |
| `setItem(r, c, QTableWidgetItem(text))` | 往第 r 行第 c 列塞一个单元格 | table_demo / dashboard |
| `pg.setConfigOptions(antialias=True)` | 全局绘图配置，抗锯齿让曲线平滑 | dashboard |
| `pg.PlotWidget(background="white")` | 可当普通控件放进布局的绘图区；默认深色底 | dashboard |
| `plot.showGrid(x=True, y=True, alpha=0.3)` | 显示网格，`alpha` 是透明度 0~1 | dashboard |
| `plot.addLegend()` | 开启图例；**不开的话 plot 里的 `name` 不会显示出来** | dashboard |
| `pg.mkPen("#2f6fed", width=2)` | 造一支画笔：颜色 + 线宽 | dashboard |
| `value.to_list()` | pandas 列转成普通 Python 列表，绘图库更容易吃 | dashboard |
| `.setSizes([300, 400])` | 分隔条内两块区域的初始像素比例，之后用户可拖动调整 | dashboard |

---

## 3. 常用中文文档地址

| 内容 | 地址 |
|---|---|
| Python 中文文档总入口 | <https://docs.python.org/zh-cn/3/> |
| Python 语言参考（语法条目） | <https://docs.python.org/zh-cn/3/reference/> |
| 标准库中文（含 sys 等） | <https://docs.python.org/zh-cn/3/library/> |
| pandas 官方文档 | <https://pandas.pydata.org/docs/>（英文，中文社区版 pypandas.cn 有部分翻译但版本较旧） |
| PySide6 / Qt for Python | <https://doc.qt.io/qtforpython-6/>（英文，无官方中文；查控件名 + 示例够用） |
| pyqtgraph | <https://pyqtgraph.readthedocs.io/>（英文） |

---

## 4. 想让 PyCharm 里也尽量中文，能做的和不能做的

**不能：** 那个悬停/Ctrl+Q 弹窗的**正文**是 PyCharm 内置的英文文档，装中文界面包也不会翻译它。

**能做的：**

1. **界面中文**：`Settings → Plugins → Marketplace` 搜 `Chinese (Simplified) Language Pack`（JetBrains 官方插件），装完重启，菜单/设置/报错文案会变中文（代码提示和文档正文仍是英文）。
2. **让 Shift+F1 打开中文网页**：`Settings → Tools → Python External Documentation`，把 Python 那一行的 URL 改成 `https://docs.python.org/zh-cn/3/`，之后对某个函数按 Shift+F1 会直接跳中文页，而不是看弹窗。
3. **最省事的办法**：代码注释写成中文（现在四个文件已经都是），概念不懂就查本文件第 2 节的表，或问 AI —— 比啃英文原文快得多。