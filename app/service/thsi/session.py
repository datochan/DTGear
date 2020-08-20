import random as rd
import time

from app.comm.utils import number, netbase


class C10JQKASession(object):
    def __init__(self):
        self.R = {}
        self.A = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
        self.data = [1450088886,  # 随机数
                     1518154760,  # 服务器时间(单独更新)
                     1518265962,  # 当前时间(单独更新)
                     518136465,  # navigator.userAgent strhash
                     7, 10, 4, 0, 0, 0, 0, 0, 0, 3756, 0, 0, 2, 2]
        self.basic_fields = [4, 4, 4, 4, 1, 1, 1, 3, 2, 2, 2, 2, 2, 2, 2, 4, 2, 1]

        for idx in range(0, 64):
            self.R[self.A[idx]] = idx

    @staticmethod
    def checksum(n: bytearray):
        t = e = 0

        while True:
            if len(n) <= e:
                break
            t = (t << 5) - t + n[e]
            e += 1

        return t & 255

    @staticmethod
    def random():
        return rd.random() * 4294967295.0

    @staticmethod
    def s(data: bytearray, idx: int, cs: int):
        out = bytearray()
        count = len(data)
        while count > idx:
            out.append(data[idx] ^ cs & 255)
            t1 = number.int2byte(cs * 131)
            cs = 0xff & (~t1)  # 由于python没有无符号数，所以需要自己转换
            idx += 1

        return out

    def __encode(self, o: bytearray):
        idx = 0
        result_list = bytearray()
        while len(o) > idx:
            m1 = o[idx] << 16
            idx += 1

            m2 = 0
            if len(o) > idx:
                m2 = o[idx] << 8
                idx += 1

            m3 = 0
            if len(o) > idx:
                m3 = o[idx]
                idx += 1

            m = m1 | m2 | m3
            result_list.append(ord(self.A[m >> 18]))
            result_list.append(ord(self.A[m >> 12 & 63]))
            result_list.append(ord(self.A[m >> 6 & 63]))
            result_list.append(ord(self.A[m & 63]))

        return result_list.decode()

    def encode(self):
        data = self.to_buffer()
        t = self.checksum(data)
        tmp = self.s(data, 0, t)
        result = bytearray()
        result.append(2)
        result.append(t)
        result.extend(tmp)
        return self.__encode(result)

    def to_buffer(self):
        result = bytearray()
        idx = 0
        field_count = len(self.basic_fields)
        while idx < field_count:
            item_data = self.data[idx]
            item_field = self.basic_fields[idx]
            tmp_buffer = bytearray(item_field)

            field_idx = item_field - 1
            while item_field > 0:
                tmp_buffer[field_idx] = item_data & 255
                item_data >>= 8
                item_field -= 1
                field_idx -= 1

            result.extend(tmp_buffer)
            idx += 1

        return result

    def update_server_time(self, time_url: str):
        """更新服务器时间"""
        time_stamp = int(time.time())

        http_client = netbase.HttpClient(time_url % (time_stamp / 1200))
        # var TOKEN_SERVER_TIME=1541343609.223;// server time
        content = http_client.value().decode("utf-8")
        content = content.split('=')[1]
        server_time = float(content.split(';')[0])

        _random = int(self.random())
        self.data[0] = _random
        self.data[1] = int(server_time)
        self.data[2] = int(time_stamp)
