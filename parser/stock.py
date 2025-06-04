from datetime import date
from log import log
from const import CATEGORY, KLINE_TYPE, MARKET
from parser.baseparser import BaseParser, register_parser
import struct
from typing import override
import six
from help import to_datetime, get_price, get_time

@register_parser(0x52d)
class Bars(BaseParser):
    def __init__(self, market: MARKET, code: str, kline_type: KLINE_TYPE, start: int, count: int):
        if type(code) is six.text_type:
            code = code.encode("utf-8")
        self.body = struct.pack(u'<H6sHHHH10s', market.value, code, kline_type.value, 1, start, count, b'')

        self.kline_type = kline_type

    @override
    def deserialize(self, data):
        (count,) = struct.unpack('<H', data[:2])
        pos = 2

        minute_category = self.kline_type.value < 4 or self.kline_type.value == 7 or self.kline_type.value == 8

        pre_diff_base = 0
        bars = []
        for i in range(count):
            (date,) = struct.unpack("<I", data[pos: pos + 4])
            pos += 4
            datetime = to_datetime(date, minute_category)

            open, pos = get_price(data, pos)
            close, pos = get_price(data, pos)

            high, pos = get_price(data, pos)
            low, pos = get_price(data, pos)

            (vol, amount) = struct.unpack("<ff", data[pos: pos + 8])
            pos += 8

            upCount = 0
            downCount = 0
            if i < count - 1:
                try:
                    try_date = to_datetime(struct.unpack("<I", data[pos: pos + 4])[0], minute_category)
                    if len(bars) > 0 and try_date.year < bars[-1]['datetime'].year:
                        raise ValueError()
                except ValueError:
                    (upCount, downCount) = struct.unpack("<HH", data[pos: pos + 4])
                    pos += 4

            open += pre_diff_base
            close += open
            high += open
            low += open

            pre_diff_base = close

            bar = {
                'datetime': datetime,
                'open': open,
                'close': close,
                'high': high,
                'low': low,
                'vol': vol,
                'amount': amount,
            }
            if upCount != 0 or downCount != 0:
                bar['upCount'] = upCount
                bar['downCount'] = downCount
            bars.append(bar)

        return bars

# >0c 0a186b00 01 0800 0800 |4e04 0000 e9ff3401
# <b1cb7400 0c 0a186b00 00 4e04 0200 0200 |8250
@register_parser(0x44e)
class Count(BaseParser):
    def __init__(self, market: MARKET):
        today = date.today().year * 10000 + date.today().month * 100 + date.today().day
        self.body = struct.pack(u'<HI', market.value, today)

    @override
    def deserialize(self, data):
        return {
            'count': struct.unpack('<H', data[:2])[0]
        }
