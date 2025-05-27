from datetime import datetime
from typing import override
from baseStockClient import BaseStockClient, update_last_ack_time
from block_reader import BlockReader, BlockReader_TYPE_FLAT
from log import log
from params import TDXParams
from parser import finance_report, index_bars, security, setup, company_info, block, xdxr
from parser.baseparser import BaseParser

import pandas as pd

class TdxClient(BaseStockClient):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def call(self, parser: BaseParser):        
        return parser.deserialize(super().send(parser.serialize()))

    def setup(self):
        log.debug("setup")
        self.call(setup.Setup())

    @override
    def connect(self, ip='202.100.166.21', port=7709, time_out=..., bindport=None, bindip='0.0.0.0'):
        return super().connect(ip, port)

    @override
    def doHeartBeat(self):
        self.get_security_count(1)

    @update_last_ack_time
    def get_security_bars(self, market, code, kline_type, start, count):
        return self.call(security.Bars(market, code, kline_type, start, count))

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

        return self.call(security.Quotes(all_stock))

    @update_last_ack_time
    def get_security_count(self, market):
        return self.call(security.Count(market))

    @update_last_ack_time
    def get_security_list(self, market, start):
        return self.call(security.List(market, start))

    @update_last_ack_time
    def get_index_bars(self, market, code, kline_type, start, count):
        return self.call(index_bars.IndexBars(market, code, kline_type, start, count))

    @update_last_ack_time
    def get_orders(self, market, code):
        return self.call(security.Orders(market, code))

    @update_last_ack_time
    def get_history_orders(self, market, code, date):
        return self.call(security.HistoryOrders(market, code, date))

    @update_last_ack_time
    def get_transaction(self, market, code, start, count):
        return self.call(security.Transaction(market, code, start, count))

    @update_last_ack_time
    def get_history_transaction(self, market, code, date, start, count):
        return self.call(security.HistoryTransaction(market, code, date, start, count))

    @update_last_ack_time
    def get_company_info_category(self, market, code):
        return self.call(company_info.Category(market, code))

    @update_last_ack_time
    def get_company_info_content(self, market, code, filename, start, length):
        return self.call(company_info.Content(market, code, filename, start, length))

    @update_last_ack_time
    def get_xdxr_info(self, market, code):
        return self.call(xdxr.XDXR(market, code))

    @update_last_ack_time
    def get_finance_info(self, market, code):
        return self.call(finance_report.Finance(market, code))

    @update_last_ack_time
    def get_block_meta(self, blockfile):
        return self.call(block.Meta(blockfile))

    @update_last_ack_time
    def get_block_info(self, blockfile, start, size):
        return self.call(block.Info(blockfile, start, size))

    @update_last_ack_time
    def get_report_file(self, filename, offset):
        return self.call(block.Report(filename, offset))

    def get_and_parse_block_info(self, blockfile):
        try:
            meta = self.get_block_meta(blockfile)
        except Exception as e:
            return None

        if not meta:
            return None

        size = meta['size']
        one_chunk = 0x7530


        chuncks = size // one_chunk
        if size % one_chunk != 0:
            chuncks += 1

        file_content = bytearray()
        for seg in range(chuncks):
            start = seg * one_chunk
            piece_data = self.get_block_info(blockfile, start, size)
            file_content.extend(piece_data)

        return BlockReader().get_data(file_content, BlockReader_TYPE_FLAT)

    def get_report_file_by_size(self, filename, filesize=0, reporthook=None):
        """
        Download file from proxy server

        :param filename the filename to download
        :param filesize the filesize to download , if you do not known the actually filesize, leave this value 0
        """
        filecontent = bytearray(filesize)
        current_downloaded_size = 0
        get_zero_length_package_times = 0
        while current_downloaded_size < filesize or filesize == 0:
            response = self.get_report_file(filename, current_downloaded_size)
            if response["chunksize"] > 0:
                current_downloaded_size = current_downloaded_size + \
                    response["chunksize"]
                filecontent.extend(response["chunkdata"])
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
                return 1
            return 0
        # 新版一劳永逸偷懒写法zzz
        market_code = 1 if str(code)[0] == '6' else 0
        # https://github.com/rainx/pytdx/issues/33
        # 0 - 深圳， 1 - 上海
        

        data = pd.concat(
            [
                to_df(
                    self.get_security_bars(__select_market_code(code), code, 9, (9 - i) * 800, 800)
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
    if client.connect('202.100.166.21'):
        log.info("获取股票行情")
        print_df(client.get_security_quotes([(0, '000001'), (1, '600300')]))
        log.info("获取k线")
        print_df(client.get_security_bars(0, '000001', 9, 0, 3))
        log.info("获取 深市 股票数量")
        print_df(client.get_security_count(0))
        log.info("获取股票列表")
        print_df(client.get_security_list(1, 255))
        log.info("获取指数k线")
        print_df(client.get_index_bars(1, '000001', 9, 1, 2))
        log.info("查询分时行情")
        print_df(client.get_orders(TDXParams.MARKET_SH, '600300'))
        log.info("查询历史分时行情")
        print_df(client.get_history_orders(TDXParams.MARKET_SH, '600300', datetime(2023, 3, 1).date()))
        log.info("查询分时成交")
        print_df(client.get_transaction(TDXParams.MARKET_SZ, '000001', 0, 30))
        log.info("查询历史分时成交")
        print_df(client.get_history_transaction(TDXParams.MARKET_SZ, '000001', datetime(2023, 3, 1).date(), 0, 10))
        log.info("查询公司信息目录")
        print_df(client.get_company_info_category(TDXParams.MARKET_SZ, '000001'))
        log.info("读取公司信息-最新提示")
        print_df(client.get_company_info_content(0, '000001', '000001.txt', 0, 10))
        log.info("读取除权除息信息")
        print_df(client.get_xdxr_info(1, '600300'))
        log.info("读取财务信息")
        print_df(client.get_finance_info(0, '000001'))
        log.info("日线级别k线获取函数")
        pprint.pprint(client.get_k_data('000001', '2017-07-01', '2017-07-10'))
    client.disconnect()