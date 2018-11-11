import click
import pandas as pd
import pymongo

from app.comm import stocks
from app.models import MongoDBClient
from app.service.stocks import report
from configure import PROJECT_ROOT, config


@click.group()
def calc():
    """更新类功能集合"""
    pass


@calc.command(help="计算后复权价")
def fixed():
    db_client = MongoDBClient("mongodb://localhost:27017/", "DTGear")

    base_df = stocks.stock_a_list()
    bonus_df = pd.read_csv(config.get("files").get("bonus"), header=0, encoding="utf8")
    bonus_df['code'] = bonus_df['code'].map(lambda x: str(x).zfill(6))

    for index, row in base_df.iterrows():
        try:
            prev_close = 0
            prev_fixed_close = 0

            print("计算 %d-%s 的后复权数据" % (row["market"], row["code"]))

            stock_day_list = db_client.find_stock_list(_filter={"code": row['code'], "market": row["market"]},
                                                       _sort=[("date", pymongo.ASCENDING)],
                                                       _fields={"date":1, "close":1})
            if len(stock_day_list) <= 0:
                # 股票本身没有交易量无需复权
                continue

            stock_day_df = pd.DataFrame(stock_day_list, columns=['date', 'close'])

            try:
                item_last = db_client.find_stock_item(_filter={"code": row['code'], "market": row["market"],
                                                               "fixed": {"$exists": True}},
                                                      _sort=[("date", pymongo.DESCENDING)])

                if item_last is not None and len(item_last) > 0:
                    # 如果之前计算过后复权价，则无需重头计算
                    last_day_df = stock_day_df[stock_day_df["date"] == item_last['date']]

                    prev_close = last_day_df.ix[last_day_df.index.values[0]]["close"]
                    prev_fixed_close = item_last["close"]

                    stock_day_df = stock_day_df[stock_day_df.index > last_day_df.index.values[0]]

            except FileNotFoundError as ex:
                # 如果从来没计算过后复权价则不管
                pass

            filter_df = bonus_df[(bonus_df["type"] == 1) & (bonus_df["code"] == row["code"])]
            filter_df = filter_df.sort_values(['date'], ascending=True)
            for idx, item in stock_day_df.iterrows():
                money = 0  # 分红
                count = 0  # 送股数

                item_df = filter_df[filter_df["date"] == int(item["date"])]
                if len(item_df) > 0:
                    money = item_df.ix[item_df.index.values[0]]["money"] / 10
                    count = item_df.ix[item_df.index.values[0]]["count"] / 10

                # 除息除权日当天复权后的涨幅 =（当天不复权收盘价 *（1 + 每股送股数量）+每股分红金额） / 上一个交易日的不复权收盘价
                # 复权收盘价 = 上一个交易日的复权收盘价 *（1 + 复权涨幅)
                if prev_close > 0:
                    daily_rate_close = (item["close"] * (1 + count) + money) / prev_close
                    prev_fixed_close = prev_fixed_close * daily_rate_close

                else:
                    prev_fixed_close = item["close"]

                prev_close = item["close"]
                db_client.upsert_one(_market=row["market"], _code=row["code"], _date=item["date"],
                                     _value={"fixed": prev_fixed_close})

        except FileNotFoundError as ex:
            continue


