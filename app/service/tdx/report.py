"""
    proxy
    ~~~~~~~~~~~~~~
    行情代理器, 用于从通达信服务器获取相关的行情信息

    :copyright: (c) 16/11/26 by datochan.
"""
import os
import sys
import zlib
import binascii

from app.comm.utils import crypto
from app.comm.utils.bytes import Buffer
from app.comm.utils.netbase import TCPClient
from app.service.tdx import request
from app.service.tdx.response import ResponseHeader


class TdxReportClient(TCPClient):
    def __init__(self, callback=None, idle_sec=10, interval_sec=5, max_fails=3):
        super(TdxReportClient, self).__init__(idle_sec, interval_sec, max_fails)
        self.__callback_proc = callback
        self.cw_list = []
        self.data_gen = None
        self.current_report_offset = 0
        self.current_save_report = ""
        self.add_handler(0, self.on_default_handler)

    @staticmethod
    def on_default_handler(header:ResponseHeader, body:Buffer):
        """
        如果没有匹配处理器则由此处理
        :param header:
        :param body:
        :return:
        """
        print("收到未知封包, event_id = %d, content: %s." % (header.event_id, str(binascii.b2a_hex(body.bytes()))))

    def on_report_list(self, header:ResponseHeader, body:Buffer):
        content = body.bytes().decode("utf-8")

        self.cw_list = content.split('\n')
        self.__callback_proc()

    def on_download(self, header:ResponseHeader, body:Buffer):
        length = body.read_format("<I")[0]
        content = body.bytes()

        if self.current_report_offset is 0:
            fp = open(self.current_save_report, 'wb+')
        else:
            fp = open(self.current_save_report, 'ab+')

        self.current_report_offset += length

        with fp as outfile:
            outfile.write(content)

        fp.close()
        self.send(next(self.data_gen))

    def download_report(self, prex, report_format, project_root):
        """
        下载指定的财报文件
        :param str prex: 前缀
        :param str report_format:
        :param str project_root:
        :return:
        """

        # 过滤出所有需要下载更新的文件
        none_total = 0

        for idx in range(len(self.cw_list), 0, -1):
            # 按时间倒叙
            item = self.cw_list[idx-1]
            item = item.replace('\r', '')
            if len(item) <= 5:
                none_total += 1
                continue
            file_name = item.split(',')[0]
            file_hash = item.split(',')[1]
            file_size = int(item.split(',')[2])

            file_name = file_name.split('.')[0]
            file_path = report_format % (project_root, file_name)
            hash_result = crypto.md5sum(file_path)
            print("更新财报文件 %s, " % file_name, end="")
            if file_hash != hash_result:
                # 如果文件已更新则删除本地文件重新下载
                if os.path.isfile(file_path):
                    os.remove(file_path)

                # 下载文件
                self.current_report_offset = 0
                self.current_save_report = file_path

                while self.current_report_offset < file_size:
                    print(".", end="")
                    package = request.gen_report_download("%s/%s.zip" % (prex, file_name),
                                                          self.current_report_offset).generate()
                    yield package

                print(", 更新完毕!")

            else:
                print("无变化, 不需要更新!")

        self.close()


    def handle_connect(self):
        print("开始连接...")
        req = request.gen_report_download("")
        self.add_handler(req.event_id, self.on_report_list)
        self.send(request.gen_report_download("tdxfin/gpcw.txt").generate())

    def handle_read(self):
        super(TdxReportClient, self).handle_read()

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
