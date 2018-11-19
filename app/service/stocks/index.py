import time
import pandas as pd
import pymongo

from configure import PROJECT_ROOT, config

from app.comm.utils import number

INDEX_MEMBER_DF = pd.DataFrame()


def index_val(_date:int, _idx_code:str, _mongo_client=None):
    """
    计算市场及指数在某一天的估值信息
    :param int _date: 某一天
    :param str _idx_code: 指数代码
    :param _mongo_client: mongodb 连接实例
    :return:
    """
    global INDEX_MEMBER_DF
    # 有复权价代表是股票
    stock_day_list = _mongo_client.find_stock_list(_filter={"date": str(_date), "fixed": {"$exists": True}},
                                               _sort=[("code", pymongo.ASCENDING)],
                                               _fields={"market": 1, "code": 1, "close": 1,
                                                        "pe_ttm": 1, "pb": 1, "roe": 1, "dr": 1})

    if len(INDEX_MEMBER_DF) <= 0:
        today = int("".join(time.strftime('%Y%m%d', time.localtime(time.time()))))
        INDEX_MEMBER_DF = pd.read_csv(config.get("files").get("index") % (PROJECT_ROOT, _idx_code), header=0)
        INDEX_MEMBER_DF = INDEX_MEMBER_DF.fillna(today)
        INDEX_MEMBER_DF = INDEX_MEMBER_DF.drop_duplicates()
        INDEX_MEMBER_DF['outDate'] = INDEX_MEMBER_DF['outDate'].astype('int')
        INDEX_MEMBER_DF['consTickerSymbol'] = INDEX_MEMBER_DF['consTickerSymbol'].map(lambda x: str(x).zfill(6))

    filter_member_df = INDEX_MEMBER_DF[(INDEX_MEMBER_DF['intoDate'] <= _date) & (INDEX_MEMBER_DF['outDate'] > _date)]

    if len(stock_day_list) <= 0:
        # 这一天没有股票交易
        return None

    stock_df = pd.DataFrame(stock_day_list, columns=['market', 'code', 'close', 'pe_ttm', 'pb', 'roe', 'dr'])
    stock_df = stock_df.fillna(0)

    pe_list = []
    pb_list = []
    roe_list = []
    dr_list = []

    for idx, r in filter_member_df.iterrows():
        _market = 0 if r["consExchangeCD"] == 'XSHE' else 1
        _item = stock_df[(stock_df["market"] == _market) & (stock_df["code"] == r["consTickerSymbol"])]

        if len(_item) <= 0:
            print("\t\t没有找到股票: %s" % r["consTickerSymbol"])
            continue

        pe_list.append(_item.values[0][3])
        pb_list.append(_item.values[0][4])
        roe_list.append(_item.values[0][5])
        dr_list.append(_item.values[0][6])

    mid_value_pe = number.get_median(pe_list)
    mid_value_pb = number.get_median(pb_list)
    avg_value_roe = number.get_average(roe_list)
    avg_value_dr = number.get_average(dr_list)

    # 日期、指数代码、pe-ttm中位数、pb中位数、roe中位数、股息率中位数
    # todo 1周涨幅、一月涨幅、一季涨幅、今年至今、一年涨幅、两年涨幅、三年涨幅、五年涨幅
    return [mid_value_pe, mid_value_pb, avg_value_roe, avg_value_dr]
