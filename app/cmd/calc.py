import click
import time
import pandas as pd
import pymongo

from app.comm.utils import number
from app.models import MongoDBClient
from app.service.stocks import index
from configure import config


@click.group()
def calc():
    """更新类功能集合"""
    pass

@calc.command(help="计算整个A股的估值信息")
def a():
    """计算A股PE中值"""
    click.echo("开始计算整个A股的估值信息...")
    first = True
    result_list = []
    db_client = MongoDBClient(config.get("db").get("mongodb"), config.get("db").get("database"))


    calendar_df = pd.read_csv(config.get("files").get("calendar"), header=0)
    today = int("".join(time.strftime('%Y%m%d', time.localtime(time.time()))))

    try:
        stock_df = pd.read_csv(config.get("files").get("stock_a"), header=0, encoding="utf8")
        if len(stock_df) > 0:
            first = False
            item_last = stock_df.loc[stock_df.index[-1]]

            calendar_df = calendar_df[calendar_df["calendarDate"] > int(item_last["date"])]

    except FileNotFoundError:
        pass

    for _, row in calendar_df.iterrows():
        cal_date = int(row["calendarDate"])
        if row['isOpen'] == 0 or 20020328 > cal_date or cal_date > today:
            continue

        stock_day_list = db_client.find_stock_list(_filter={"date": str(cal_date), "fixed": {"$exists": True}},
                                                   _sort=[("code", pymongo.ASCENDING)],
                                                   _fields={"market": 1, "code": 1, "close": 1,
                                                            "pe_ttm": 1, "pb": 1, "roe": 1, "dr": 1})

        stock_df = pd.DataFrame(stock_day_list, columns=['market', 'code', 'close', 'pe_ttm', 'pb', 'roe', 'dr'])
        stock_df = stock_df.fillna(0)

        pe_list = []
        pb_list = []
        roe_list = []
        dr_list = []
        for _, r in stock_df.iterrows():
            pe_list.append(r['pe_ttm'])
            pb_list.append(r['pb'])
            roe_list.append(r['roe'])
            dr_list.append(r['dr'])

        mid_value_pe = number.get_median(pe_list)
        mid_value_pb = number.get_median(pb_list)
        avg_value_roe = number.get_average(roe_list)
        avg_value_dr = number.get_average(dr_list)
        click.echo("计算 %s 日的数据中值, pe=%f, pb=%f, roe=%f, dr=%f ... " %
                   (cal_date, mid_value_pe, mid_value_pb, avg_value_roe, avg_value_dr))

        result_list.append([cal_date, mid_value_pe, mid_value_pb, avg_value_roe, avg_value_dr])

        if len(result_list) % 50 == 0:
            if first:
                first = False

                result_df = pd.DataFrame(result_list, columns=['date', 'pe', 'pb', 'roe', 'dr'])
                result_df.to_csv(config.get("files").get("stock_a"), index=False,
                                        mode="w", header=True, encoding='utf8', float_format="%.6f")
            else:
                result_df = pd.DataFrame(result_list, columns=['date', 'pe', 'pb', 'roe', 'dr'])
                result_df.to_csv(config.get("files").get("stock_a"), index=False,
                                        mode="a+", header=False, encoding='utf8', float_format="%.6f")

            result_list = []

    result_df = pd.DataFrame(result_list, columns=['date', 'pe', 'pb', 'roe', 'dr'])
    result_df.to_csv(config.get("files").get("stock_a"), index=False,
                     mode="a+", header=False, encoding='utf8', float_format="%.6f")


def _indexes(idx_market, idx_code, start_date, calendar_df):
    db_client = MongoDBClient(config.get("db").get("mongodb"), config.get("db").get("database"))

    today = int("".join(time.strftime('%Y%m%d', time.localtime(time.time()))))
    item_last = db_client.find_stock_item(_filter={"code": idx_code, "market": idx_market, "dr": {"$exists": True}},
                                          _sort=[("date", pymongo.DESCENDING)])

    if item_last is not None and len(item_last) > 0:
        calendar_df = calendar_df[calendar_df["calendarDate"] > int(item_last.get("date"))]

    click.echo("\t开始 %s 指数的估值信息..." % idx_code)
    for _, row in calendar_df.iterrows():
        cal_date = int(row["calendarDate"])
        if row['isOpen'] == 0 or cal_date < start_date or cal_date > today:
            continue

        click.echo("\t\t计算%d-%s - %d ..." % (idx_market, idx_code, cal_date))
        _result = index.index_val(cal_date, idx_code, db_client)

        if _result is not None:
            db_client.upsert_one(_filter={"code": str(idx_code), "market": idx_market, "date": str(cal_date)},
                                 _value={"pe_ttm": _result[0], "pb": _result[1], "roe": _result[2],
                                         "dr": _result[3]})
    click.echo("\t%s 指数的估值信息计算完毕" % idx_code)


@calc.command(help="计算各指数的估值信息")
@click.option('--code', type=click.STRING, default=None, help='是否更新全量数据, 默认只更新当前季度')
def indexes(code):
    idx_list = config.get("indexes")

    try:
        calendar_df = pd.read_csv(config.get("files").get("calendar"), header=0)

        if code is not None:
            for item in idx_list:
                if item[1] != code:
                    continue
                _indexes(item[0], item[1], item[2], calendar_df)
                return

        for item in idx_list:
            _indexes(item[0], item[1], item[2], calendar_df)

    except FileNotFoundError:
        pass
