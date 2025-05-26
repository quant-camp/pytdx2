import struct
from typing import override
from parser.baseparser import BaseParser, register_parser
import six

@register_parser(u'0c 1f 18 76', u'00 01', u'10 00')
class Finance(BaseParser):
    def __init__(self, market, code):
        if type(code) is six.text_type:
            code = code.encode("utf-8")
        self.body.extend(struct.pack(u"<HB6s", 1, market, code))

    @override
    def deserialize(self, data):
        (
            num,
            market,
            code,
            liutongguben,
            province,
            industry,
            updated_date,
            ipo_date,
            zongguben,
            guojiagu,
            FaQiRenFaRenGu,
            FaRenGu,
            BGu,
            HGu,
            MeiGuShouYi,
            ZiChanZongJi,
            LiuDongZiChanZongJi,
            GuDingZiChanJinE,
            WuXingZiChan,
            GuDongRenShu,
            LiuDongFuZhaiHeJi,
            changqifuzhai,
            ZiBenGongJiJin,
            GuiMuQuanYiHeJi,
            YinYeZongShouRu,
            YinYeChengBen,
            YingShouZhangKuan,
            YinYeLiRun,
            TouZiShouYi,
            JingYinXianJinLiuJinE,
            zongxianjinliu,
            CunHuo,
            LiRunZongE,
            ShuiHouLiRun,
            GuiMuJinLiRun,
            WeiFenLiRun,
            MeiGuJinZiChan,
            baoliu2
        ) = struct.unpack("<HB6sfHHIIffffffffffffffffffffffffffffff", data)

        return {
            'market': market,
            'code': code.decode('utf-8'),
            'liutongguben': liutongguben,
            'province': province,
            'industry': industry,
            'updated_date': updated_date,
            'ipo_date': ipo_date,
            'zongguben': zongguben,
            'guojiagu': guojiagu,
            'FaQiRenFaRenGu': FaQiRenFaRenGu,
            'FaRenGu': FaRenGu,
            'BGu': BGu,
            'HGu': HGu,
            'MeiGuShouYi': MeiGuShouYi,
            'ZiChanZongJi': ZiChanZongJi,
            'LiuDongZiChanZongJi': LiuDongZiChanZongJi,
            'GuDingZiChanJinE': GuDingZiChanJinE,
            'WuXingZiChan': WuXingZiChan,
            'GuDongRenShu': GuDongRenShu,
            'LiuDongFuZhaiHeJi': LiuDongFuZhaiHeJi,
            'changqifuzhai': changqifuzhai,
            'ZiBenGongJiJin': ZiBenGongJiJin,
            'GuiMuQuanYiHeJi': GuiMuQuanYiHeJi,
            'YinYeZongShouRu': YinYeZongShouRu,
            'YinYeChengBen': YinYeChengBen,
            'YingShouZhangKuan': YingShouZhangKuan,
            'YinYeLiRun': YinYeLiRun,
            'TouZiShouYi': TouZiShouYi,
            'JingYinXianJinLiuJinE': JingYinXianJinLiuJinE,
            'zongxianjinliu': zongxianjinliu,
            'CunHuo': CunHuo,
            'LiRunZongE': LiRunZongE,
            'ShuiHouLiRun': ShuiHouLiRun,
            'GuiMuJinLiRun': GuiMuJinLiRun,
            'WeiFenLiRun': WeiFenLiRun,
            'MeiGuJinZiChan': MeiGuJinZiChan,
            'baoliu2': baoliu2
        }
