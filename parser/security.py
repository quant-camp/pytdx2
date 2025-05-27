import datetime
from log import log
from parser.baseparser import BaseParser, register_parser
import struct
from typing import OrderedDict, override
import six
from help import to_datetime, get_price, get_time


@register_parser(u'0c 10 08 64', u'01 01', u'2d 05')
class Bars(BaseParser):
    def __init__(self, market, code, kline_type, start, end):
        if type(code) is six.text_type:
            code = code.encode("utf-8")
        self.body = struct.pack(u'<H6sHHHH10s', market, code, kline_type, 1, start, end, b'')

        self.kline_type = kline_type

    @override
    def deserialize(self, data):
        (count,) = struct.unpack('<H', data[:2])
        pos = 2

        pre_diff_base = 0
        bars = []
        for _ in range(count):
            (date,) = struct.unpack("<I", data[pos: pos + 4])
            pos += 4
            datetime = to_datetime(date, self.kline_type < 4 or self.kline_type == 7 or self.kline_type == 8)

            open, pos = get_price(data, pos)
            close, pos = get_price(data, pos)

            high, pos = get_price(data, pos)
            low, pos = get_price(data, pos)

            (vol, amount) = struct.unpack("<ff", data[pos: pos + 8])
            pos += 8

            open += pre_diff_base
            close += open
            high += open
            low += open

            pre_diff_base = close

            bars.append({
                'datetime': datetime,
                'open': open,
                'close': close,
                'high': high,
                'low': low,
                'vol': vol,
                'amount': amount,
            })

        return bars

@register_parser(u'0c 0c 18 6c', u'00 01', u'4e 04')
class Count(BaseParser):
    def __init__(self, market):
        self.body = struct.pack(u'<HI', market, 0x133c775)

    @override
    def deserialize(self, data):
        return {
            'count': struct.unpack('<H', data[:2])[0]
        }

@register_parser(u'0c 01 18 64', u'01 01', u'50 04')
class List(BaseParser):
    def __init__(self, market, start):
        self.body = struct.pack(u'<HH', market, start)

    @override
    def deserialize(self, data):
        (count,) = struct.unpack('<H', data[:2])

        stocks = []
        for i in range(count):
            pos = 2 + i * 29
            (code, vol, name, unknow1, decimal_point,
             pre_close, unknow2) = struct.unpack("<6sH8s4sBf4s", data[pos: pos + 29])
            code = code.decode('utf-8')
            name = name.decode('gbk', errors='ignore').rstrip('\x00')

            stocks.append({
                'code': code,
                'vol': vol,
                'name': name,
                'pre_close': pre_close,
                'decimal_point': decimal_point,
                'unknow1': unknow1,
                'unknow2': unknow2,
            })

        return stocks

@register_parser(u'0c 1b 08 00', u'01 01', u'1d 05')
class Orders(BaseParser):
    def __init__(self, market, code):
        if type(code) is six.text_type:
            code = code.encode("utf-8")
        self.body = struct.pack(u'<H6sI', market, code, 0)

    @override
    def deserialize(self, data):
        (count,) = struct.unpack('<H', data[:2])
        pos = 2

        orders = []
        last_price = 0
        for _ in range(count):
            price, pos = get_price(data, pos)
            unknown, pos = get_price(data, pos)
            vol, pos = get_price(data, pos)

            last_price += price
            
            orders.append({
                'price': last_price,
                'vol': vol,
                'unknown': unknown,
            })

        return orders

@register_parser(u'0c 01 30 00', u'01 01', u'b4 0f')
class HistoryOrders(BaseParser):
    def __init__(self, market: int, code: str, date: datetime.date):
        if type(code) is six.text_type:
            code = code.encode("utf-8")
        date = date.year * 10000 + date.month * 100 + date.day
        self.body = struct.pack(u'<IB6s', date, market, code)

    @override
    def deserialize(self, data):
        (count,) = struct.unpack('<H', data[:2])
        pos = 2

        (unknown, ) = struct.unpack('<I', data[pos: pos + 4])
        pos += 4

        orders = []
        last_price = 0
        for _ in range(count):
            price, pos = get_price(data, pos)
            unknown, pos = get_price(data, pos)
            vol, pos = get_price(data, pos)

            last_price += price

            orders.append({
                'price': last_price,
                'vol': vol,
                'unknown': unknown,
            })

        return orders

