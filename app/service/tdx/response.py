"""
    response
    ~~~~~~~~~~~~~~
    数据传输对象, 用于封装通达信的应答包

    :copyright: (c) 16/11/26 by datochan.
"""

import struct

from app.comm.utils.bytes import Buffer


class ResponseHeader(object):
    """
    应答封包的基本包装
        # PacketFlag uint32        // 封包标识
        # IsCompress  byte         // 封包是否被压缩
        # Index uint16             // 索引(股票索引)
        # CmdId uint16             //
        # Unknown   byte           // 未知标识
        # EventId    uint16        // 事件标识, 靠此字段可以确定封包的类别
        # BodyLength uint16        // 分别是封包长度
        # BodyMaxLength  uint16    // 解压所需要的空间大小
    """
    __identity = "<LB2HB3H"

    def __init__(self):
        self.pkg_flag = 0
        self.is_compress = False  # 用于标识封包体是否使用zlib压缩
        self.idx = 0
        self.cmd_id = 0
        self.unknown = 0
        self.event_id = 0
        self.body_length = 0
        self.body_max_length = 0

    @classmethod
    def length(cls):
        return struct.calcsize(cls.__identity)

    @classmethod
    def parse(cls, data: Buffer):
        """
        解析应答封包
        :param data:
        :return:
        """
        header = ResponseHeader()
        data_header = data.read_format(cls.__identity)

        header.pkg_flag = data_header[0]
        header.is_compress = data_header[1] & 0x10 != 0
        header.idx = data_header[2]
        header.cmd_id = data_header[3]
        header.unknown = data_header[4]
        header.event_id = data_header[5]
        header.body_length = data_header[6]
        header.body_max_length = data_header[7]

        return header


class ResponseMarketInfo:
    """
    #     Unknown1   [10]uint32 // 10L: unknown
    #     Unknown2   uint16     // H: unknown
    #     DateSZ     uint32     // L: 深最后交易日期
    #     LastSZFlag uint32     // L: 深最后交易Flag
    #     DateSH     uint32     // L: 沪最后交易日期
    #     LastSHFlag uint32     // L: 沪最后交易Flag
    #     Unknown3   uint32     // L: unknown
    #     Unknown4   uint16     // H: unknown
    #     Unknown5   uint32     // L: unknown
    #     ServerName [21]byte   // 21s: 服务器名称
    #     DomainUrl  [18]byte   // 18s: domain
    """
    __identity = "<10LH4LLHL21s18s"

    def __init__(self):
        self.date_sz = 0
        self.data_sh = 0
        self.last_flag_sz = 0
        self.last_flag_sh = 0
        self.server_name = ""
        self.domain_url = ""

    @classmethod
    def length(cls):
        return struct.calcsize(cls.__identity)

    @classmethod
    def parse(cls, data: Buffer):
        """
        解析
        :param data:
        :return:
        """
        market_info = ResponseMarketInfo()

        server_info = data.read_format(cls.__identity)

        market_info.date_sz = server_info[11]
        market_info.last_flag_sz = server_info[12]
        market_info.data_sh = server_info[13]
        market_info.last_flag_sh = server_info[14]
        market_info.server_name = str(server_info[18].decode('gbk'))
        market_info.domain_url = str(server_info[19].decode('ascii'))

        return market_info