# >0c 0b186e00 01 1000 1000 |4d04 0000 0000 0000 4006 0000 0000 0000
# <b1cb7400 1c 0b186e00 00 4d04 e874 42e7 |789c647d797c93c5f67e7c59050451644702280a486dd2a649902549d3a6206e80a2885e15dc154551af3ba870d9f7455904da025d285dd3b449d326699b6e49936e69293b65130a140a140ac5df9c99f79d997c7ffddc3fbcfa7c662667cef29c3367e6d5750dd3aa424315f36581b6b4b371cedc3299f87761765793203b996b84ff83414a11e462a04931178d824c36d44041e1f3655959d5e6b4b332fa97f763bf2841b6f8201b49454632ce9005fd09d23f6050843452302c08a4400bb79c4eafb3ddb1b748ff7ecc078bd074b2c55328082d3cce13e78b73c7b54aa0ebcf3f090b5f1f49416108541c57cb83f68f5d030bbfc64068e133a2a6ce9a19bc6e58539a5e0285a1e9ea0e95a6da1a72ad12203969ec24047a9881c208c817b0dd0c1e69fda7d1148484a937fcdfc900b438890a331c8920b7cc9d5e9a1088970033bedb131d2427ad76beacfea83cb34c6eb749ffdebe7438dae03daa2802d2622d28bb1288cf2c0be448a03577ba4f13aa263e1e4d414a000184ed4a730b02e525bec240e8d76596598ec5b9d848fe877a1885052fffcba60b27d3294243e9509123ee9b84cc7a170381aaf8fd7b11884e57d3bbdc24b4f77733105515365d42ea98a9c2aa0d778d14a426d385712375dfb12146e8b6f30f3692864cc783aaabfe8c113e9db5878da425232939d0174f3e1123343ff2091d49114a406a0ef466cb635385f3f2630ca4a022a0a813f6b7a70a4b7bed642025f975fc9a52bf7e3e4618a49bc440613052b93f3fb96aaf04baf06a538cd0e39f350c240a332bcbef9240afee2c8b11929503192882ac8907ddfeea4793d010fa3b032161ce7c218ac7c8121a134d82a1651e0369c8c27954d1da3093706a1393b8424b40bc308f9de81f23cc5dfb1e05294309c8bfb7d8238146bcfc548c306aaa996e4b180279f20adc79796174a8b11b7f8e16b69d51d091547824bfabbaa3e49c04faf984ca241cda3b888222e8481174a43e87a79a04e5ec9114a4d1809cb2b278cdecdb7587499893f11f0984fedb7c991f19417907c5c8168eed344dd00e7a249a8214645bea8f30f54d7febfba942ca25250329251daf3f42250e3a7eb236944d87b4c011c8b1f1138e9405a60a474f343190b8c1fc74d8cc5f1871c74841a2b5c43919089b79fe74818da41141ffd7cce372b74a2329c3d0af2b4e7406f8352d98971e2d4c306d6120f4eb32ca0a5a79d0a2a13ba28591979f88a220f4eb02eeda661ea4fd3165aa501e18ce40c8ab541c329fe7412b8f7f661284cdafb1e99021d81302f77990c6d21a2d74dc7d9f81909c8adb9d4d3cc879b3d6241c9725301092536d45f9191ee45ddf142dbcd1b69e81909c32bcd57779d0dc570e18858f1fdec340c810a6ce0a5695ebef1863849c956729281ce993bda5b491875dd020cd14ba26331092b8b921a39d0725ad18661216bdc3d6140e7edc53798d07dd6effc824acb5b1bd0b47122f7057f979d0bc1a4bb410d5752f032189e726e766f0a0c8233d4c42d4dc9e0c84445059644be54113520e440b53efcf6220885247dc415a70e0ad24a3b0f06c6fbac12a3492cb53966cf67af224d03f8ba24d82fa743403895e85077d77096d4b746a14058199fb4aedb741a7245049bfd5266146ff2719484146e241674f94460bdf1de04642c22cefa80fe4a7e4154aa0f7fffcda244cffa391feba883032120025d0e80fd1dedd3f78818144fe547a39efbe043ad5f53d93103a611f03a9442796e8374ba08c458dd1c2d7473e63a008022a3a5a9b25816aeeec8d162e1575630bc7720a943b0b64f4efea52a42a9f7db49882d43850fb5d88642548a03f56bf6312ba6cff9881f09aaaedd5896ca4ad66c124cc5f389881f09ac0b132d0a26d47a285b3033730909ae8937d6f01fd751f4d78dc247c9f2e6720a40599f1f614defbf66bb3213f5e6da52250a35f57eb86e9541435b5c7121480c226d2913410a8db2baf32884c5678ed7cb4e048bf4d47d280
# >0c 0c186e00 01 1000 1000 |4d04 0000 4006 0000 4006 0000 0000 0000
# >0c 14186e00 01 1000 1000 |4d04 0000 4038 0000 4006 0000 0000 0000
@register_parser(0x44d)
class List(BaseParser):
    def __init__(self, market: MARKET, start: int = 0, count: int = 1600):
        self.body = struct.pack(u'<HIII', market.value, start, count, 0)

    @override
    def deserialize(self, data):
        (count,) = struct.unpack('<H', data[:2])
        
        stocks = []
        for i in range(count):
            pos = 2 + i * 37
            (code, vol, name, _, unknown1, decimal_point, pre_close, unknown2, unknown3) = struct.unpack("<6sH8s8s4sBfHH", data[pos: pos + 37])
            code = code.decode('gbk', errors='ignore').rstrip('\x00')
            name = name.decode('gbk', errors='ignore').rstrip('\x00')

            # print(data[pos: pos + 37].hex())
            stocks.append({
                'code': code,
                'vol': vol,
                'name': name,
                'decimal_point': decimal_point,
                'pre_close': pre_close,
                'unknown1': [unknown1.hex(), unknown2, unknown3],
            })

        return stocks

