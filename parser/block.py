import struct
from typing import override
from parser.baseparser import BaseParser, register_parser
import six

@register_parser(u'0c 39 18 69', u'00 01', u'c5 02')
class Meta(BaseParser):
    def __init__(self, file_name):
        if type(file_name) is six.text_type:
            file_name = file_name.encode("utf-8")
        self.body.extend(struct.pack(u'<{}s'.format(0x2a - 2), file_name))

    @override
    def deserialize(self, data):
        (size, unknow1, hash_value, unknow2) = struct.unpack(u"<I1s32s1s", body_buf)
        return {
            "size": size,
            "hash_value" : hash_value,
            "unknow1" : unknow1,
            "unknow2" : unknow2
        }

@register_parser(u'0c 37 18 6a', u'00 01', u'b9 06')
class Info(BaseParser):
    def __init__(self, file_name, start, size):
        if type(file_name) is six.text_type:
            file_name = file_name.encode("utf-8")
        self.body.extend(struct.pack(u'<II{}s'.format(0x6e - 10), start, size, file_name))

    @override
    def deserialize(self, data):
        return {
            'size': struct.unpack('<I', data[:4])[0],
           'data': data[4:]
        }

@register_parser(u'0c 12 34 00', u'00 00', u'b9 06')
class Report(Info):
    pass