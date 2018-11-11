# -*- coding:utf-8 -*-

import time
import socket
import platform
import asyncore
from urllib.error import URLError
from urllib.request import urlopen, Request

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

from app.comm.utils import bytes

RECV_BUFFER_SIZE = 65535

class TCPClient(asyncore.dispatcher_with_send):
    def __init__(self, idle_sec=10, interval_sec=5, max_fails=3):
        asyncore.dispatcher_with_send.__init__(self)
        # self.debug = True
        self.in_buffer = bytes.Buffer()
        self.__map_handler = {}         # 注册的处理器
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        if platform.system() == "Linux":
            self.__keepalive_linux(idle_sec, interval_sec, max_fails)
        elif platform.system() == "Darwin":
            self.__keepalive_osx(idle_sec, interval_sec, max_fails)
        else:
            print("未知操作系统平台...")

    def add_handler(self, event, handler):
        """
        绑定指定事件的处理器
        :param event: 事件名, int类型; 0=所有未知事件的处理器
        :param handler: 事件的处理器
        :return:
        """
        self.__map_handler[event] = handler

    def del_handler(self, event):
        """
        解绑指定事件的处理器
        :param event:
        :return:
        """
        if event in self.__map_handler:
            del self.__map_handler[event]

    def get_handler(self, event):
        """
        获取指定事件的处理器
        :param event:
        :return:
        """
        if event in self.__map_handler:
            return self.__map_handler[event]

        return None

    def connect(self, host=None, port=7190):
        """开始连接"""
        print('connect。。。')
        asyncore.dispatcher.connect(self, (host, port))

    def __keepalive_linux(self, after_idle_sec=7200, interval_sec=5, max_fails=3):
        """
        开启心跳包
        :param after_idle_sec: 如果在{after_idle_sec}秒内没有任何数据交互, 则进行探测.缺省值:7200(s)
        :param interval_sec: 探测时发探测包的时间间隔为{interval_sec}秒.缺省值:75(s)
        :param max_fails: 探测重试的次数.全部超时则认定连接失效..缺省值:9(次)
        :return:
        """
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, after_idle_sec)
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, interval_sec)
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, max_fails)

    def __keepalive_osx(self, after_idle_sec=1, interval_sec=3, max_fails=5):
        """
        开启心跳包
        :param after_idle_sec: 如果在60秒内没有任何数据交互, 则进行探测.缺省值:7200(s)
        :param interval_sec: 探测时发探测包的时间间隔为5秒.缺省值:75(s)
        :param max_fails: 探测重试的次数.全部超时则认定连接失效..缺省值:9(次)
        :return:
        """
        # scraped from /usr/include, not exported by python's socket module
        TCP_KEEPALIVE = 0x10
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self.socket.setsockopt(socket.IPPROTO_TCP, TCP_KEEPALIVE, interval_sec)

    def handle_read(self):
        sub_buffer = self.recv(RECV_BUFFER_SIZE)
        if len(sub_buffer) == 0:
            return

        # print("recv %s" % binascii.b2a_hex(sub_buffer))

        self.in_buffer.write_bytes(sub_buffer)

    def handle_error(self):
        self.close()
        print("连接异常终止, 正在重新建立链接...")
        super(TCPClient, self).connect(self.addr)


class HttpClient(object):
    def __init__(self, url=None, ref=None, cookie=None, auth=None, data=None):
        self._ref = ref
        self._token = auth
        self._cookie = cookie
        self._url = url
        self._data = data
        self._set_opener()

    def _set_opener(self):
        request = Request(self._url)
        request.add_header("Accept-Language", "en-US,en;q=0.5")
        request.add_header("Connection", "keep-alive")
        if self._cookie is not None:
            request.add_header("Cookie", self._cookie)
        if self._token is not None:
            request.add_header("Authorization", "Bearer " + self._token)
            # request.add_header("Accept-Encoding", "gzip, deflate")
        if self._ref is not None:
            request.add_header('Referer', self._ref)

        request.add_header("User-Agent", 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 '
                                         '(KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36')
        self._request = request

    def value(self):
        values = urlopen(self._request, data=self._data, timeout=50).read()
        return values


def http_request(url=None, ref=None, cookie=None, auth=None, data=None, retry_count=3, retry_time=10):
    """
    带重试次数的网络请求
    :param url:
    :param ref:
    :param cookie:
    :param auth:
    :param retry_count: 重试多少次
    :param retry_time: 每次重试的时间间隔
    :return:
    """
    idx = 0
    retry = True
    response_content = 0
    while idx < retry_count and retry:
        try:
            dt_client = HttpClient(url, ref=ref, cookie=cookie, auth=auth)
            response_content = dt_client.value()
            retry = False
        except URLError as ex:
            idx += 1
            print("网络请求失败, 等待10秒后重试第 %d 次!" % idx)
            time.sleep(retry_time)

    if retry:
        raise Exception("网络请求出错...")

    return response_content
