import struct
from typing import override
from params import BLOCK_FILE_TYPE
from parser.baseparser import BaseParser, register_parser
import six

@register_parser(0x6b9)
class Report(BaseParser):
    def __init__(self, file_name: str, start: int = 0, size: int = 0x7530):
        if type(file_name) is six.text_type:
            file_name = file_name.encode("utf-8")
        self.body = struct.pack(u'<II{}s'.format(0x6e - 10), start, size, file_name)

    @override
    def deserialize(self, data):
        return {
            'size': struct.unpack('<I', data[:4])[0],
            'data': data[4:]
        }

@register_parser(0x2c5)
class Meta(BaseParser):
    def __init__(self, block_file_type: BLOCK_FILE_TYPE):
        file_name = block_file_type.value.encode("utf-8") if type(block_file_type.value) is six.text_type else block_file_type.value
        self.body = struct.pack(u'<{}s'.format(0x2a - 2), file_name)

    @override
    def deserialize(self, data):
        (size, unknow1, hash_value, unknow2) = struct.unpack(u"<I1s32s1s", data)
        return {
            "size": size,
            "hash_value" : hash_value,
            "unknow1" : unknow1,
            "unknow2" : unknow2
        }

@register_parser(0x6b9)
class Info(Report):
    def __init__(self, block_file_type: BLOCK_FILE_TYPE, start: int, size: int):
        super().__init__(block_file_type.value, start, size)