@register_parser(u'0c 01 20 63', u'00 02', u'3e 05')
class Quotes(BaseParser):
    def __init__(self, stocks: list[int, str]):
        count = len(stocks)
        if count <= 0:
            raise Exception("stocks count must > 0")
        self.body = struct.pack('<H6sH', 5, b'', count)
        
        stock_buf = bytearray()
        for stock in stocks:
            (market, code) = stock
            if type(code) is six.text_type:
                code = code.encode("utf-8")
            stock_buf.extend(struct.pack('<B6s', market, code))
        self.body.extend(stock_buf)

    @override
    def deserialize(self, data):
        (_, count) = struct.unpack('<HH', data[:4])
        pos = 4

        def _format_time(time_stamp):
            if time_stamp == 0:
                return '00:00:00.000'
            else:
                time_stamp = str(time_stamp)
            """
            format time from reversed_bytes0
            by using method from https://github.com/rainx/pytdx/issues/187
            """
            time = time_stamp[:-6] + ':'
            if int(time_stamp[-6:-4]) < 60:
                time += '%s:' % time_stamp[-6:-4]
                time += '%06.3f' % (
                    int(time_stamp[-4:]) * 60 / 10000.0
                )
            else:
                time += '%02d:' % (
                    int(time_stamp[-6:]) * 60 / 1000000
                )
                time += '%06.3f' % (
                    (int(time_stamp[-6:]) * 60 % 1000000) * 60 / 1000000.0
                )
            return time

        quotes = []
        for _ in range(count):
            (market, code, active1) = struct.unpack('<B6sH', data[pos: pos + 9])
            pos += 9
            code = code.decode('utf-8')
            
            price, pos = get_price(data, pos)
            last_close, pos = get_price(data, pos)
            open, pos = get_price(data, pos)
            high, pos = get_price(data, pos)
            low, pos = get_price(data, pos)
            reversed_bytes0, pos = get_price(data, pos)
            reversed_bytes1, pos = get_price(data, pos)
            vol, pos = get_price(data, pos)
            cur_vol, pos = get_price(data, pos)
            
            last_close += price
            open += price
            high += price
            low += price
            server_time = _format_time(reversed_bytes0)

            (amount,) = struct.unpack('<f', data[pos: pos + 4])
            pos += 4

            s_vol, pos = get_price(data, pos)
            b_vol, pos = get_price(data, pos)
            s_amount, pos = get_price(data, pos) #reversed_bytes2
            b_amount, pos = get_price(data, pos) #reversed_bytes3

            bid1, pos = get_price(data, pos)
            ask1, pos = get_price(data, pos)
            bid_vol1, pos = get_price(data, pos)
            ask_vol1, pos = get_price(data, pos)

            bid2, pos = get_price(data, pos)
            ask2, pos = get_price(data, pos)
            bid_vol2, pos = get_price(data, pos)
            ask_vol2, pos = get_price(data, pos)

            bid3, pos = get_price(data, pos)
            ask3, pos = get_price(data, pos)
            bid_vol3, pos = get_price(data, pos)
            ask_vol3, pos = get_price(data, pos)

            bid4, pos = get_price(data, pos)
            ask4, pos = get_price(data, pos)
            bid_vol4, pos = get_price(data, pos)
            ask_vol4, pos = get_price(data, pos)

            bid5, pos = get_price(data, pos)
            ask5, pos = get_price(data, pos)
            bid_vol5, pos = get_price(data, pos)
            ask_vol5, pos = get_price(data, pos)

            bid1 += price
            ask1 += price
            bid2 += price
            ask2 += price
            bid3 += price
            ask3 += price
            bid4 += price
            ask4 += price
            bid5 += price
            ask5 += price

            (reversed_bytes4,) = struct.unpack('<H', data[pos: pos + 2])
            pos += 2

            reversed_bytes5, pos = get_price(data, pos)
            reversed_bytes6, pos = get_price(data, pos)
            reversed_bytes7, pos = get_price(data, pos)
            reversed_bytes8, pos = get_price(data, pos)

            (reversed_bytes9, active2) = struct.unpack("<hH", data[pos: pos + 4])
            pos += 4

            quotes.append({
                'market': market,
                'code': code,
                'active1': active1,
                'active2': active2,
                'price': price,
                'last_close': last_close,
                'open': open,
                'high': high,
                'low': low,
                'server_time': server_time,
                'reversed_bytes1': reversed_bytes1,
                'vol': vol,
                'cur_vol': cur_vol,
                'amount': amount,
                's_vol': s_vol,
                'b_vol': b_vol,
                's_amount': s_amount,
                'b_amount': b_amount,
                'handi_cap': {
                    'bid': [
                        {'price': bid1, 'vol': bid_vol1},
                        {'price': bid2, 'vol': bid_vol2},
                        {'price': bid3, 'vol': bid_vol3},
                        {'price': bid4, 'vol': bid_vol4},
                        {'price': bid5, 'vol': bid_vol5},
                    ],
                    'ask': [
                        {'price': ask1, 'vol': ask_vol1},
                        {'price': ask2, 'vol': ask_vol2},
                        {'price': ask3, 'vol': ask_vol3},
                        {'price': ask4, 'vol': ask_vol4},
                        {'price': ask5, 'vol': ask_vol5},
                    ]
                },
                'reversed_bytes4': reversed_bytes4,
                'reversed_bytes5': reversed_bytes5,
                'reversed_bytes6': reversed_bytes6,
                'reversed_bytes7': reversed_bytes7,
                'reversed_bytes8': reversed_bytes8,
                'reversed_bytes9': reversed_bytes9,
            })

        return quotes

