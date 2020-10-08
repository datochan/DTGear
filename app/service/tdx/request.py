"""
    request
    ~~~~~~~~~~~~~~
    数据传输对象, 用于封装通达信的请求包

    :copyright: (c) 16/11/26 by datochan.
"""
import binascii
import random
import struct
import time

from app.comm.utils import strings, crypto


class RequestNode(object):
    """
        财报相关的封包
        # 	EventId   uint16
        # 	CmdId     uint16
        # 	IsRaw     byte
        # 	Index     uint16
        # 	RawData   interface{}    // 原始请求封包体的原始数据
    """
    def __init__(self):
        self.prex_flag = 0
        self.event_id = 0
        self.cmd_id = 0
        self.idx = 0
        self.is_compress = 0  # 用于标识封包体是否使用zlib压缩
        self.raw_data = b""   # 封包体

    @staticmethod
    def header_length():
        """
        返回封包头的长度
        :return:
        """
        return struct.calcsize("<BHHBHHH")

    def body_length(self):
        """
        返回封包体的长度
        :return:
        """
        return len(self.raw_data)

    def generate(self):
        """
        生成通达信通讯封包
        # 	flag  byte      // 固定为0x0C
        # 	index uint16    // idx(先随机，发现特殊值再单独处理)
        # 	cmdId uint16    // 具体命令的子标识
        # 	isRaw byte      // 是否是未压缩的原始封包(已知封包全是0,待发现特殊值再特殊封装)
        # 	bodyLength uint16        // H: 分别是封包长度(封包长度+2字节)
        # 	bodyMaxLength  uint16    // H: 解压所需要的空间大小(已知两个相等待发现特殊值再特殊处理)
        # 	eventId        uint16    // H: 事件标识, 靠此字段可以确定封包的类别
        :return:
        """
        header = struct.pack("<BHHBHHH", self.prex_flag, self.idx, self.cmd_id, self.is_compress,
                             self.body_length() + 2, self.body_length() + 2, self.event_id)

        return b"".join([header, self.raw_data])


class RequestHQNode(RequestNode):
    """
    请求行情数据封包的基本包装
        # 	EventId   uint16
        # 	CmdId     uint16
        # 	IsRaw     byte
        # 	Index     uint16
        # 	RawData   interface{}    // 原始请求封包体的原始数据
    """
    def __init__(self):
        super(RequestHQNode, self).__init__()
        self.prex_flag = 0x0C

    def generate(self):
        """
        生成通达信通讯封包
        # 	flag  byte      // 固定为0x0C
        # 	index uint16    // idx(先随机，发现特殊值再单独处理)
        # 	cmdId uint16    // 具体命令的子标识
        # 	isRaw byte      // 是否是未压缩的原始封包(已知封包全是0,待发现特殊值再特殊封装)
        # 	bodyLength uint16        // H: 分别是封包长度(封包长度+2字节)
        # 	bodyMaxLength  uint16    // H: 解压所需要的空间大小(已知两个相等待发现特殊值再特殊处理)
        # 	eventId        uint16    // H: 事件标识, 靠此字段可以确定封包的类别
        :return:
        """
        if self.idx == 0:
            self.idx = random.randint(0x00, 0x7fff)

        return super(RequestHQNode, self).generate()


def gen_device_node(main_version=7.43, core_version=5.92):
    """
    生成注册设备封包
    :param main_version: 软件版本号, 默认为: 7.29
    :param core_version: 行情数据引擎版本号, 默认为: 5.895

    :return:
        # 	unknown1    [110]byte // 0
        # 	unknown2    uint32    // 0x01040000
        # 	unknown3    uint32    // 0
        # 	mainVersion float32
        # 	coreVersion float32
        # 	unknown4    uint32     // 0
        # 	unknown5    [47]byte   // 0
        # 	macAddr     [12]byte   // rand
        # 	unknown6    [89]byte   // 0
    """
    req = RequestHQNode()
    req.event_id = 0x0B
    req.cmd_id = 0x007B

    mac_addr = bytes(strings.random_mac_address(), "ascii")
    content = struct.pack("<110s2L2fL47s12s89s", b"\0" * 110, 0x01040000, 0, main_version, core_version, 0,
                          b"\0" * 47, mac_addr, b"\0" * 89)
    req.raw_data = crypto.encrypt_with_blowfish(content)

    return req


def gen_market_init():
    """
    初始化市场行情信息
    :return:
    """
    req = RequestHQNode()
    req.event_id = 0x000D
    req.cmd_id = 0x0094
    req.is_compress = 1
    req.raw_data = b"\01"

    return req


def gen_notice():
    """
    请求服务器公告信息
    :return:
    """
    req = RequestHQNode()
    req.event_id = 0x0FDB
    req.cmd_id = 0x0099
    req.is_compress = 1
    req.raw_data = struct.pack("30s", binascii.a2b_hex(b"7464786C6576656C320000AE47E940040000000000000000000000000003"))
    return req


def gen_market_stock_count(market=0):
    """
    获取指定市场金融产品数量
    :param market: 深圳0, 上海1
    :return:
    """
    req = RequestHQNode()
    req.event_id = 0x044E
    req.is_compress = 1

    if market == 0:
        req.cmd_id = 0x006B
    else:
        req.cmd_id = 0x006C

    today = "".join(time.strftime('%Y%m%d', time.localtime(time.time())))
    req.raw_data = struct.pack("<HL", market, int(today))

    return req


def gen_stock_base(market, offset):
    """
    请求股票基础信息
    :param market: 深圳0, 上海1
    :param offset:
    :return:
    """
    req = RequestHQNode()
    req.event_id = 0x0450
    req.is_compress = 1

    if market == 0:
        req.cmd_id = 0x006D
    else:
        req.cmd_id = 0x006E

    req.raw_data = struct.pack("<2H", market, offset)

    return req


def gen_stock_bonus(stocks: bytes, idx):
    """
    请求股票高送转信息
    :param stocks: 7byte: market&code[...]
    :param idx:
    :return:
    """
    req = RequestHQNode()
    req.event_id = 0x000F
    req.cmd_id = 0x0076
    req.is_compress = 1
    req.idx = idx

    content_length = len(stocks)
    stocks_count = int(content_length/7)

    req.raw_data = struct.pack("<H%ds" % content_length, stocks_count, stocks)

    return req


def gen_stock_days(market, code, start: int, end: int, idx):
    """
    请求日线数据
    :param market:
    :param code:
    :param start: int
    :param end: int
    :param idx:
    :return:

    # 0C 13 38 87 00 01 14 00 14 00 CD 0F 00 00 33 39 39 30 30 31 00 2A 33 01 BC A2 33 01 04 00
    # -- ----- -- ----- ----------- ----- ----- ----------------- ----------- ----------- -----
    #    idx                              market code             start       end
    """
    req = RequestHQNode()
    req.event_id = 0x0FCD
    req.cmd_id = 0x0087
    req.is_compress = 1
    req.idx = idx

    req.raw_data = struct.pack("<H6s2IH", market, code.encode("ascii"), start, end, 0x4)

    return req


def gen_report_download(filename, offset=0):
    """
    请求财务数据状态信息
    :param str filename:
    :param int offset: 从多少偏移开始下载
    :return:
    """
    req = RequestNode()
    req.event_id = 0x06B9
    req.cmd_id = 0
    req.is_compress = 0
    req.raw_data = b"\01"
    idx = offset
    node_size = 0x7530
    req.raw_data = struct.pack("<2I100s", idx, node_size, filename.encode('ascii'))

    return req
