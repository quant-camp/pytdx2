from datetime import date
import math
from typing import override
from baseStockClient import BaseStockClient, update_last_ack_time
from block_reader import BlockReader, BlockReader_TYPE_FLAT
from log import log
from const import BLOCK_FILE_TYPE, KLINE_TYPE, MARKET
from parser import stock, remote, company_info, block
from parser.baseparser import BaseParser

import pandas as pd

class TdxClient(BaseStockClient):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def call(self, parser: BaseParser):
        return parser.deserialize(super().send(parser.serialize()))

    def setup(self):
        self.call(remote.Connect())
        # self.call(setup.Notice())

    @override
    def connect(self, ip='202.100.166.21', port=7709, time_out=..., bindport=None, bindip='0.0.0.0'):
        return super().connect(ip, port)

    @override
    def doHeartBeat(self):
        self.call(remote.HeartBeat())

    @update_last_ack_time
    def get_security_bars(self, market: MARKET, code: str, kline_type: KLINE_TYPE, start, count):
        # k线数据最多800条
        MAX_KLINE_COUNT = 800
        bars = []
        while len(bars) < count:
            part = self.call(stock.Bars(market, code, kline_type, start, min(count - len(bars), MAX_KLINE_COUNT)))
            if not part:
                break
            bars = [*part, *bars]
            if len(part) < MAX_KLINE_COUNT:
                break
            start = start + len(part)

        return bars

    @update_last_ack_time
    def get_security_quotes(self, all_stock, code=None):
        """
        支持三种形式的参数
        get_security_quotes(market, code )
        get_security_quotes((market, code))
        get_security_quotes([(market1, code1), (market2, code2)] )
        :param all_stock （market, code) 的数组
        :param code{optional} code to query
        :return:
        """

        if code is not None:
            all_stock = [(all_stock, code)]
        elif (isinstance(all_stock, list) or isinstance(all_stock, tuple))\
                and len(all_stock) == 2 and type(all_stock[0]) is int:
            all_stock = [all_stock]

        return self.call(stock.Quotes(all_stock))

    @update_last_ack_time
    def get_security_count(self, market: MARKET):
        return self.call(stock.Count(market))

    @update_last_ack_time
    def get_security_list(self, market: MARKET, start):
        return self.call(stock.List(market, start))

    @update_last_ack_time
    def get_orders(self, market: MARKET, code: str):
        return self.call(stock.Orders(market, code))

    @update_last_ack_time
    def get_history_orders(self, market: MARKET, code: str, date: date):
        return self.call(stock.HistoryOrders(market, code, date))

    @update_last_ack_time
    def get_transaction(self, market: MARKET, code: str):
        # 这里最多就1800条
        MAX_TRANSACTION_COUNT = 1800
        start = 0
        transaction = []
        while True:
            part = self.call(stock.Transaction(market, code, start, MAX_TRANSACTION_COUNT))
            if not part:
                break
            transaction = [*part, *transaction]
            if len(part) < MAX_TRANSACTION_COUNT:
                break
            start = start + len(part)
        return transaction

    @update_last_ack_time
    def get_history_transaction(self, market: MARKET, code: str, date: date):
        # ref : https://github.com/rainx/pytdx/issues/7
        # 分笔行情最多2000条
        MAX_TRANSACTION_COUNT = 2000
        start = 0
        transaction = []
        while True:
            part = self.call(stock.HistoryTransaction(market, code, date, start, MAX_TRANSACTION_COUNT))
            if not part:
                break
            transaction.extend(part)
            if len(part) < MAX_TRANSACTION_COUNT:
                break
            start = start + len(part)
            
        return transaction

    @update_last_ack_time
    def get_company_info(self, market: MARKET, code: str):
        category = self.call(company_info.Category(market, code))

        info = []
        for part in category:
            content = self.call(company_info.Content(market, code, part['filename'], part['start'], part['length']))
            info.append({
                'name': part['name'],
                'content': content['content'],
            })

        xdxr = self.call(company_info.XDXR(market, code))
        if xdxr:
            info.append({
                'name': '除权分红',
                'content': xdxr,
            })

        finance = self.call(company_info.Finance(market, code))
        if finance:
            info.append({
                'name': '财报',
                'content': finance,
            })
        return info

    @update_last_ack_time
    def get_block_info(self, block_file_type: BLOCK_FILE_TYPE):
        try:
            meta = self.call(block.Meta(block_file_type))
        except Exception as e:
            log.error(e)
            return None

        if not meta:
            return None

        size = meta['size']
        one_chunk = 0x7530

        file_content = bytearray()
        for seg in range(math.ceil(size / one_chunk)):
            start = seg * one_chunk
            piece_data = self.call(block.Info(block_file_type, start, one_chunk))["data"]
            file_content.extend(piece_data)

        return BlockReader().get_data(file_content, BlockReader_TYPE_FLAT)

    @update_last_ack_time
    def get_report_file(self, filename: str, filesize=0, reporthook=None):
        """
        Download file from proxy server

        :param filename the filename to download
        :param filesize the filesize to download , if you do not known the actually filesize, leave this value 0
        """
        filecontent = bytearray(filesize)
        current_downloaded_size = 0
        get_zero_length_package_times = 0
        while current_downloaded_size < filesize or filesize == 0:
            response = self.call(block.Report(filename, current_downloaded_size))
            if response["size"] > 0:
                current_downloaded_size = current_downloaded_size + \
                    response["size"]
                filecontent.extend(response["data"])
                if reporthook is not None:
                    reporthook(current_downloaded_size,filesize)
            else:
                get_zero_length_package_times = get_zero_length_package_times + 1
                if filesize == 0:
                    break
                elif get_zero_length_package_times > 2:
                    break

        return filecontent    
    
    def get_k_data(self, code, start_date, end_date):
        # 具体详情参见 https://github.com/rainx/pytdx/issues/5
        # 具体详情参见 https://github.com/rainx/pytdx/issues/21
        def __select_market_code(code):
            code = str(code)
            if code[0] in ['5', '6', '9'] or code[:3] in ["009", "126", "110", "201", "202", "203", "204"]:
                return MARKET.SH
            return MARKET.SZ
        # 新版一劳永逸偷懒写法zzz
        market_code = 1 if str(code)[0] == '6' else 0
        # https://github.com/rainx/pytdx/issues/33
        # 0 - 深圳， 1 - 上海
        

        data = pd.concat(
            [
                to_df(
                    self.get_security_bars(__select_market_code(code), code, KLINE_TYPE.DAY_K, (9 - i) * 800, 800)
                ) for i in range(10)
            ], axis=0)
 
        data = data.assign(date=data['datetime'].apply(lambda x: str(x)[0:10]))\
            .assign(code=str(code))\
            .set_index('date', drop=False, inplace=False)\
            .drop(['datetime'], axis=1)[start_date:end_date]
        return data.assign(date=data['date'].apply(lambda x: str(x)[0:10]))

