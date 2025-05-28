from datetime import datetime
import struct
from typing import override

from log import log
from parser.baseparser import BaseParser, register_parser

@register_parser(0xd)
class Setup(BaseParser):
    def __init__(self):
        self.body = struct.pack('<B', 1)

    @override
    def deserialize(self, data):
        (_, year, day, month, minute, hour, _, second, ss, date, a1, b1, date2, a2, b2, c, d, e, server_name, web_site, f, category) = struct.unpack('<BHBBBBBB33sIHHIHHHH5s22s64s6s30s', data)
        log.debug("ss is " + ss.hex())
        log.debug("e is " + e.hex())
        log.debug("f is " + f.hex())
        log.debug("a1 b1 a2 b2 c d is \n" + str(a1) + " " + str(b1) + " " + str(a2) + " " + str(b2) + " " + str(c) + " " + str(d))
        
        info = {
            "date_time": datetime(year, month, day, hour, minute, second).strftime('%Y-%m-%d %H:%M:%S'),
            "server_name": server_name.decode('gbk').replace('\x00', ''),
            "web_site": web_site.decode('gbk').replace('\x00', ''),
            "category": category.decode('gbk').replace('\x00', ''),
        }
        log.debug("info is \n" + str(info))
        return info

@register_parser(0xfdb)
class Notice(BaseParser):
    def __init__(self):
        self.body = bytearray.fromhex(u'd5 d0 c9 cc d6 a4 a8 af 00 00 00 8f c2 25 40'
                                      u'13 00 00 d5 00 c9 cc bd f0 d7 ea 00 00 00 02')
                                      
    @override
    def deserialize(self, data):
        (unknow, link) = struct.unpack('<58s120s', data[:178])
        link = link.decode('gbk').replace('\x00', '')
        msg = data[178:].decode('gbk').replace('\x00', '')
        log.debug("unknow : " + unknow.hex())
        log.debug("link : " + link)
        log.debug("msg : \n" + msg)
        return {
            "link": link,
            "msg": msg
        }