@register_parser(0x450)
class ListB(BaseParser):
    def __init__(self, market: MARKET, start):
        self.body = struct.pack(u'<HH', market.value, start)

    @override
    def deserialize(self, data):
        (count,) = struct.unpack('<H', data[:2])

        stocks = []
        for i in range(count):
            pos = 2 + i * 29
            (code, vol, name, unknown1, decimal_point, pre_close, unknown2, unknown3) = struct.unpack("<6sH8s4sBfHH", data[pos: pos + 29])
            code = code.decode('gbk', errors='ignore').rstrip('\x00')
            name = name.decode('gbk', errors='ignore').rstrip('\x00')
            
            stocks.append({
                'code': code,
                'vol': vol,
                'name': name,
                'decimal_point': decimal_point,
                'pre_close': pre_close,
                'unknown1': [unknown1.hex(), unknown2, unknown3],
            })

        return stocks

@register_parser(0x51d) # TODO: 不对
class Orders(BaseParser):
    def __init__(self, market: MARKET, code: str):
        if type(code) is six.text_type:
            code = code.encode("gbk")
        self.body = struct.pack(u'<H6sI', market.value, code, 0)

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

@register_parser(0xfb4)
class HistoryOrders(BaseParser):
    def __init__(self, market: MARKET, code: str, date: date):
        if type(code) is six.text_type:
            code = code.encode("utf-8")
        date = date.year * 10000 + date.month * 100 + date.day
        self.body = struct.pack(u'<IB6s', date, market.value, code)

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

@register_parser(0xfc5)
class Transaction(BaseParser):
    def __init__(self, market: MARKET, code: str, start: int, count: int):
        if type(code) is six.text_type:
            code = code.encode("utf-8")
        self.body = struct.pack(u'<H6sHH', market.value, code, start, count)

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
            trans, pos = get_price(data, pos)
            buyorsell, pos = get_price(data, pos)
            unknown, pos = get_price(data, pos)

            last_price += price
            transactions.append({
                "time": "%02d:%02d" % (hour, minute),
                'price': last_price,
                'vol': vol,
                'trans': trans,
                'action': 'SELL' if buyorsell == 1 else 'BUY',
                'unknown': unknown,
            })

        return transactions

@register_parser(0xfb5)
class HistoryTransaction(BaseParser):
    def __init__(self, market: MARKET, code: str, date: date, start: int, count: int):
        if type(code) is six.text_type:
            code = code.encode("utf-8")
        date = date.year * 10000 + date.month * 100 + date.day
        self.body = struct.pack(u'<IH6sHH', date, market.value, code, start, count)

    @override
    def deserialize(self, data):
        (count, _) = struct.unpack('<H4s', data[:6])
        pos = 6

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
                'action': 'SELL' if buyorsell == 1 else 'BUY',
                'unknown': unknown,
            })

        return transactions


