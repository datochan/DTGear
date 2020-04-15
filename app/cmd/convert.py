import click
import pymongo
import pandas as pd

from app import comm
from app.comm import stocks
from app.models import MongoDBClient
from configure import PROJECT_ROOT, config
from app.service.stocks import report as rt, bonus


@click.group()
def convert():
    """更新类功能集合"""
    pass

@convert.command(help="转换股票财报数据的指标")
def report():
    """
    转换PE、PB、ROE、股息率 四个指标需要的信息
    1.基本每股收益、4.每股净资产、96.归属于母公司所有者的净利润、238.总股本、239.已上市流通A股
        PE=股价/利润
        PB=股价/每股净资产
        ROE=利润/每股净资产
        因此：PB=PE*ROE
        总市值=当前股价×总股本
    """
    click.echo("转换股票财报数据的指标...")

    all_date_list = []
    file_list = comm.file_list_in_path("%s/data/reports/" % PROJECT_ROOT)

    for file_name in file_list:
        if file_name.startswith(".") or file_name.startswith("rt"):
            continue

        file_name = file_name.split('.')[0]
        ymd_str = file_name[4:]
        all_date_list.append(ymd_str)

    all_date_list.sort()

    is_first = True
    for date_item in all_date_list:

        click.echo("\t开始转换 %s 的财报数据..." % date_item)
        report_list = []
        report_df = stocks.report_list(_date=date_item)

        for idx, row in report_df.iterrows():
            market = stocks.market_with_code(row['code'])
            act = stocks.report_publish_time(row['date'], row['code'])
            report_list.append([row['date'], market, row['code'], row[1], row[2], row[4], row[6], row[72], row[96], row[238], row[239], act])

        # date, market, code, 1.基本每股收益、2.扣非每股收益、4.每股净资产、6.净资产收益率(roa)、72.所有者权益（或股东权益）合计、96.归属于母公司所有者的净利润、
        # 238.总股本、239.已上市流通A股、披露时间
        result_df = pd.DataFrame(report_list, columns=['date', 'market', 'code', 'eps', 'neps', 'bps', 'roe', 'na', 'np', 'tcs', 'ccs', "publish"])

        result_df = result_df.sort_values(['code'], ascending=1)
        if is_first is True:
            result_df.to_csv(config.get("files").get("reports"), index=False, header=True, mode='w',
                             encoding='utf8')
            is_first = False
        else:
            result_df.to_csv(config.get("files").get("reports"), index=False, header=False, mode='a+',
                             encoding='utf8')
    click.echo("股票财报数据转换完毕...")


@convert.command(help="计算后复权价")
def fixed():
    db_client = MongoDBClient(config.get("db").get("mongodb"), config.get("db").get("database"))

    base_df = stocks.stock_a_list()
    bonus_df = bonus.bonus_with(None)

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
                    prev_fixed_close = item_last["fixed"]

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
                db_client.upsert_one(_filter={"code": str(row["code"]), "market": row["market"], "date": str(item["date"])},
                                     _value={"fixed": prev_fixed_close})

        except FileNotFoundError as ex:
            continue


@convert.command(help="更新ST信息")
def st():
    db_client = MongoDBClient(config.get("db").get("mongodb"), config.get("db").get("database"))

    st_df = pd.read_csv(config.get("files").get("st"), header=0)
    st_df['ticker'] = st_df['ticker'].map(lambda x: str(x).zfill(6))

    for index, row in st_df.iterrows():
        _date = str(row["tradeDate"]).replace('-', '')
        _market = 0
        if str(row["exchangeCD"]) == "XSHG":
            _market = 1

        db_client.upsert_one(_filter={"code": str(row["ticker"]), "market": _market, "date": _date},
                             _value={"st": 1, "name": "%s"%row['tradeAbbrName']}, _upsert=False)
        print("更新记录: %d" % index)

