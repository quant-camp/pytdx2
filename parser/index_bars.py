import struct
from typing import override
from parser.security import Bars
from help import get_price, to_datetime

class IndexBars(Bars):
    @override
    def deserialize(self, data):
        (count,) = struct.unpack('<H', data[:2])
        pos = 2

        pre_diff_base = 0
        bars = []
        for _ in range(count):
            (date,) = struct.unpack("<I", data[pos: pos + 4])
            pos += 4
            date = to_datetime(date, self.kline_type.value < 4 or self.kline_type.value == 7 or self.kline_type.value == 8)

            open, pos = get_price(data, pos)
            close, pos = get_price(data, pos)

            high, pos = get_price(data, pos)
            low, pos = get_price(data, pos)

            (vol, amount, upCount, downCount) = struct.unpack("<ffHH", data[pos: pos + 12])
            pos += 12

            open += pre_diff_base
            close += open
            high += open
            low += open

            pre_diff_base = close

            bars.append({
                'date': date,
                'open': open,
                'close': close,
                'high': high,
                'low': low,
                'vol': vol,
                'amount': amount,
                'upCount': upCount,
                'downCount': downCount,
            })

        return bars
