import struct

class BaseParser:
    
    msg_id = 0
    body = bytearray()
    
    def __init__(self):
        super().__init__()

    def serialize(self):
        body = struct.pack('<H', self.msg_id) + self.body
        header = struct.pack('<BIBHH', 0xc, 0, 1, len(body), len(body))
        return header + body

    def deserialize(self, data):
        return data

def register_parser(msg_id: int = 0):
    def decorator(cls):
        class Decorator(cls):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.msg_id = msg_id
        return Decorator
    return decorator