#>0c 92034103 00 2700 2700 |d10f 0100 363033383933 0000000000000000000000000000000001001400000000010000000000
#<b1cb7400 1c 92034103 00 d10f d800 1e01 |789c5d8e3f08417110c77f0629cbddd35b2c0c269b7a25d45b7c079252e697d1a8accc66b39794b229b34529492959d44b49bd9449b25894f2f36e50aeaefbf7bdcf5d486533562e6fa93f0ba97944325b39fd186c65de0dd47306d24386b367cc4a12e70d03ee91511e33a29eae47e296c5305b0c77c0e81e08fe8bb07a4a544b8277a1a06f6f49efcbecabf70bda3b9a916028c5b02b8ce65534659f307910661bd23708c9b5b07a5361997742fa44fa0f3d3ffff44e8dd12f32bc142319165e7b4141de7e0b2760ea9b6e9c713318bb2ae3039a01596a
# 0000 303030303031 00000000000000000000000000000000 0100 bc07 000000000000
# 3d00 c3f53841 3d00 d7a3384148e13a415c8f3a4148e13a41295c3b410ad73b41ec513c4100003c411f853b4133333b4114ae3b410ad73b410ad73b410ad73b41ec513c41ec513c41cdcc3c41b81e3d41b81e3d41b81e3d41b81e3d41ae473d418fc23d41713d3e4166663e417b143e419a993d41a4703d4185eb3d4185eb3d419a993d41cdcc3c41cdcc3c41d7a33c41c3f53c41c3f53c41ae473d41b81e3d41ae473d41b81e3d41b81e3d41b81e3d41ae473d41c3f53c41b81e3d41b81e3d41b81e3d41cdcc3c41c3f53c41b81e3d41c3f53c41ae473d41b81e3d41ae473d41b81e3d41c3f53c41b81e3d41b81e3d41c3f53c41c3f53c41c3f53c41
@register_parser(0xfd1)
class ChartSampling(BaseParser):
    def __init__(self, market: MARKET, code: str):
        if type(code) is six.text_type:
            code = code.encode("gbk")
        self.body = bytearray(struct.pack('<H6s', market.value, code))
        
        self.body.extend(bytearray().fromhex('0000000000000000000000000000000001001400000000010000000000'))
    @override
    def deserialize(self, data):
        market, code = struct.unpack('<H6s', data[:8])
        num, price, _ = struct.unpack('<HfH', data[34:42])

        print(num)
        prices = []
        for i in range(num):
            p, = struct.unpack('<f', data[42 + i * 4: 42 + (i + 1) * 4])
            prices.append(p)
            
        return {
            'market': market,
            'code': code.decode('gbk'),
            'price': price,
            'prices': prices
        }

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

@register_parser(0x53e)
class QuotesDetail(BaseParser):
    def __init__(self, stocks: list[MARKET, str]):
        count = len(stocks)
        if count <= 0:
            raise Exception("stocks count must > 0")
        self.body = bytearray(struct.pack('<H6sH', 5, b'', count))
        
        for stock in stocks:
            (market, code) = stock
            if type(code) is six.text_type:
                code = code.encode("utf-8")
            self.body.extend(struct.pack('<B6s', market.value, code))

    @override
    def deserialize(self, data):
        (_, count) = struct.unpack('<HH', data[:4])
        pos = 4

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
            server_time, pos = get_price(data, pos)
            after_hour, pos = get_price(data, pos)
            vol, pos = get_price(data, pos)
            cur_vol, pos = get_price(data, pos)
            
            last_close += price
            open += price
            high += price
            low += price
            server_time = _format_time(server_time)

            (amount,) = struct.unpack('<f', data[pos: pos + 4])
            pos += 4

            s_vol, pos = get_price(data, pos)
            b_vol, pos = get_price(data, pos)
            s_amount, pos = get_price(data, pos) #reversed_bytes2
            b_amount, pos = get_price(data, pos) #reversed_bytes3

            handi_cap = {
                'bid': [],
                'ask': [],
            }
            for _ in range(5): # 5个
                bid, pos = get_price(data, pos)
                ask, pos = get_price(data, pos)
                bid_vol, pos = get_price(data, pos)
                ask_vol, pos = get_price(data, pos)

                bid += price
                ask += price

                handi_cap['bid'].append({
                    'price': bid,
                    'vol': bid_vol,
                })
                handi_cap['ask'].append({
                    'price': ask,
                    'vol': ask_vol,
                })

            (v1, unknown, v2, active2) = struct.unpack('<H4shH', data[pos: pos + 10])
            pos += 10

            quotes.append({
                'market': MARKET(market),
                'code': code,
                'price': price,
                'open': open,
                'high': high,
                'low': low,
                'last_close': last_close,
                'server_time': server_time,
                'after_hour': after_hour,
                'vol': vol,
                'cur_vol': cur_vol,
                'amount': amount,
                's_vol': s_vol,
                'b_vol': b_vol,
                's_amount': s_amount,
                'b_amount': b_amount,
                # 'handi_cap': handi_cap,
                'v1': v1,
                'unknown': unknown.hex(),
                'v2': v2,
                'active1': active1,
                'active2': active2,
            })

        return quotes

