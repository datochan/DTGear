"""

"""
import struct


class Buffer:
    """

    """
    def __init__(self, data:bytes=b""):
        self.__buffer = data

    def length(self):
        """
        获取缓冲区内容的长度
        :return:
        """
        return len(self.__buffer)

    def write_bytes(self, buf):
        self.__buffer += buf

    def bytes(self):
        return self.__buffer

    def read_bytes(self, size):
        """
        从缓存中读取指定长度的内容(读取的内容从缓存中移除)
        :param size:
        :return:
        """
        if len(self.__buffer) >= size:
            result = self.__buffer[:size]
            self.__buffer = self.__buffer[size:]
            return result

        return None

    def peek_bytes(self, size):
        """
        从缓存中读取指定长度的内容(读取的内容继续保留在缓存中)
        :param size:
        :return:
        """
        if len(self.__buffer) >= size:
            return self.__buffer[:size]

        return None

    def read_format(self, fmt:str):
        """
        按照指定格式读取指定长度内容
        :param fmt:
        :return:
        """
        read_size = struct.calcsize(fmt)
        if len(self.__buffer) >= read_size:
            result = self.__buffer[:read_size]
            self.__buffer = self.__buffer[read_size:]
            return struct.unpack(fmt, result)

        return None

    def write_format(self, fmt:str, *args):
        """
        todo 多参，待完成
        按照指定格式写入内容
        :param fmt:
        :return:
        """
        self.__buffer += struct.pack(fmt, args)