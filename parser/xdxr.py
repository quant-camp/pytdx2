import struct
from typing import override
from parser.baseparser import BaseParser, register_parser
import six

from help import to_datetime

@register_parser(u'0c 1f 18 76', u'00 01', u'0f 00')
class XDXR(BaseParser):
    def __init__(self, market, code):
        if type(code) is six.text_type:
            code = code.encode("utf-8")
        self.body = struct.pack(u'<HB6s', 1, market, code)

    @override
    def deserialize(self, data):
        (market, marketOR, code, count) = struct.unpack('<HB6sH', data[:11])

        xdxrs = []
        for i in range(count):
            pos = 11 + i * 29
            (market, code, unknown, date, category) = struct.unpack('<B6sBIB', data[pos: pos + 13])
            date = to_datetime(date)

            left_data = data[pos + 13: pos + 29]
            fenhong, peigujia, songzhuangu, peigu = None, None, None, None
            suogu = None
            xingquanjia, fenshu = None, None
            panqianliutong, qianzongguben, panhouliutong, houzongguben = None, None, None, None
            if category == 1:
                fenhong, peigujia, songzhuangu, peigu  = struct.unpack("<ffff", left_data)
            elif category in [11, 12]:
                _, _, suogu, _ = struct.unpack("<ffff", left_data)
            elif category in [13, 14]:
                xingquanjia, _, fenshu, _ = struct.unpack("<ffff", left_data)
            else:
                panqianliutong, qianzongguben, panhouliutong, houzongguben = struct.unpack("<ffff", left_data)

            xdxrs.append({
                'market': market,
                'code': code,
                'date': date,
                'category': category,
                'fenhong': fenhong,
                'peigujia': peigujia,
                'songzhuangu': songzhuangu,
                'peigu': peigu,
                'suogu': suogu,
                'xingquanjia': xingquanjia,
                'fenshu': fenshu,
                'panqianliutong': panqianliutong,
                'qianzongguben': qianzongguben,
                'panhouliutong': panhouliutong,
                'houzongguben': houzongguben,
            })
        return xdxrs