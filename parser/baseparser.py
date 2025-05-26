import struct

from log import log

class BaseParser:
    header = bytearray()
    version = bytearray()
    body_header = bytearray()
    body = bytearray()
    
    def __init__(self):
        super().__init__()

    def serialize(self):
        body = self.body_header + self.body
        body_len = struct.pack('<HH', len(body), len(body))

        return self.header + self.version + body_len + body

    def deserialize(self, data):
        return data

def register_parser(header: str = u'', version: str=u'', body_header: str=u''):
    def decorator(cls):
        class Decorator(cls):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.header = bytearray.fromhex(header) if header else bytearray()
                self.version = bytearray.fromhex(version) if version else bytearray()
                self.body_header = bytearray.fromhex(body_header) if body_header else bytearray()
        return Decorator
    return decorator