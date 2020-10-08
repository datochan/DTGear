import click
import pandas as pd
import pymongo

from app.comm import date
from app.models import MongoDBClient
from configure import config, PROJECT_ROOT


@click.group()
def plot():
    """策略执行"""
    pass


@plot.command(help="策略1, 定期定额方式")
@click.option('--years', type=click.INT, default=None, help='定投年限')
@click.option('--money', type=click.FLOAT, default=None, help='每期定投的金额')
def plot1(years, money):
    tax = 0.00025  # 买卖按照万分之2.5计算

    for item in config.get("indexes"):
        _market = item[0]
        _idx_code = item[1]
        _money_per = money
        click.echo("开始计算 %d - %s 指数的回测策略" % (_market, _idx_code))
        _start_date = date.datetime_to_str(date.years_ago(years))
        last_day_list = date.last_days(int(_start_date), 1, True)  # 每月最后一个交易日集合

        data = []
        db_client = MongoDBClient(config.get("db").get("mongodb"), config.get("db").get("database"))

        _idx_list = db_client.find_stock_list(_filter={"code": _idx_code, "market": _market},
                                              _sort=[("date", pymongo.ASCENDING)],
                                              _fields={"date": 1, "close": 1})

        item_df = pd.DataFrame(list(_idx_list), columns=["date", "close"])
        item_df = item_df.dropna(0)

        total_count = int(0)  # 累计数量

        for idx, item_date in enumerate(last_day_list):
            last_df = item_df[item_df["date"] == str(item_date)]
            if last_df is None or len(last_df) <= 0:
                continue

            item_point = last_df.ix[last_df.index.values[0]]["close"]
            item_count = _money_per * (1 - tax) / item_point
            total_count += item_count
            data.append([item_date, "买入", item_point, item_count, total_count])

        item = data.pop(-1)
        item_count = total_count * item[2] * (1 - tax) / item[2]
        data.append([item[0], "卖出", item[2], item_count, 0])
        result_df = pd.DataFrame(data, columns=["日期", "操作", "单价", "数量", "累计数量"])

        result_df.to_csv(config.get("files").get("plots") % (PROJECT_ROOT, "plot1", _market, _idx_code), index=False,
                         mode="w", header=True, encoding='gb18030', float_format="%.3f")


@plot.command(help="策略2, 依据PE高度定期不定额方式")
@click.option('--years', type=click.INT, default=None, help='定投年限')
@click.option('--money', type=click.FLOAT, default=None, help='每期定投的金额')
def plot2(years, money):
    """
    红利指数定投进阶方案
    80% <= pe百分位: 全卖
    60% <= pe百分位 < 80%: 定赎回
    40% <= pe百分位 < 60%: 正常定投
    20% <= pe百分位 < 40%: 1.5倍定投
    pe百分位 < 20%: 2倍定投

    :return:
    """
    tax = 0.00025  # 买卖按照万分之2.5计算

    for item in config.get("indexes"):
        data = []
        _market = item[0]
        _idx_code = item[1]
        _money_per = money

        click.echo("开始计算 %d - %s 指数的回测策略" % (_market, _idx_code))
        _start_date = date.datetime_to_str(date.years_ago(years))
        last_day_list = date.last_days(int(_start_date), 1, True)  # 每月最后一个交易日集合

        db_client = MongoDBClient(config.get("db").get("mongodb"), config.get("db").get("database"))

        _idx_list = db_client.find_stock_list(_filter={"code": _idx_code, "market": _market},
                                              _sort=[("date", pymongo.ASCENDING)],
                                              _fields={"date": 1, "pe_ttm": 1, "close": 1})

        item_df = pd.DataFrame(list(_idx_list), columns=["date", "pe_ttm", "close"])
        item_df = item_df.dropna(0)

        _pe_series = 1 / item_df["pe_ttm"]
        item_df.insert(0, 'rank', _pe_series.rank(pct=True))
        item_df = item_df.reset_index()

        total_count = 0  # 累计数量

        for idx, item_date in enumerate(last_day_list):
            last_df = item_df[item_df["date"] == str(item_date)]
            if last_df is None or len(last_df) <= 0:
                continue

            _tmp_rank = last_df.ix[last_df.index.values[0]]["rank"]
            item_point = last_df.ix[last_df.index.values[0]]["close"]
            item_rank = float("%.2f" % ((1 - _tmp_rank) * 100))

            if item_rank >= 80 and total_count > 0:
                # 全部卖出, 卖出后要扣税费
                item_count = total_count * item_point * (1 - tax) / item_point
                data.append([item_date, item_rank, "卖出", -item_point, item_count, 0])
                total_count = 0

            elif 60 <= item_rank < 80:
                # 卖出1份
                _op = "卖出"
                # 卖出的这一份应该包含税费，所以要多卖出一部分税费的数量
                item_count = _money_per * (1 + tax) / item_point
                if total_count >= item_count:
                    total_count -= item_count
                elif total_count > 0:
                    item_count = total_count
                    total_count = 0
                else:
                    _op = "/"
                    item_count = 0
                    total_count = 0

                data.append([item_date, item_rank, _op, -item_point, item_count, total_count])

            elif 40 <= item_rank < 60:
                # 买入1份
                item_count = _money_per * (1 - tax) / item_point
                total_count += item_count
                data.append([item_date, item_rank, "买入", item_point, item_count, total_count])

            elif 20 <= item_rank < 40:
                # 买入1.5份
                item_count = (_money_per * 1.5) * (1 - tax) / item_point
                total_count += item_count
                data.append([item_date, item_rank, "买入", item_point, item_count, total_count])
            elif 0 <= item_rank < 20:
                # 买入2份
                item_count = (_money_per * 2) * (1 - tax) / item_point
                total_count += item_count
                data.append([item_date, item_rank, "买入", item_point, item_count, total_count])
            else:
                data.append([item_date, item_rank, "/", item_point, 0, total_count])

        result_df = pd.DataFrame(data, columns=["日期", "百分位", "操作", "单价", "数量", "累计数量"])

        result_df.to_csv(config.get("files").get("plots") % (PROJECT_ROOT, "plot2", _market, _idx_code), index=False,
                         mode="w", header=True, encoding='gb18030', float_format="%.3f")


