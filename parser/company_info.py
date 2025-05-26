import struct
from typing import override
from parser.baseparser import BaseParser, register_parser
import six

@register_parser(u'0c 0f 10 9b', u'00 01', u'cf 02')
class Category(BaseParser):
    def __init__(self, market, code):
        if type(code) is six.text_type:
            code = code.encode("utf-8")
        self.body.extend(struct.pack(u"<H6sI", market, code, 0))

    @override
    def deserialize(self, data):
        (count,) = struct.unpack('<H', data[:2])

        def get_str(str):
            pos = str.find(b'\x00')
            if pos != -1:
                str = str[:pos]
            try:
                return str.decode('gbk')
            except:
                return 'unknown str'


        categories = []
        for i in range(count):
            category_buf = data[2 + i * 152:2 + (i + 1) * 152 - 1]

            (name, filename, start, length) = struct.unpack("<64s80sII", category_buf)
            categories.append({
                'name': get_str(name),
                'filename': get_str(filename),
                'start': start,
                'length': length,
            })

        return categories

@register_parser(u'0c 07 10 9c', u'00 01', u'd0 02')
class Content(BaseParser):
    def __init__(self, market, code, filename, start, length):
        if type(code) is six.text_type:
            code = code.encode("utf-8")

        if type(filename) is six.text_type:
            filename = filename.encode("utf-8")

        if len(filename) != 80:
            filename = filename.ljust(80, b'\x00')

        self.body.extend(struct.pack(u"<H6sH80sIII", market, code, 0, filename, start, length, 0))

    @override
    def deserialize(self, data):
        (market, code, marketOR, length) = struct.unpack(u"<H6sHH", data)

        return {
            'market': market,
            'code': code,
            'marketOR': marketOR,
            'length': length,
            'content': data[12:12+length].decode('gbk'),
        }