@register_parser(u'0c 17 08 01', u'01 01', u'c5 0f')
class Transaction(BaseParser):
    def __init__(self, market, code, start, count):
        if type(code) is six.text_type:
            code = code.encode("utf-8")
        self.body = struct.pack(u'<H6sHH', market, code, start, count)

    @override
    def deserialize(self, data):
        (count,) = struct.unpack('<H', data[:2])
        pos = 2

        last_price = 0
        transactions = []
        for _ in range(count):
            hour, minute, pos = get_time(data, pos)

            price, pos = get_price(data, pos)
            vol, pos = get_price(data, pos)
            num, pos = get_price(data, pos)
            buyorsell, pos = get_price(data, pos)
            unknown, pos = get_price(data, pos)

            last_price += price
            transactions.append({
                "time": "%02d:%02d" % (hour, minute),
                'price': last_price,
                'vol': vol,
                'num': num,
                'buyorsell': buyorsell,
                'unknown': unknown,
            })

        return transactions

@register_parser(u'0c 01 30 01', u'00 01', u'b5 0f')
class HistoryTransaction(BaseParser):
    def __init__(self, market, code, date, start, count):
        if type(code) is six.text_type:
            code = code.encode("utf-8")
        date = date.year * 10000 + date.month * 100 + date.day
        self.body = struct.pack(u'<IH6sHH', date, market, code, start, count)

    @override
    def deserialize(self, data):
        (count,) = struct.unpack('<H', data[:2])
        pos = 2

        last_price = 0
        transactions = []
        for _ in range(count):
            hour, minute, pos = get_time(data, pos)

            price, pos = get_price(data, pos)
            vol, pos = get_price(data, pos)
            buyorsell, pos = get_price(data, pos)
            unknown, pos = get_price(data, pos)
            last_price += price
            transactions.append({
                "time": "%02d:%02d" % (hour, minute),
                'price': last_price,
                'vol': vol,
                'buyorsell': buyorsell,
                'unknown': unknown,
            })

        return transactions