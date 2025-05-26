import struct

from parser.baseparser import BaseParser, register_parser

@register_parser(u'0c 02 18 93', u'00 01', u'0d 00')
class Setup(BaseParser):
    def __init__(self):
        self.body = struct.pack('<B', 1)

@register_parser(u'0c 02 18 94', u'00 01', u'0d 00')
class Setup2(BaseParser):
    def __init__(self):
        self.body = struct.pack('<B', 2)

@register_parser(u'0c 03 18 99', u'00 01', u'db 0f')
class Setup3(BaseParser):
    def __init__(self):
        self.body = bytearray.fromhex(u'd5 d0 c9 cc d6 a4 a8 af 00 00 00 8f c2 25 40'
                                      u'13 00 00 d5 00 c9 cc bd f0 d7 ea 00 00 00 02')