# >0c 6f022a00 01 3000 3000 |4705 0400 
# 00 333939303032 f3490200 
# 00 333939303033 f3490200 
# 01 393939393938 544a0200 
# 01 393939393937 544a0200
# <b1cb7400 0c 6f022a00 00 4705 0200 0200 |9393

# >0c 7a002900 01 0f00 0f00 |4705 0100 
# 01 363030303039 00000000

# <b1cb7400 0c 7a002900 00 4705 6e00 6e00 |929392a5a3a3a3a3aac39837a1829a899360da91939316639625d884aa86de060090234f91d92a119d9391149294d290259281d197bb8ed0998996d79f1792a9459482a79393f5cca8db77a177a1939377a177a1939377a177a1939377a177a1939377a177a1939377a177a19393
@register_parser(0x547)
class TODO547(BaseParser):
    def __init__(self, stocks: list[MARKET, str]):
        count = len(stocks)
        if count <= 0:
            raise Exception("stocks count must > 0")
        self.body = bytearray(struct.pack('<H', count))
        
        for (market, code) in stocks:
            if type(code) is six.text_type:
                code = code.encode("gbk")
            self.body.extend(struct.pack('<B6sI', market.value, code, 0))
    @override
    def deserialize(self, data):
        print("data: ", data.hex())
            
        return data

