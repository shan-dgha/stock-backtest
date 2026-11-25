"""数据层：只跟表格数据打交道，不涉及任何界面。

这个文件里不应该出现 print、不应该出现 Qt。

约定：进来的参数一律是 pandas 的 DataFrame，出去的尽量是"普通 Python 值"
（list / str / float），这样界面层拿去就能直接用，不必再处理 Series。
"""

# 本文件目前没有用到 numpy（保留是为了以后做数值计算时直接可用，删掉也不影响运行）
import numpy as np
import pandas as pd


def read_csv(path):
    """读 CSV 返回 DataFrame。

    只包了一层 pd.read_csv：好处是把"读文件失败会抛什么异常"收在一个地方，
    以后要加编码探测（encoding="gbk" 之类）、跳过表头行等，都改这里就够。
    """
    return pd.read_csv(path)


def column_names(df):
    """所有列名，统一转成字符串列表（表头/下拉框都只吃字符串）。"""
    return [str(c) for c in df.columns]


def numeric_columns(df):
    """只挑出数字类型的列（int/float），给"纵轴"下拉框用。

    文字列拿去当纵轴画不出线，所以在数据层就过滤掉，界面层不用再判断。
    """
    return [str(c) for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]


def to_xy(df, x_col, y_col):
    """把两列取成画图用的 (x, y) 两个列表。

    y：to_numeric 转数字，转不了的变 NaN——宁可画出来是断的，也不要抛异常。
    x：整列都能转数字（如成交量、序号）就直接用列值；
       只要有一个转不了（如"日期"这种字符串），就退化成 0,1,2… 的行号，
       否则横轴会出现 NaN 点，曲线会乱。
    """
    y = pd.to_numeric(df[y_col], errors='coerce')
    x_num = pd.to_numeric(df[x_col], errors='coerce')
    if x_num.notna().all():     # notna 判断"不是 NaN"，all() 要求整列都满足
        x = x_num.to_list()
    else:
        x = list(range(len(df)))
    return x, y.tolist()