@calc.command(help="计算PE、PB、ROE")
def pe_pb_roe():
    """

    转换PE、PB、ROE、股息率 四个指标需要的信息
    1.基本每股收益、4.每股净资产、96.归属于母公司所有者的净利润、238.总股本、239.已上市流通A股
        PE=股价/每股收益
        PB=股价/每股净资产
        ROE=利润/每股净资产
        因此：PB=PE*ROE
    :return:
    """
    db_client = MongoDBClient("mongodb://localhost:27017/", "DTGear")

    base_df = stocks.stock_a_list()

    for index, row in base_df.iterrows():
        try:
            print("计算 %d-%s 的PE、PB、ROE数据..." % (row["market"], row["code"]))

            stock_day_list = db_client.find_stock_list(_filter={"code": row['code'], "market": row["market"]},
                                                       _sort=[("date", pymongo.ASCENDING)],
                                                       _fields={"date":1, "close":1})
            if len(stock_day_list) <= 0:
                # 股票本身没有交易量无需复权
                continue

            stock_day_df = pd.DataFrame(stock_day_list, columns=['date', 'close'])

            item_last = db_client.find_stock_item(_filter={"code": row['code'], "market": row["market"],
                                                           "pb": {"$exists": True}},
                                                  _sort=[("date", pymongo.DESCENDING)])

            if item_last is not None and len(item_last) > 0:
                # 如果之前计算过后复权价，则无需重头计算
                last_day_df = stock_day_df[stock_day_df["date"] == item_last['date']]
                stock_day_df = stock_day_df[stock_day_df.index > last_day_df.index.values[0]]

            for idx, item in stock_day_df.iterrows():
                lyr_value = report.lyr_with(int(item["date"]), row['code'], item["close"])
                pe_value = report.pe_ttm_with(int(item["date"]), row['code'], item["close"])
                pb_value = report.pb_with(int(item["date"]), row['code'], item["close"])
                roe_value = 0.0
                if pe_value != 0.0:
                    roe_value = pb_value / pe_value
                print("\t %s-%s" % (row["code"], int(item["date"])))
                db_client.upsert_one(_market=row["market"], _code=row["code"], _date=item["date"],
                                     _value={"lyr": lyr_value, "pe_ttm": pe_value, "pb": pb_value,
                                             "roe": roe_value})

        except FileNotFoundError as ex:
            continue


@calc.command(help="计算总股本、流通股本、流通市值、总市值、股息率")
def mv():
    """
        总市值=当前股价×总股本
    """
    click.echo("计算总股本、流通股本、流通市值、总市值、股息率...")

    db_client = MongoDBClient("mongodb://localhost:27017/", "DTGear")

    base_df = stocks.stock_a_list()
    bonus_df = pd.read_csv(config.get("files").get("bonus"), header=0, encoding="utf8")
    bonus_df['code'] = bonus_df['code'].map(lambda x: str(x).zfill(6))

    for index, row in base_df.iterrows():
        try:
            prev_close = 0
            prev_fixed_close = 0

            print("计算 %d-%s 的后复权数据" % (row["market"], row["code"]))

            stock_day_list = db_client.find_stock_list(_filter={"code": row['code'], "market": row["market"]},
                                                       _sort=[("date", pymongo.ASCENDING)],
                                                       _fields={"date":1, "close":1})
            if len(stock_day_list) <= 0:
                # 股票本身没有交易量无需复权
                continue

            stock_day_df = pd.DataFrame(stock_day_list, columns=['date', 'close'])

            try:
                item_last = db_client.find_stock_item(_filter={"code": row['code'], "market": row["market"],
                                                               "fixed": {"$exists": True}},
                                                      _sort=[("date", pymongo.DESCENDING)])

                if item_last is not None and len(item_last) > 0:
                    # 如果之前计算过后复权价，则无需重头计算
                    last_day_df = stock_day_df[stock_day_df["date"] == item_last['date']]

                    prev_close = last_day_df.ix[last_day_df.index.values[0]]["close"]
                    prev_fixed_close = item_last["close"]

                    stock_day_df = stock_day_df[stock_day_df.index > last_day_df.index.values[0]]

            except FileNotFoundError as ex:
                # 如果从来没计算过后复权价则不管
                pass

            filter_df = bonus_df[(bonus_df["type"] == 1) & (bonus_df["code"] == row["code"])]
            filter_df = filter_df.sort_values(['date'], ascending=True)
            for idx, item in stock_day_df.iterrows():
                money = 0  # 分红
                count = 0  # 送股数

                item_df = filter_df[filter_df["date"] == int(item["date"])]
                if len(item_df) > 0:
                    money = item_df.ix[item_df.index.values[0]]["money"] / 10
                    count = item_df.ix[item_df.index.values[0]]["count"] / 10

                # 除息除权日当天复权后的涨幅 =（当天不复权收盘价 *（1 + 每股送股数量）+每股分红金额） / 上一个交易日的不复权收盘价
                # 复权收盘价 = 上一个交易日的复权收盘价 *（1 + 复权涨幅)
                if prev_close > 0:
                    daily_rate_close = (item["close"] * (1 + count) + money) / prev_close
                    prev_fixed_close = prev_fixed_close * daily_rate_close

                else:
                    prev_fixed_close = item["close"]

                prev_close = item["close"]
                db_client.upsert_one(_market=row["market"], _code=row["code"], _date=item["date"],
                                     _value={"fixed": prev_fixed_close})

        except FileNotFoundError as ex:
            continue



    click.echo("总股本、流通股本、流通市值、总市值、股息率 计算完毕...")