# 00 00|00 00|00 00|50 00|00 00|05 00|00 00|01 00|00 00 # 上证A股
# 02 00|00 00|00 00|50 00|00 00|05 00|00 00|01 00|00 00 # 深证A股
# 06 00|00 00|28 00|50 00|00 00|05 00|00 00|01 00|00 00 # A股Default
# 07 00|00 00|00 00|28 00|00 00|05 00|00 00|01 00|00 00 # B股
# 08 00|00 00|00 00|50 00|00 00|05 00|00 00|01 00|00 00 # 科创
# 0c 00|00 00|00 00|50 00|00 00|05 00|00 00|01 00|00 00 # 北证A股
# 0e 00|00 00|00 00|50 00|00 00|05 00|00 00|01 00|00 00 # 创业
@register_parser(0x54b)
class QuotesList(BaseParser):
    def __init__(self, category: CATEGORY, start: int = 0, count: int = 0x50):
        self.body = struct.pack('<HHHHHHHHH', category.value, 0, start, count, 0 ,5, 0, 1, 0)
    @override
    def deserialize(self, data):
        (block, count) = struct.unpack('<HH', data[:4])
        pos = 4

        print("block: %d, count: %d" % (block, count))
        
        stocks = []
        for _ in range(count):
            (market, code, active1 ) = struct.unpack('<B6sH', data[pos: pos + 9])
            pos += 9
            price, pos = get_price(data, pos)
            last_close, pos = get_price(data, pos)
            open, pos = get_price(data, pos)
            high, pos = get_price(data, pos)
            low, pos = get_price(data, pos)
            server_time, pos = get_price(data, pos)
            after_hour, pos = get_price(data, pos) # 盘后交易量
            vol, pos = get_price(data, pos)
            cur_vol, pos = get_price(data, pos)

            last_close += price
            open += price
            high += price
            low += price
            server_time = _format_time(server_time)

            (amount,) = struct.unpack('<f', data[pos: pos + 4])
            pos += 4

            s_vol, pos = get_price(data, pos)
            b_vol, pos = get_price(data, pos)
            s_amount, pos = get_price(data, pos) #reversed_bytes2
            b_amount, pos = get_price(data, pos) #reversed_bytes3

            handi_cap = {
                'bid': [],
                'ask': [],
            }
            for _ in range(1): # 5个
                bid, pos = get_price(data, pos)
                ask, pos = get_price(data, pos)
                bid_vol, pos = get_price(data, pos)
                ask_vol, pos = get_price(data, pos)

                bid += price
                ask += price

                handi_cap['bid'].append({
                    'price': bid,
                    'vol': bid_vol,
                })
                handi_cap['ask'].append({
                    'price': ask,
                    'vol': ask_vol,
                })

            # (v1, v2, unknown1, _) = struct.unpack('<HhBBfBB10s', data[pos: pos + 22])
            (v1, v2, unknown1, _) = struct.unpack('<Hh8s10s', data[pos: pos + 22])
            pos += 22
            # (unknown2, unknown22, _) = struct.unpack('<ff24s', data[pos: pos + 32])
            (unknown2, _) = struct.unpack('<8s24s', data[pos: pos + 32])
            pos += 32
            active2, = struct.unpack('<H', data[pos: pos + 2]) # == active1
            pos += 2

            stocks.append({
                'market': MARKET(market),
                'code': code.decode('gbk'),
                'price': price,
                'open': open,
                'high': high,
                'low': low,
                'last_close': last_close,
                'server_time': server_time,
                'after_hour': after_hour,
                'vol': vol,
                'cur_vol': cur_vol,
                'amount': amount,
                's_vol': s_vol,
                'b_vol': b_vol,
                's_amount': s_amount,
                'b_amount': b_amount,
                # 'handi_cap': handi_cap,
                'v1': v1,
                'v2': v2,
                'unknown1': unknown1.hex(),
                'unknown2': unknown2.hex(),
                'active1': active1,
                'active2': active2,
            })
        return stocks

