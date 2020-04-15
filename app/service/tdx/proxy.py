"""
    proxy
    ~~~~~~~~~~~~~~
    行情代理器, 用于从通达信服务器获取相关的行情信息

    :copyright: (c) 16/11/26 by datochan.
"""
import sys
import zlib
import binascii
import struct

from app.comm.utils.bytes import Buffer
from app.comm.utils.netbase import TCPClient
from app.service.tdx import request
from app.service.tdx.response import ResponseHeader, ResponseMarketInfo

# 用于自定义事件
EVENT_READY = 0x00007190

class TdxProxy(TCPClient):
    def __init__(self, idle_sec=10, interval_sec=5, max_fails=3):
        super(TdxProxy, self).__init__(idle_sec, interval_sec, max_fails)

        self.add_handler(0, self.on_default_handler)
        self.market = ResponseMarketInfo()
        self.stock_sh_count = 0   # 沪市金融产品数量
        self.stock_sz_count = 0   # 深市金融产品数量

    def on_default_handler(self, header:ResponseHeader, body:Buffer):
        """
        如果没有匹配处理器则由此处理
        :param header:
        :param body:
        :return:
        """
        if header.event_id == 0x0B:
            print("注册模拟设备成功的信息: %s." % str(binascii.b2a_hex(body.bytes())))
        elif header.event_id == 0x0FDB:
            notice = struct.unpack("<116s", body.bytes()[0xb2:0x126])
            print("收到代理服务器的公告信息:%s ..." % notice[0].decode('gbk'))

            callback_proc = self.get_handler(EVENT_READY)
            if callback_proc is not None:
                callback_proc()

        elif header.event_id == 0x000D:
            self.market = ResponseMarketInfo.parse(body)
            print("市场最新交易信息: 券商名称:%s, 最后交易时间:%d" % (self.market.server_name, self.market.date_sz))
        elif header.event_id == 0x044E:
            count = body.read_format("<H")[0]
            if header.cmd_id == 0x6B:
                print("收到sz市场股票数量为: %d." % count)
                self.stock_sz_count = count
            elif header.cmd_id == 0x6C:
                print("收到sh市场股票数量为: %d." % count)
                self.stock_sh_count = count
        else:
            # 收到未知封包
            print("收到未知封包, event_id = %d, content: %s." % (header.event_id, str(binascii.b2a_hex(body.bytes()))))

    def handle_connect(self):
        print("开始连接...")
        self.send(request.gen_device_node().generate())
        self.send(request.gen_market_init().generate())
        self.send(request.gen_notice().generate())
        self.send(request.gen_market_stock_count(0).generate())
        self.send(request.gen_market_stock_count(1).generate())

    def handle_read(self):
        super(TdxProxy, self).handle_read()

        while True:
            try:
                if self.in_buffer.length() <= 0:
                    break

                header_size = ResponseHeader.length()
                header = self.in_buffer.peek_bytes(header_size)
                if len(header) < header_size:
                    self.get_handler(0)(header=Buffer(header))
                    break

                """
                L: 封包标识
                B: 是否压缩的标识
                H: 索引(股票索引)
                B: 判断封包类型(此字段与发送的字段相同，靠这个字段可以确定封包的功能)
                H: 未知标识
                H: 事件标识，靠此字段可以确定封包的类别
                2H: 分别是封包长度, 解压所需要的空间大小
                """
                objHeader = ResponseHeader.parse(Buffer(header))

                if self.in_buffer.length() < objHeader.body_length+header_size:
                    # 如果封包不足则等待下一次接收后继续再判断，直至封包完整再继续解析
                    break

                self.in_buffer.read_bytes(header_size)
                compress_data = self.in_buffer.read_bytes(objHeader.body_length)


                if objHeader.is_compress:
                    decompiler = zlib.decompressobj()
                    content = decompiler.decompress(compress_data)
                else:
                    content = compress_data

                # print("收到 content: %s." % str(binascii.b2a_hex(content)))

                handle_proc = self.get_handler(objHeader.event_id)

                if handle_proc is None:
                    self.get_handler(0)(header=objHeader, body=Buffer(content))
                else:
                    handle_proc(header=objHeader, body=Buffer(content))

            except StopIteration:
                sys.exit()
            except Exception as ex:
                print("发生未知错误: %s" % str(ex))