class ResponseStockBase:
    """
    #     Code         [6]byte    // 股票代码
    #     Unknown1     uint16     // 未知 固定0x64
    #     Name         [8]byte    // 股票名称
    #     Unknown2     uint32     // 未知
    #     Unknown3     byte       // 未知 固定0x02
    #     Price        float32    // 价格(昨收)
    #     Bonus1       uint16     // 用于计算权息数据
    #     Bonus2       uint16     // 权息数量
    """
    __identity = "<6sH8sLBf2H"

    def __init__(self):
        self.code = ""
        self.name = ""
        self.unknown1 = 0
        self.unknown2 = 0
        self.unknown3 = 0
        self.price = 0.0
        self.bonus1 = 0
        self.bonus2 = 0

    @classmethod
    def length(cls):
        return struct.calcsize(cls.__identity)

    @classmethod
    def parse(cls, data: Buffer):
        """
        解析
        :param data:
        :return:
        """
        data_stock = data.read_format(cls.__identity)

        stock_base = ResponseStockBase()

        stock_base.code = "%s" % data_stock[0].decode('gbk')
        stock_base.unknown1 = data_stock[1]
        stock_base.name = "%s" % data_stock[2].decode('gbk').replace("\00", "")
        stock_base.unknown2 = data_stock[3]
        stock_base.unknown3 = data_stock[4]
        stock_base.price = data_stock[5]
        stock_base.bonus1 = data_stock[6]
        stock_base.bonus2 = data_stock[7]

        return stock_base


class ResponseStockBonus:
    """
    #     Market       byte    // B: 市场(market): 0深, 1沪
    #     Code         [6]byte // 6s: 股票代码(code)
    #     Unknown1     byte    // B: 股票代码的0结束符(python解析麻烦,所以单独解析出来不使用)
    #     Date         int32   // L: 日期(date)
    #     Type         byte    // B: 分红配股类型(type): 1标识除权除息, 2: 配送股上市; 3: 非流通股上市; 4:未知股本变动; 5: 股本变动,
                                        6: 增发新股, 7: 股本回购, 8: 增发新股上市, 9:转配股上市
    #     Money        float32 // 送现金
    #     Price        float32 // 配股价
    #     Count        float32 // 送股数
    #     Rate         float32 // 配股比例
    """
    __identity = "<B6sBLB4f"

    def __init__(self):
        self.market = 0
        self.code = ""
        self.date = ""
        self.type = 0
        self.money = 0.0
        self.price = 0.0
        self.count = 0.0
        self.rate = 0.0

    @classmethod
    def length(cls):
        return struct.calcsize(cls.__identity)

    @classmethod
    def parse(cls, data: Buffer):
        """
        解析
        :param data:
        :return:
        """
        data_stock = data.read_format(cls.__identity)

        stock_bonus = ResponseStockBonus()

        stock_bonus.market = data_stock[0]
        stock_bonus.code = "%s" % data_stock[1].decode('ascii')
        stock_bonus.date = "%d%02d%02d" % (data_stock[3] / 10000, data_stock[3] % 10000 / 100, data_stock[3] % 100)

        stock_bonus.type = data_stock[4]

        stock_bonus.money = data_stock[5]
        stock_bonus.price = data_stock[6]
        stock_bonus.count = data_stock[7]
        stock_bonus.rate = data_stock[8]

        return stock_bonus


class ResponseStockDays:
    """
    #      Date		uint32
    #      Open       uint32
    #      High       uint32
    #      Low        uint32
    #      Close      uint32
    #      Amount     float32
    #      Volume     uint32
    #      Unknown1   uint32
    """
    __identity = "<IIIIIfII"

    def __init__(self):
        self.date = ""
        self.open = 0.0
        self.high = 0.0
        self.low = 0.0
        self.close = 0.0
        self.amount = 0.0
        self.volume = 0
        self.unknown1 = 0

    @classmethod
    def length(cls):
        return struct.calcsize(cls.__identity)

    @classmethod
    def parse(cls, data: Buffer, _fund: bool = False):
        """
        解析
        :param data:
        :param bool _fund: 是否是基金
        :return:
        """
        data_stock = data.read_format(cls.__identity)

        stock_day = ResponseStockDays()

        stock_day.date = "%d%02d%02d" % (data_stock[0] / 10000, data_stock[0] % 10000 / 100, data_stock[0] % 100)

        precision = 100.00
        if _fund:
            precision = 1000.00

        stock_day.open = data_stock[1] / precision
        stock_day.high = data_stock[2] / precision
        stock_day.low = data_stock[3] / precision
        stock_day.close = data_stock[4] / precision
        stock_day.amount = data_stock[5]
        stock_day.volume = data_stock[6]

        return stock_day