# >0c f32d8800 01 8300 8300 4c05 | 0500 00000000 0000 1100 0030303030303100333030373636003330303739300033303132333600333030363537003330303932360033303036303401363033383933003030303135350033303034333201363035353938003030323437320136303035343700303032323631003330303036350030303236343000333030393633
# <b1cb7400 1c ff2d8800 00 4c05 a304 df06 789c75946b4c53671cc6ffef29d07268cfa1078a06499529c36583f50eac5b4e41702ba5355ec6d06d06dd07972c448dbbbb0fb55ccbc5225044a86ca52d051c2a9d651d552a8439c7580ec6d9396288ec6296a84159b23042ec4edd87950fe73ddf9f5f9ee7f7be07400c208b1eb95b5c4395eab1326b9821a628676d23b2df89771fe831d55af21dd5bbc05e8d01aadf5f571ce62f4770a8bc602a839833f551a52edbface24701cb7189432599e465321f6ab43c88efad11b5d3e8670e87b1bb774bcf2d9dc31d3e074aa3f44c2375e1cd057d8304a03216482b9c464880d32fdf31bfd60f67c2117a8e23f50818c491a975a913a7fbbed7b8600f745a10337ddd1192fdfe60ffc1c078e4554085bfd2c64352200e875ea0391ff43bc171b68d144791117844962217285527330d9bdd38ddc6810550e7632c4657ce412657e4116d49abc37139b160410b0251442b24510a632810028ab34fc1dc3193dfe8c4e6b19e05ced6072b48c469d372f1acb6e47cdecb7abfd2a5be7eb3e4953bae3e14fc68bcbc286210138fcac9d1e891b8545a99004e6164b696ccef8cc197a75e3ab212ecebc28ca295068ecfca12cad5259ea9a6421b6ae3867fcbec5b365be5bd8d949042324a056bc0985e301f860f6edd0c7c56404b45d747be56ececdecfca75d64aa2ea15da7557d894c012f430c90b67ebc59a4edeb37facf2574aff0e0ca186b6610eb45e144009624d9531a8999acff5e1b7de434ce89e912228d4c995fa01491bd0ba88fe7c25cd83554eff510f30bc86f891f4cdff0a9c8e432f3da2c98d4729da7073e9e96940624803f68588d211dd95ba25bda7b7a828b2422a34f47ae5607052364711159ecb8cd108fc9b6135477fa8bfb09a3cf8c3bcd0268395e08b6cccec4cef5a9c0eeb575561f1bb270789a7e98d5cc799d8382e86a2aa52244546f50c9d5fac61f19a223c7f75dc6a92d39af4f1a5d36716b200942bfb0fef1b872c9efd1db9cffc11afb2d7f35d29b6f49396f5988602753ab0bf219deb94d14f55289e57e3f717f93e501aa4389b62543cdc7a16370663d207e575c5a2aceb6303f225e8b4d7836a3963ede769893c0f0d8a914aa3c45067941de82aa510d32f48e32c4a2bcd5233a4f9ebfeb315eea13382cf1f0c5095404025e38310178603eb2adf4498c11cdf0fbf46d9d8cd37d06c91691a955793d6420b74c2cdd7366be9f58cef505c481b79a6fcc18af581247fd82a2ee511ea0512cb7935a89c4c15dbc61cd0fc6932dd57dd2b8c4a9bd27aa5da1d0c80f5123396d48a5daed1863bde7b8e6b60fbddb609936d96f649fb46e045f3d5108766187b413e19002ba61fb1a8ceac359facfc81427e6101515cfbefda3d450c67d348169e630d70f0c11f0f0badba75053007bfbd8f33b4eac56749f7e0face30240d6dc9697d3a8bb9172d05d4b5af373ce5ab9498f38b339f51ca5a295342a5915e5e14b92538a9b7f65883ff8b5de792c38c77b5ce535390702c8f3c483c07972732154b720fbb758f93a0914003caa34ccc4643d97de43d70977723aaa7adaab40a3046a206798ef8e3f99b0c7c30ed89a1f9adfe67622d9beeba6dacfb38221299c5bdd0aa82da50e0baf5b8984e1ea9bf70c793149117a932e7cc0c94902ea5f8efca387
@register_parser(0x54c)
class Quotes(QuotesList):
    def __init__(self, stocks: list[MARKET, str]):
        count = len(stocks)
        if count <= 0:
            raise Exception("stocks count must > 0")
        self.body = bytearray(struct.pack('<HIHH', 5, 0, 0, count))
        for (market, code) in stocks:
            self.body.extend(struct.pack('<B6s', market.value, code.encode('gbk')))


