"""
    client
    ~~~~~~~~~~~~~~
    数据传输对象, 用于封装通达信的请求和应答包

    :copyright: (c) 16/11/26 by datochan.
"""
import asyncore
from datetime import datetime
import struct
import time

import pandas as pd
import pymongo

from app import models
from app.comm import stocks, date
from app.comm.utils.bytes import Buffer
from app.service.tdx import request
from app.service.tdx.proxy import TdxProxy, EVENT_READY
from app.service.tdx.response import ResponseHeader, ResponseStockBase, ResponseStockBonus, ResponseStockDays
from configure import config


class TdxClient:
    """用于数据更新和抓取的客户端"""
    __db_client:models.MongoDBClient
    def __init__(self, db_client=None, callback=None):
        self.proxy = TdxProxy()
        self.__callback_proc = callback
        self.__db_client = db_client

        """注册事件响应函数"""
        self.proxy.add_handler(EVENT_READY, self.ready)

        self.bonus_idx = 0                 # 用于记录高送转的更新数量
        self.data_day = pd.DataFrame()     # 日线数据
        self.data_last_stock = None        # 最后一条股票代码，用来判断更新日线和5分钟线是否结束
        try:
            self.data_gen = None
            # 基础市场数据
            self.data_stocks = pd.DataFrame([], columns=['code', 'name', 'market', 'unknown1', 'unknown2',
                                                             'unknown3', 'price', 'bonus1', 'bonus2'])
            self.data_bonus = pd.DataFrame([], columns=["code", "date", "market", "type", "money",
                                                            "price", "count", "rate"])

        except FileNotFoundError:
            print("请先更新股票基础数据!")
            exit()

    def ready(self):
        self.proxy.del_handler(EVENT_READY)

        if self.__callback_proc is not None:
            self.__callback_proc()

    def update_base(self):
        """
        用于更新基础数据信息
        注意，要调用此方法，必须要先获取一次服务器公告
        :return:
        """
        print("开始更新深市基础数据...")

        idx = 0
        req = request.gen_stock_base(0, idx)
        self.proxy.add_handler(req.event_id, self.on_base)

        # 更新深市股票列表信息
        while idx < self.proxy.stock_sz_count:
            req = request.gen_stock_base(0, idx)
            idx += 0x03E8
            package = req.generate()

            yield package

        # 更新沪市股票列表信息
        print("开始更新沪市基础数据...")
        idx = 0
        while idx < self.proxy.stock_sh_count:
            req = request.gen_stock_base(1, idx)
            idx += 0x03E8

            package = req.generate()
            yield package


    def update_bonus(self):
        """
        更新高送转数据
        :return:
        """
        try:
            if self.bonus_idx <= 0:
                print("开始更新高送转数据")
            idx = 0
            req = request.gen_stock_bonus(b"", idx)
            self.proxy.add_handler(req.event_id, self.on_stock_bonus)

            filter_df = self.data_stocks[self.data_stocks['bonus2'] > 0]
            # filter_df = filter_df.sort_values(['market'], ascending=1)
            filter_df = filter_df.reset_index().drop(["index"], axis=1)
            filter_df = filter_df[filter_df.index >= self.bonus_idx]

            total = 0
            idx = 0
            content = bytearray()
            for index, row in filter_df.iterrows():
                if idx < 0xC8:
                    idx += 1
                    total += 1
                    content += bytearray(struct.pack("<B7s", row["market"],
                                                     str(row["code"]).zfill(6).encode("ascii")))[:7]
                    continue
                # 7*0xc8 = 1400
                # 0C 75 18 76 00 01 7C 05 7C 05 0F 00 C8 00 00 30 30 30 30 30 31 ...
                req = request.gen_stock_bonus(content, 0)
                self.proxy.send(req.generate())
                return

            if idx > 0:
                # 0C 75 18 76 00 01 7C 05 7C 05 0F 00 C8 00 00 30 30 30 30 30 31 ...
                req = request.gen_stock_bonus(content, 0x1100)
                self.proxy.send(req.generate())

        except FileNotFoundError as ex:
            print("请先更新股票基础资料，再更新权息数据...")

        except Exception as ex:
            print("更新股票权息数据时发生异常，错误信息为: %s" % ex)


    def update_history(self):
        """
        更新日线数据
        :return:
        """
        try:
            req = request.gen_stock_days(0, "", 0, 0, 0)
            self.proxy.add_handler(req.event_id, self.on_history)

            df = stocks.all_list_except_bond()
            self.data_stocks = df.sort_index(ascending=1)
            end = int("".join(time.strftime('%Y%m%d', time.localtime(time.time()))))

            _is_work_day = date.is_work_day(end)
            if _is_work_day is None:
                print("股市交易日历发生错误，请更新股市交易日历后再重试!")
                return

            if _is_work_day is True:
                # 是交易日, 需要在当日3点半之后再执行
                _cur_time = int(time.time())
                _target_time = int(time.mktime(time.strptime('%s 15:00:00' % str(datetime.now())[0:10], '%Y-%m-%d %H:%M:%S')))
                if _cur_time < _target_time:
                    # 如果当前交易还未结束则更新到上一个交易日
                    end = date.prev_day(end)

            for index, row in self.data_stocks.iterrows():
                stock_code = str(row["code"]).zfill(6)

                start = 19901219
                item = self.__db_client.find_stock_item({"code": stock_code, "market": row["market"]},
                                                        _sort=[("date", pymongo.DESCENDING)])
                if item is not None:
                    start = int(item.get("date", 19901219))
                    start = date.next_day(start)

                tmp_start = start
                tmp_end = 0

                while tmp_end != end:
                    if tmp_start+40000 > end:
                        tmp_end = end
                    else:
                        tmp_end = tmp_start+40000

                    req = request.gen_stock_days(row["market"], stock_code, tmp_start, tmp_end, index)

                    tmp_start = tmp_end+1
                    package = req.generate()

                    yield package

        except FileNotFoundError as ex:
            print("请先更新股票基础资料，再更新日线数据...")

        except Exception as ex:
            print("更新日线数据时发生未知异常，错误信息为: %s" % str(ex))


    def on_history(self, header:ResponseHeader, body:Buffer):
        """处理日线封包"""
        current_df_list = []
        is_st = 0
        stock_code = self.data_stocks.ix[header.idx]['code']
        stock_name = self.data_stocks.ix[header.idx]['name']
        market = int(self.data_stocks.ix[header.idx]['market'])

        if header.cmd_id != 0x87:
            # 只处理日线数据
            return

        if stock_name.startswith("ST") or stock_name.startswith("SST") or \
                stock_name.startswith("*ST") or stock_name.startswith("S*ST"):
            is_st = 1

        # 日线数据
        item_count =  body.read_format("<HL")[1] / ResponseStockDays.length()

        idx = 0
        while idx < item_count:
            item = ResponseStockDays.parse(body)
            current_df_list.append([item.date, int(market), stock_code, stock_name,
                                    item.open, item.low, item.high, item.close, item.volume, item.amount, is_st])
            idx += 1

        print("获取 %s 的日线数据" % stock_code)


        hs_df = pd.DataFrame(current_df_list, columns=['date', 'market', 'code', 'name', 'open', 'low', 'high', 'close',
                                                       'volume', 'amount', 'st'])

        self.__db_client.insert_json(hs_df)

        self.proxy.send(next(self.data_gen))


    def on_stock_bonus(self, header:ResponseHeader, body:Buffer):
        """处理权息封包"""
        idx = 0
        current_df_list = []
        stocks_count =  body.read_format("<H")[0]
        self.bonus_idx += stocks_count

        while idx < stocks_count:
            idx += 1
            bonus_idx = 0
            body.read_bytes(7)  # 跳过股票代码和市场的字节
            bonus_count = body.read_format("<H")[0]
            while bonus_idx < bonus_count:
                stock_bonus = ResponseStockBonus.parse(body)

                bonus_item = [stock_bonus.code, stock_bonus.date, stock_bonus.market, stock_bonus.type,
                              stock_bonus.money, stock_bonus.price, stock_bonus.count, stock_bonus.rate]
                current_df_list.append(bonus_item)
                bonus_idx += 1

        data_bonus = pd.DataFrame(current_df_list, columns=["code", "date", "market", "type", "money",
                                                            "price", "count", "rate"])
        self.data_bonus = pd.concat([self.data_bonus, data_bonus], ignore_index=True)

        print("收到 %d 只股票的高送转信息." % stocks_count)
        if header.idx == 0x1100:
            print("保存权息数据")
            self.data_bonus.to_csv(config.get("files").get("bonus"), index=False, mode="w", encoding='utf8',
                                   float_format="%.6f")
            # 数据更新完毕, 解除事件绑定
            self.bonus_idx = 0
            self.proxy.del_handler(header.event_id)
            print("权息数据更新完毕")
            self.proxy.close()
        else:
            self.update_bonus()


    def on_base(self, header:ResponseHeader, body:Buffer):
        """更新市场股票基础信息列表"""
        idx = 0
        current_df_list = []

        market_type = 0 if header.cmd_id == 0x6D else 1      # 0表示深市，1表示沪市
        stocks_count =  body.read_format("<H")[0]
        while idx < stocks_count:
            obj_stock_base = ResponseStockBase.parse(body)

            stock_item = [obj_stock_base.code, obj_stock_base.name, market_type,
                          obj_stock_base.unknown1, obj_stock_base.unknown2, obj_stock_base.unknown3,
                          obj_stock_base.price, obj_stock_base.bonus1, obj_stock_base.bonus2]

            current_df_list.append(stock_item)
            idx += 1

        data_stocks = pd.DataFrame(current_df_list, columns=['code', 'name', 'market', 'unknown1', 'unknown2',
                                                             'unknown3', 'price', 'bonus1', 'bonus2'])
        self.data_stocks = pd.concat([self.data_stocks, data_stocks], ignore_index=True)

        if len(self.data_stocks) >= (self.proxy.stock_sz_count+self.proxy.stock_sh_count):
            # 保存数据信息
            print("保存基础数据...")
            self.data_stocks.to_csv(config.get("files").get("stock_list"),
                                    index=False, mode="w", encoding='utf8', float_format="%.3f")

            # 解绑事件处理器
            self.proxy.del_handler(header.event_id)

            # 开始更新股票权息数据
            self.update_bonus()
            return

        self.proxy.send(next(self.data_gen))

    def connect(self, host=None, port=7190):
        self.proxy.connect(host, port)


if __name__ == "__main__":
    def __update():
        c1.data_gen = c1.update_base()
        c1.proxy.send(next(c1.data_gen))

    c1 = TdxClient(callback=__update)

    c1.connect("121.14.110.200", 443)

    print("**********************start ioloop******************")
    asyncore.loop()
