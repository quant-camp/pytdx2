# coding=utf-8

import datetime
import struct
import six

from log import log


#### XXX: 分析了一下，貌似是类似utf-8的编码方式保存有符号数字
def get_price(data, pos):
    pos_byte = 6
    bdata = indexbytes(data, pos)
    intdata = bdata & 0x3f
    if bdata & 0x40:
        sign = True
    else:
        sign = False

    if bdata & 0x80:
        while True:
            pos += 1
            bdata = indexbytes(data, pos)
            intdata += (bdata & 0x7f) << pos_byte
            pos_byte += 7

            if bdata & 0x80:
                pass
            else:
                break

    pos += 1

    if sign:
        intdata = -intdata

    return intdata, pos

def to_datetime(num, with_time=False):
    year = 0
    month = 0
    day = 0
    hour = 15
    minute = 0
    if with_time:
        zip_data = num & 0xFFFF
        year = (zip_data >> 11) + 2004
        month = int((zip_data & 0x7FF) / 100)
        day = (zip_data & 0x7FF) % 100

        tminutes = num >> 16
        hour = int(tminutes / 60)
        minute = tminutes % 60
    else:
        year = int(num / 10000)
        month = int((num % 10000) / 100)
        day = num % 100

    date = datetime.date(year, month, day)
    time = datetime.time(hour, minute)
    datetime_obj = datetime.datetime.combine(date, time)
    return datetime_obj

def get_time(buffer, pos):
    (tminutes, ) = struct.unpack("<H", buffer[pos: pos + 2])
    hour = int(tminutes / 60)
    minute = tminutes % 60
    pos += 2

    return hour, minute, pos

def indexbytes(data, pos):

    if six.PY2:
        if type(data) is bytearray:
            return data[pos]
        else:
            return six.indexbytes(data, pos)
    else:
        return data[pos]