@plot.command(help="策略3, 依据PE高度，盈余均摊到后续投入成本的策略")
@click.option('--years', type=click.INT, default=None, help='定投年限')
@click.option('--money', type=click.FLOAT, default=None, help='每期定投的金额')
def plot3(years, money):
    """
    红利指数定投进阶方案
    80% <= pe百分位: 全卖, 清仓后的盈余均摊到剩余两倍的定投期数中(因为有可能翻倍投入，为避免将子弹打光，所以两倍)
    60% <= pe百分位 < 80%: 定赎回
    40% <= pe百分位 < 60%: 正常定投
    20% <= pe百分位 < 40%: 1.5倍定投
    pe百分位 < 20%: 2倍定投

    :return:
    """
    tax = 0.00025  # 买卖按照万分之2.5计算

    for item in config.get("indexes"):
        data = []
        _market = item[0]
        _idx_code = item[1]
        _money_per = money

        click.echo("开始计算 %d - %s 指数的回测策略" % (_market, _idx_code))
        _start_date = date.datetime_to_str(date.years_ago(years))
        last_day_list = date.last_days(int(_start_date), 1, True)  # 每月最后一个交易日集合

        db_client = MongoDBClient(config.get("db").get("mongodb"), config.get("db").get("database"))

        _idx_list = db_client.find_stock_list(_filter={"code": _idx_code, "market": _market},
                                              _sort=[("date", pymongo.ASCENDING)],
                                              _fields={"date": 1, "pe_ttm": 1, "close": 1})

        item_df = pd.DataFrame(list(_idx_list), columns=["date", "pe_ttm", "close"])
        item_df = item_df.dropna(0)

        _pe_series = 1 / item_df["pe_ttm"]
        item_df.insert(0, 'rank', _pe_series.rank(pct=True))
        item_df = item_df.reset_index()

        total_count = int(0)  # 累计数量
        _month_count = len(last_day_list)

        for idx, item_date in enumerate(last_day_list):
            last_df = item_df[item_df["date"] == str(item_date)]
            if last_df is None or len(last_df) <= 0:
                continue

            _tmp_rank = last_df.ix[last_df.index.values[0]]["rank"]
            item_point = last_df.ix[last_df.index.values[0]]["close"]
            item_rank = float("%.2f" % ((1 - _tmp_rank) * 100))

            if item_rank >= 80 and total_count > 0:
                _wait_amount = item_point * total_count
                _wait_count = (_month_count - (idx + 1))
                if _wait_amount != 0:
                    _money_per += _wait_amount / (_wait_count * 2)

                item_count = total_count * item_point * (1 - tax) / item_point
                data.append([item_date, item_rank, "卖出", -item_point, item_count, 0])
                total_count = 0

            elif 60 <= item_rank < 80:
                # 卖出的这一份应该包含税费，所以要多卖出一部分税费的数量
                _op = "卖出"
                item_count = _money_per * (1 + tax) / item_point
                if total_count >= item_count:
                    total_count -= item_count
                elif total_count > 0:
                    item_count = total_count * item_point * (1 - tax) / item_point
                    total_count = 0
                else:
                    _op = "/"
                    item_count = 0
                    total_count = 0

                data.append([item_date, item_rank, _op, -item_point, item_count, total_count])

            elif 40 <= item_rank < 60:
                # 买入1份
                item_count = _money_per * (1 - tax) / item_point
                total_count += item_count
                data.append([item_date, item_rank, "买入", item_point, item_count, total_count])

            elif 20 <= item_rank < 40:
                # 买入1.5份
                item_count = (_money_per * 1.5) * (1 - tax) / item_point
                total_count += item_count
                data.append([item_date, item_rank, "买入", item_point, item_count, total_count])
            elif 0 <= item_rank < 20:
                # 买入2份
                item_count = (_money_per * 2) * (1 - tax) / item_point
                total_count += item_count
                data.append([item_date, item_rank, "买入", item_point, item_count, total_count])
            else:
                data.append([item_date, item_rank, "/", item_point, 0, total_count])

        result_df = pd.DataFrame(data, columns=["日期", "百分位", "操作", "单价", "数量", "累计数量"])

        result_df.to_csv(config.get("files").get("plots") % (PROJECT_ROOT, "plot3", _market, _idx_code), index=False,
                         mode="w", header=True, encoding='gb18030', float_format="%.3f")


