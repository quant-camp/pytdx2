import struct
from typing import override
from const import BLOCK_FILE_TYPE
from parser.baseparser import BaseParser, register_parser
import six

# iwshop/1_600009.htm
@register_parser(0x6b9)
class Report(BaseParser):
    def __init__(self, file_name: str, start: int = 0, size: int = 0x7530):
        if type(file_name) is six.text_type:
            file_name = file_name.encode("utf-8")
        self.body = struct.pack('<II100s', start, size, file_name)

    @override
    def deserialize(self, data):
        return {
            'size': struct.unpack('<I', data[:4])[0],
            'data': data[4:]
        }


# tdxfin/gpcw.txt
# >00 00000000 00 2a00 2a00 |c502 737065632f737065637a736576656e742e7478740000000000000000000000000000000000000000  spec/speczsevent.txt
# >00 00000000 00 2a00 2a00 |c502 737065632f737065637a73686f742e74787400000000000000000000000000000000000000000000  spec/speczshot.txt
# >00 00000000 00 2a00 2a00 |c502 7464787a73626173652e636667000000000000000000000000000000000000000000000000000000  tdxzsbase.cfg
# >00 00000000 00 2a00 2a00 |c502 7464787a7362617365322e6366670000000000000000000000000000000000000000000000000000  tdxzsbase2.cfg
# >00 00000000 00 2a00 2a00 |c502 7a68622e7a6970000000000000000000000000000000000000000000000000000000000000000000  zhb.zip
# >00 00000000 00 2a00 2a00 |c502 73706563616464696e666f2e74787400000000000000000000000000000000000000000000000000  specaddinfo.txt
# >00 00000000 00 2a00 2a00 |c502 737065632f73706563686b626c6f636b2e7478740000000000000000000000000000000000000000  spec/spechkblock.txt
# >00 00000000 00 2a00 2a00 |c502 62692f626967646174615f312e7a6970000000000000000000000000000000000000000000000000  bi/bigdata_1.zip
@register_parser(0x2c5)
class Meta(BaseParser):
    def __init__(self, block_file_type: BLOCK_FILE_TYPE):
        file_name = block_file_type.value.encode("utf-8") if type(block_file_type.value) is six.text_type else block_file_type.value
        self.body = struct.pack('<40s', file_name)

    @override
    def deserialize(self, data):
        (size, unknow1, hash_value, unknow2) = struct.unpack(u"<I1s32s1s", data)
        return {
            "size": size,
            "hash_value" : hash_value,
            "unknow1" : unknow1,
            "unknow2" : unknow2
        }

class Info(Report):
    def __init__(self, block_file_type: BLOCK_FILE_TYPE, start: int, size: int):
        super().__init__(block_file_type.value, start, size)