def to_df(v):
    if isinstance(v, list):
        return pd.DataFrame(data=v)
    elif isinstance(v, dict):
        return pd.DataFrame(data=[v, ])
    else:
        return pd.DataFrame(data=[{'value': v}])

if __name__ == "__main__":
    import pprint

    def print_df(data):
        pprint.pprint(to_df(data))

    client = TdxClient()
    if client.connect('180.153.18.172', 80):
        # log.info("获取股票行情")
        # print_df(client.get_security_quotes([(MARKET.SZ, '300766'), (MARKET.SH, '600300')]))
        # log.info("获取 深市 股票数量")
        # print_df(client.get_security_count(MARKET.SZ))
        log.info("获取股票列表")
        print_df(client.get_security_list(MARKET.SH, 22384))
        # log.info("获取股票列表")
        # print_df(client.get_security_list(MARKET.SH, 25217))
        # log.info("获取股票列表")
        # print_df(client.get_security_list(MARKET.SZ, 20569))
        # log.info("获取k线")
        # print_df(client.get_security_bars(MARKET.SZ, '000001', KLINE_TYPE.DAY_K, 0, 500))
        # log.info("获取指数k线")
        # print_df(client.get_security_bars(MARKET.SH, '999999', KLINE_TYPE.DAY_K, 0, 2000))
        # log.info("查询分时行情")
        # print_df(client.get_orders(MARKET.SZ, '000001'))
        # log.info("查询历史分时行情")
        # print_df(client.get_history_orders(MARKET.SZ, '000001', date(2023, 3, 1)))
        # log.info("查询分时成交")
        # print_df(client.get_transaction(MARKET.SZ, '300766'))
        # log.info("查询历史分时成交")
        # print_df(client.get_history_transaction(MARKET.SZ, '300689', date(2025, 5, 22)))
        # log.info("查询公司信息")
        # print_df(client.get_company_info(MARKET.SZ, '000001'))
        log.info("日线级别k线获取函数")
        pprint.pprint(client.get_k_data('000001', '2017-07-01', '2017-07-10'))
        # log.info("获取板块信息")
        # pprint.pprint(client.get_block_info(BLOCK_FILE_TYPE.SZ))
        # log.info("获取报告文件")
        # pprint.pprint(client.get_report_file('tdxfin/gpcw.txt'))
        client.disconnect()