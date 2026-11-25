# 数据看板（Windows 本地版）

一个双击就能用的本地数据查看器：打开 CSV → 看表格 → 看折线图 → 自己选横轴纵轴。
不联网、不要账号、数据只在自己电脑上。

---

## 文件说明

| 文件 | 是什么 | 能不能删 |
|---|---|---|
| `app.py` | **主程序（类版本）** —— 日常就用这个 | 不能 |
| `data_utils.py` | **数据层**：读 CSV、挑列、算坐标。不含任何界面代码 | 不能 |
| `dash03.py` | 脚本版主程序（重构前的版本，留着对照学习） | 可以 |
| `demo_data.csv` | 演示数据（44 行股票数据） | 可以，但要留一份测试用 |
| `速查表.md` | PySide6 / pandas 常用写法速查 | 留 |
| `学习地图.html` | 整套知识的结构图（浏览器打开） | 留 |
| `打包.bat` | 双击即重新打包 exe | 留 |
| `.gitignore` | 排除 .venv / dist / build 等不该进仓库的东西 | 不能 |
| `dist/` | 打包产物（exe 在这里，180MB） | 可以删（删了要重新打包） |
| `build/` / `*.spec` | 打包中间文件，可随时重建 | 可以删 |

> 学习过程中的历史文件（`main.py`、`dashboard.py`、`dashboard02.py`、`table_demo.py`、`data_test.py` 及各种 `.bak`）已在 2026-11-25 清理。

---

## 平时怎么运行

PyCharm 里打开 `app.py`，按 `Shift+F10`。

命令行方式：

```powershell
.venv\Scripts\python.exe app.py
```

---

## 怎么打包成 exe

**方式一：双击 `打包.bat`**（推荐，省事）

**方式二：Terminal 里执行**

```powershell
pyinstaller --noconfirm --windowed --name DataDashboard app.py
```

产物：`dist\DataDashboard\DataDashboard.exe`

**三条必须记住的规则：**

1. 发人时**整个 `dist\DataDashboard` 文件夹压缩发**，不能只发 exe
2. 改了代码必须**重新打包**，exe 里是旧代码的副本
3. 打包后闪退看不到报错时，**去掉 `--windowed` 再打一次**，会有黑框显示错误

---

## 常见改动，改哪里

| 我想…… | 改哪里 |
|---|---|
| 改窗口标题 | `setWindowTitle("...")` |
| 改表格最多显示多少行 | `MAX_ROWS = 500` |
| 改折线颜色 | `pg.mkPen("#2f6fed", width=2)` |
| 改窗口初始大小 | `resize(1000, 700)` |
| 改表格/图表的高度比例 | `splitter.setSizes([300, 400])` |
| 加一条参考线 / 第二根曲线 | `draw_chart` 里再加一条 `curve` |
| 读 Excel（.xlsx） | `data_utils.read_csv` 里加 `pd.read_excel` 分支 |
| 让横轴显示真实日期 | 用 `pg.DateAxisItem` + 时间戳（还没做） |

---

## 报错对照表

| 报错 | 意思 | 先查 |
|---|---|---|
| `NameError: name 'x' is not defined` | 名字不存在 | 拼写 / 大小写 / 定义在调用之后 |
| `AttributeError: module 'data_utils' has no attribute 'xxx'` | 函数名写错 | 去 `data_utils.py` 看 `def` 清单 |
| `AttributeError: 'list' object has no attribute 'to_list'` | 类型变了还按旧的用 | 谁返回的、返回什么类型 |
| `KeyError: '收盘'` | 数据里没这一列 | 别写死列名，用下拉框 |
| `FileNotFoundError` | 找不到文件 | `print(os.getcwd())` 看工作目录 |
| `TypeError: ... takes 0 positional arguments but 1 was given` | 信号带参数，函数没接 | 加 `(index=None)` 或 `*args` |
| `IndentationError` | 缩进不对 | 统一 4 空格 |

---

## 版本记录

- **v1（第 9 节）**：表格 + 图表，列名写死
- **v2（第 10 节）**：加「打开文件」按钮
- **v3（第 11 节）**：下拉框选列，能看任意 CSV
- **v4（第 12 节）**：拆出 `data_utils.py` 数据层
- **v5（第 13 节）**：`app.py` 类重构（`global` 消失）
- **v6（第 14 节）**：打包成 exe
- **v7（清理）**：删除历史文件、加 `.gitignore`、加 `打包.bat`
- **v8（进行中）**：上传到 GitHub

---

## 下一步想做的话

1. 真日期轴（横轴显示 2026-09-01，而不是 0~43）
2. 按条件筛选（只看最近 30 天）
3. 点表头排序
4. 导出当前图表为 PNG
5. 记住上次打开的文件