@convert.command(help="转换 PE、PB、ROE 指标")
def pe_pb_roe():
    """

    转换PE、PB、ROE、股息率 四个指标需要的信息
    1.基本每股收益、4.每股净资产、96.归属于母公司所有者的净利润、238.总股本、239.已上市流通A股
        PE=股价/每股收益
        PB=股价/每股净资产
        ROE=利润/每股净资产=PB/PE : 财报中已有静态的净资产收益率数据, 这里通过TTM计算一个大概的ROE作为参考
    :return:
    """
    db_client = MongoDBClient(config.get("db").get("mongodb"), config.get("db").get("database"))

    base_df = stocks.stock_a_list()

    for index, row in base_df.iterrows():
        try:
            print("计算 %d-%s 的PE、PB、ROE数据..." % (row["market"], row["code"]))

            stock_day_list = db_client.find_stock_list(_filter={"code": row['code'], "market": row["market"],
                                                                "close": {"$exists": True}},
                                                       _sort=[("date", pymongo.ASCENDING)],
                                                       _fields={"date":1, "close":1})
            if len(stock_day_list) <= 0:
                # 股票本身没有交易量
                continue

            stock_day_df = pd.DataFrame(stock_day_list, columns=['date', 'close'])

            item_last = db_client.find_stock_item(_filter={"code": row['code'], "market": row["market"],
                                                           "pb": {"$exists": True}},
                                                  _sort=[("date", pymongo.DESCENDING)])

            if item_last is not None and len(item_last) > 0:
                # 如果之前计算过，则无需重头计算
                last_day_df = stock_day_df[stock_day_df["date"] == item_last['date']]
                stock_day_df = stock_day_df[stock_day_df.index > last_day_df.index.values[0]]

            for idx, item in stock_day_df.iterrows():
                lyr_value = rt.lyr_with(int(item["date"]), row['code'], item["close"])
                pe_value = rt.ttm_with(int(item["date"]), row['code'], item["close"])
                pb_value = rt.pb_with(int(item["date"]), row['code'], item["close"])
                roe_value = 0.0
                if pe_value != 0.0:
                    roe_value = pb_value / pe_value
                db_client.upsert_one(_filter={"code": str(row["code"]), "market": row["market"], "date": str(item["date"])},
                                     _value={"lyr": lyr_value, "pe_ttm": pe_value, "pb": pb_value,
                                             "roe": roe_value})

        except FileNotFoundError as ex:
            continue


@convert.command(help="转换 流通市值、总市值、股息率")
def mv():
    """
        总市值=当前股价×总股本
    """
    click.echo("计算总股本、流通股本、流通市值、总市值、股息率...")

    db_client = MongoDBClient(config.get("db").get("mongodb"), config.get("db").get("database"))

    base_df = stocks.stock_a_list()
    bonus_df = bonus.bonus_with(None)

    report_df = pd.read_csv(config.get("files").get("reports"), header=0, encoding="utf8")
    report_df['code'] = report_df['code'].map(lambda x: str(x).zfill(6))

    for index, row in base_df.iterrows():
        try:
            print("计算 %d-%s 的股本、市值、股息率" % (row["market"], row["code"]))

            ccs = 0  # 流通股
            tcs = 0  # 总股本

            stock_day_list = db_client.find_stock_list(_filter={"code": row['code'], "market": row["market"],
                                                                "close": {"$exists": True}},
                                                       _sort=[("date", pymongo.ASCENDING)],
                                                       _fields={"date":1, "close":1})
            if len(stock_day_list) <= 0:
                # 股票本身没有交易量
                continue

            stock_day_df = pd.DataFrame(stock_day_list, columns=['date', 'close'])

            try:
                item_last = db_client.find_stock_item(_filter={"code": row['code'], "market": row["market"],
                                                               "dr": {"$exists": True}},
                                                      _sort=[("date", pymongo.DESCENDING)])

                if item_last is not None and len(item_last) > 0:
                    # 如果之前计算过，则无需重头计算
                    last_day_df = stock_day_df[stock_day_df["date"] == item_last['date']]
                    stock_day_df = stock_day_df[stock_day_df.index > last_day_df.index.values[0]]

                    ccs = item_last["cmv"] // item_last["close"]  # 流通股
                    tcs = item_last["tmv"] // item_last["close"]  # 总股本

            except FileNotFoundError as ex:
                pass

            filter_bonus_df = bonus_df[(bonus_df["code"] == row["code"]) & (bonus_df["type"] != 6) &
                                       ((bonus_df["type"] > 1) & (bonus_df["type"] < 13))]
            filter_bonus_df = filter_bonus_df.sort_values(['date'], ascending=True)

            filter_report_df = report_df[report_df["code"] == row["code"]]
            filter_report_df = filter_report_df.sort_values(['date'], ascending=True)

            for idx, item in stock_day_df.iterrows():
                item_df = filter_bonus_df[filter_bonus_df["date"] == int(item["date"])]
                if len(item_df) > 0:
                    # 高送转中记录的数据单位都到万
                    ccs = item_df.ix[item_df.index.values[0]]["count"]*10000
                    tcs = item_df.ix[item_df.index.values[0]]["rate"]*10000

                item_df = filter_report_df[filter_report_df["publish"] == int(item["date"])]
                if len(item_df) > 0:
                    ccs = item_df.ix[item_df.index.values[0]]["ccs"]
                    tcs = item_df.ix[item_df.index.values[0]]["tcs"]

                ccs_mv = item["close"] * ccs
                tcs_mv = item["close"] * tcs
                # 3年的股息率
                dr = bonus.dividend_rate_with(int(item["date"]), row["code"], item["close"])

                db_client.upsert_one(_filter={"code": str(row["code"]), "market": row["market"], "date": str(item["date"])},
                                     _value={"cmv": ccs_mv, "tmv": tcs_mv, "dr": dr})

        except FileNotFoundError as ex:
            continue

    click.echo("总股本、流通股本、流通市值、总市值、股息率 计算完毕...")