@register_parser(0x563)
class Unusual(BaseParser): # 主力监控
    def __init__(self, market: MARKET, start: int, count: int = 600):
        self.body = struct.pack('<HII', market.value, start, count)
    @override
    def deserialize(self, data):
        (count, ) = struct.unpack('<H', data[:2])

        stocks = []
        for i in range(count):
            pice_data = data[32 * i + 2: 32 * (i + 1) + 2]

            market, code, _, type, _, index, z = struct.unpack('<H6sBBBHH', pice_data[:15])
            hour, minute_sec = struct.unpack('<BH', pice_data[29: 32])

            type, val = self.unpack_by_type(type, pice_data[15: 28])

            # print(pice_data.hex())
            stocks.append({
                "index": index,
                "market": MARKET(market),
                "code": code.decode('gbk').replace('\x00', ''),
                "time": f"{hour:02d}:{minute_sec // 100:02d}:{minute_sec % 100:02d}",
                "type": type,
                "val": val,
            })
        return stocks
    
    def unpack_by_type(self, type: int, data: bytearray):
        v1, v2, v3, v4 = struct.unpack('<Bfff', data)
        desc = ''
        val = ''
        match type:
            case 0x03: # 主力买入、卖出
                if v1 == 0x00:
                    desc = "主力买入"
                else:
                    desc = "主力卖出"
                val = f"{v2:.2f}/{v3:.2f}"
            case 0x04: # 加速拉升
                desc = "加速拉升"
                val = f"{v2*100:.2f}%"
            case 0x05: # 加速下跌
                desc = "加速下跌"
            case 0x06: # 低位反弹
                desc = "低位反弹"
                val = f"{v2*100:.2f}%"
            case 0x07: # 高位回落
                desc = "高位回落"
                val = f"{v2*100:.2f}%"
            case 0x08: # 撑杆跳高
                desc = "撑杆跳高"
                val = f"{v2*100:.2f}%"
            case 0x09: # 平台跳水
                desc = "平台跳水"
                val = f"{v2*100:.2f}%"
            case 0x0a: # 单笔冲涨、跌
                desc = "单笔冲" + ("跌" if v2 < 0x00 else "涨")
                val = f"{v2*100:.2f}%"
            case 0x0b: # 区间放量 涨、跌、平
                desc = "区间放量"
                val = f"{v2:.1f}倍"
                if v3 == 0:
                    desc += "平"
                else:
                    desc += "跌" if v3 < 0 else "涨"
                    val += f"{v3*100:.2f}%"
            case 0x0c: # 区间缩量
                desc = "区间缩量"
            case 0x10: # 大单托盘
                desc = "大单托盘"
                val = f"{v4:.2f}/{v3:.2f}"
            case 0x11: # 大单压盘
                desc = "大单压盘"
                val = f"{v2:.2f}/{v3:.2f}"
            case 0x12: # 大单锁盘
                desc = "大单锁盘"
            case 0x13: # 竞价试买
                desc = "竞价试买"
                val = f"{v2:.2f}/{v3:.2f}"
            case 0x14: # 打开涨停
                type, v2, v3 = struct.unpack('<Bff', data[1:10])
                direction = "涨" if v1 == 0x00 else "跌"
                if type == 0x01:
                    desc = f"逼近{direction}停"
                elif type == 0x02:
                    desc = f"封{direction}停板"
                elif type == 0x04:
                    desc = f"封{direction}大减"
                elif type == 0x05:
                    desc = f"打开{direction}停"
                val = f"{v2:.2f}/{v3:.2f}"
            case 0x15: # 尾盘
                if v1 == 0x00:
                    desc = "尾盘??"
                elif v1 == 0x01:
                    desc = "尾盘对倒"
                elif v1 == 0x02:
                    desc = "尾盘拉升"
                else:
                    desc = "尾盘???"
                val = f"{v2*100:.2f}%/{v3:.2f}"
            case 0x16: # 盘中弱势、强势
                desc = "盘中" + ("弱势" if v2 < 0x00 else "强势")
                val = f"{v2*100:.2f}%"
            case 0x1d: # 急速拉升
                desc = "急速拉升"
                val = f"{v2*100:.2f}%"
            case 0x1e: # 急速下跌
                desc = "急速下跌" 
                val = f"{v2*100:.2f}%"
            
        return desc, val