@plot.command(help="策略4, 依据PB高度定期不定额方式")
@click.option('--years', type=click.INT, default=None, help='定投年限')
@click.option('--money', type=click.FLOAT, default=None, help='每期定投的金额')
def plot4(years, money):
    """
    红利指数定投进阶方案
    80% <= pb百分位: 全卖
    60% <= pb百分位 < 80%: 定赎回
    40% <= pb百分位 < 60%: 正常定投
    20% <= pb百分位 < 40%: 1.5倍定投
    pe百分位 < 20%: 2倍定投

    :return:
    """
    tax = 0.00025  # 买卖按照万分之2.5计算

    for item in config.get("indexes"):
        data = []
        _market = item[0]
        _idx_code = item[1]
        _money_per = money

        click.echo("开始计算 %d - %s 指数的回测策略" % (_market, _idx_code))
        _start_date = date.datetime_to_str(date.years_ago(years))
        last_day_list = date.last_days(int(_start_date), 1, True)  # 每月最后一个交易日集合

        db_client = MongoDBClient(config.get("db").get("mongodb"), config.get("db").get("database"))

        _idx_list = db_client.find_stock_list(_filter={"code": _idx_code, "market": _market},
                                              _sort=[("date", pymongo.ASCENDING)],
                                              _fields={"date": 1, "pb": 1, "close": 1})

        item_df = pd.DataFrame(list(_idx_list), columns=["date", "pb", "close"])
        item_df = item_df.dropna(0)

        _pe_series = 1 / item_df["pb"]
        item_df.insert(0, 'rank', _pe_series.rank(pct=True))
        item_df = item_df.reset_index()

        total_count = int(0)  # 累计数量

        for idx, item_date in enumerate(last_day_list):
            last_df = item_df[item_df["date"] == str(item_date)]
            if last_df is None or len(last_df) <= 0:
                continue

            _tmp_rank = last_df.ix[last_df.index.values[0]]["rank"]
            item_point = last_df.ix[last_df.index.values[0]]["close"]
            item_rank = float("%.2f" % ((1 - _tmp_rank) * 100))

            if item_rank >= 80 and total_count > 0:
                item_count = total_count * item_point * (1 - tax) / item_point
                data.append([item_date, item_rank, "卖出", -item_point, item_count, 0])
                total_count = 0

            elif 60 <= item_rank < 80:
                # 卖出1份
                _op = "卖出"
                item_count = _money_per * (1 + tax) / item_point
                if total_count >= item_count:
                    total_count -= item_count
                elif total_count > 0:
                    item_count = total_count
                    total_count = 0
                else:
                    _op = "/"
                    item_count = 0
                    total_count = 0

                data.append([item_date, item_rank, _op, -item_point, item_count, total_count])

            elif 40 <= item_rank < 60:
                # 买入1份
                item_count = _money_per * (1 - tax) / item_point
                total_count += item_count
                data.append([item_date, item_rank, "买入", item_point, item_count, total_count])

            elif 20 <= item_rank < 40:
                # 买入1.5份
                item_count = (_money_per * 1.5) * (1 - tax) / item_point
                total_count += item_count
                data.append([item_date, item_rank, "买入", item_point, item_count, total_count])
            elif 0 <= item_rank < 20:
                # 买入2份
                item_count = (_money_per * 2) * (1 - tax) / item_point
                total_count += item_count
                data.append([item_date, item_rank, "买入", item_point, item_count, total_count])
            else:
                data.append([item_date, item_rank, "/", item_point, 0, total_count])

        result_df = pd.DataFrame(data, columns=["日期", "百分位", "操作", "单价", "数量", "累计数量"])

        result_df.to_csv(config.get("files").get("plots") % (PROJECT_ROOT, "plot4", _market, _idx_code), index=False,
                         mode="w", header=True, encoding='gb18030', float_format="%.3f")
