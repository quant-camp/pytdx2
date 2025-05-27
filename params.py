# coding=utf-8


from enum import Enum


class TDXParams:
    # ref : https://github.com/rainx/pytdx/issues/7
    # 分笔行情最多2000条
    MAX_TRANSACTION_COUNT = 2000
    # k先数据最多800条
    MAX_KLINE_COUNT = 800

class MARKET(Enum):
    # 0 - 深圳， 1 - 上海
    SZ = 0
    SH = 1

class KLINE_TYPE(Enum):
    # 0 -   5 分钟K 线
    # 1 -   15 分钟K 线
    # 2 -   30 分钟K 线
    # 3 -   1 小时K 线
    # 4 -   日K 线
    # 5 -   周K 线
    # 6 -   月K 线
    # 7 -   1 分钟
    # 8 -   1 分钟K 线
    # 9 -   日K 线
    # 10 -  季K 线
    # 11 -  年K 线
    FIVE_MIN = 0
    FIFTEEN_MIN = 1
    THIRTY_MIN = 2
    ONE_HOUR = 3
    DAILY = 4
    WEEKLY = 5
    MONTHLY = 6
    EXHQ_1_MIN = 7
    ONE_MIN = 8
    DAY_K = 9
    THREE_MONTH = 10
    YEARLY = 11

class BLOCK_FILE_TYPE(Enum):
    DEFAULT = 'block.dat'
    SZ = 'block_zs.dat'
    FG = 'block_fg.dat'
    GN = 'block_gn.dat'