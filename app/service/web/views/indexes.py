# -*- coding: utf-8 -*-
"""
    indexes
    ~~~~~~~~~~~~~~
    获取指数相关的信息

    :copyright: (c) 18/11/21 by datochan.
"""
import json
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pymongo
from flask import request
from flask_mako import render_template

from app.comm import date
from app.service.web import webapp
from app.service.web.models import StockModel
from configure import PROJECT_ROOT, config


@webapp.route('/indexes', methods=['GET', 'POST'])
def indexes():
    """显示指数估值信息"""
    _lp_file = None

    try:
        _lp_file = open("%s/last_update" % PROJECT_ROOT, 'r')
        _content = _lp_file.read()
        last_date = _content.strip()
    finally:
        if _lp_file:
            _lp_file.close()

    _tmp_date = date.datetime_to_str(date.years_ago(years=3))
    _tmp_date = _tmp_date if date.is_work_day(int(_tmp_date)) else str(date.next_day(int(_tmp_date)))

    last_date = last_date if date.is_work_day(int(last_date)) else str(date.prev_day(int(last_date)))

    return render_template('indexes/list.mako', ctx={
        "last_date": last_date,
        "start_date": _tmp_date
    })


@webapp.route('/indexes.json', methods=['GET', 'POST'])
def indexes_json():
    """显示指数估值信息"""
    # '上证50', '沪深300', '中证500', '中证1000', '上证红利', '中证红利'，'中小板指', '创业扳指'
    # '食品饮料'
    idx_list = config.get("indexes")
    stock_model = StockModel()
    result = []

    for idx, item in enumerate(idx_list):
        index_obj = {"idx": idx + 1}
        _market = 'SZ' if item[0] == 0 else 'SH'

        item_detail = stock_model.stock_item(_filter={"code": item[1], "market": item[0]},
                                             _sort=[("date", pymongo.DESCENDING)])

        index_obj["name"] = "<a href='/index/%s%s' title='%s的估值信息'> %s </a>" % \
                            (_market, item_detail["code"], item_detail["name"], item_detail["name"])
        index_obj["interest"] = "%.2f%%" % (1 / item_detail["pe_ttm"] * 100)
        index_obj["dr"] = "%.2f%%" % (item_detail["dr"] * 100)
        index_obj["roe"] = "%.2f%%" % (item_detail["roe"] * 100)
        index_obj["PE"] = "%.2f" % item_detail["pe_ttm"]
        index_obj["PB"] = "%.2f" % item_detail["pb"]

        _filter = {"code": item[1], "market": item[0], "date": {"$gte": date.datetime_to_str(date.years_ago(10))}}
        item_list = stock_model.stock_list(_filter=_filter, _sort=[("date", pymongo.ASCENDING)],
                                           _fields={"pe_ttm": 1, "pb": 1})

        item_df = pd.DataFrame(list(item_list), columns=["pe_ttm", "pb"])
        item_df = item_df.dropna(0)

        _pe_series = 1 / item_df["pe_ttm"]
        pe_ranks = _pe_series.rank(pct=True)

        _pb_series = 1 / item_df["pb"]
        pb_ranks = _pb_series.rank(pct=True)

        index_obj["PE_RATE"] = "%.2f%%" % ((1 - pe_ranks.values[-1]) * 100)
        index_obj["PB_RATE"] = "%.2f%%" % ((1 - pb_ranks.values[-1]) * 100)

        # 本周以来的涨跌幅
        now = datetime.today()
        _tmp_date = (now - timedelta(days=now.weekday())).strftime('%Y%m%d')
        item_last_week = stock_model.stock_item(_filter={"code": item[1], "market": item[0],
                                                         "date": _tmp_date if date.is_work_day(int(_tmp_date))
                                                         else str(date.next_day(int(_tmp_date)))})
        if item_last_week is None:
            item_last_week = item_detail

        # 本月以来
        _tmp_date = datetime(now.year, now.month, 1).strftime('%Y%m%d')
        item_last_month = stock_model.stock_item(_filter={"code": item[1], "market": item[0],
                                                          "date": _tmp_date if date.is_work_day(int(_tmp_date))
                                                          else str(date.next_day(int(_tmp_date)))})
        if item_last_month is None:
            item_last_month = item_detail

        # 本季度以来
        month = (now.month - 1) - (now.month - 1) % 3 + 1
        _tmp_date = datetime(now.year, month, 1).strftime('%Y%m%d')
        item_last_quarter = stock_model.stock_item(_filter={"code": item[1], "market": item[0],
                                                            "date": _tmp_date if date.is_work_day(int(_tmp_date))
                                                            else str(date.next_day(int(_tmp_date)))})

        if item_last_quarter is None:
            item_last_quarter = item_detail

        # 本年度以来
        _tmp_date = datetime(now.year, 1, 1).strftime('%Y%m%d')
        item_last_year = stock_model.stock_item(_filter={"code": item[1], "market": item[0],
                                                         "date": _tmp_date if date.is_work_day(int(int(_tmp_date)))
                                                         else str(date.next_day(int(_tmp_date)))})

        if item_last_year is None:
            item_last_year = item_detail

        index_obj["last_week"] = "%.2f%%" % (
                    (item_detail["close"] - item_last_week["close"]) / item_last_week["close"] * 100)
        index_obj["last_month"] = "%.2f%%" % (
                    (item_detail["close"] - item_last_month["close"]) / item_last_month["close"] * 100)
        index_obj["last_quarter"] = "%.2f%%" % (
                    (item_detail["close"] - item_last_quarter["close"]) / item_last_quarter["close"] * 100)
        index_obj["last_year"] = "%.2f%%" % (
                    (item_detail["close"] - item_last_year["close"]) / item_last_year["close"] * 100)
        result.append(index_obj)

    # 追加A股市场的估值信息
    stock_a_df = pd.read_csv(config.get("files").get("stock_a"), header=0, encoding="utf8")
    stock_a_df = stock_a_df.dropna(0)
    if len(stock_a_df) > 0:
        item_last = stock_a_df.loc[stock_a_df.index[-1]]

        pe_array = 1 / stock_a_df["pe"]
        pb_array = 1 / stock_a_df["pb"]
        pe_ranks = pe_array.rank(pct=True)
        pb_ranks = pb_array.rank(pct=True)

        stock_a_item = {"idx": len(idx_list) + 1, "name": "A股市场", "interest": "%.2f%%" % (1 / item_last["pe"] * 100),
                        "dr": "%.2f%%" % (item_last["dr"] * 100), "roe": "%.2f%%" % (item_last["roe"] * 100),
                        "PE": "%.2f" % item_last["pe"], "PB": "%.2f" % item_last["pb"],
                        "PE_RATE": "%.2f%%" % ((1 - pe_ranks.values[-1]) * 100),
                        "PB_RATE": "%.2f%%" % ((1 - pb_ranks.values[-1]) * 100)}

        result.append(stock_a_item)

    # 追加国债收益供参考
    bond_df = pd.read_csv(config.get("files").get("bond"), header=0, encoding="utf8")
    if len(bond_df) > 0:
        item_last = bond_df.loc[bond_df.index[-1]]
        bond_item = {"idx": len(idx_list) + 2,
                     "name": "<a href='http://www.pbc.gov.cn/rmyh/108976/index.html#Container' "
                             "title='%s的历史利率' target='_blank'> 十年国债利率 </a>",
                     "interest": "%.2f%%" % item_last["10year"]}
        result.append(bond_item)

    return json.dumps(result)


@webapp.route('/index/<_code>', methods=['GET', 'POST'])
def index(_code=None):
    if _code is None or len(_code) < 8:
        return "error"

    """获取某个指数的详情"""
    _market = 1 if _code[:2] == "SH" else 0
    _idx_code = _code[2:]

    stock_model = StockModel()

    _filter = {"code": _idx_code, "market": _market, "date": {"$gte": date.datetime_to_str(date.years_ago(10))}}

    _idx_list = stock_model.stock_list(_filter=_filter, _sort=[("date", pymongo.ASCENDING)],
                                       _fields={"date": 1, "name": 1, "pe_ttm": 1, "pb": 1, "dr": 1})

    item_df = pd.DataFrame(list(_idx_list), columns=["date", "name", "pe_ttm", "pb", "dr"])
    item_df = item_df.dropna(0)

    _pe_series = 1 / item_df["pe_ttm"]
    pe_ranks = _pe_series.rank(pct=True)

    _pb_series = 1 / item_df["pb"]
    pb_ranks = _pb_series.rank(pct=True)

    return render_template('indexes/detail.mako', ctx={
        "index_name": item_df["name"].values[0],
        "index_code": _code,
        "start_date": date.datetime_to_str(date.years_ago(years=3)),

        "pe_max": "%.2f" % item_df["pe_ttm"].max(),
        "pe_min": "%.2f" % item_df["pe_ttm"].min(),
        "pe_mean": "%.2f" % item_df["pe_ttm"].mean(),
        "pe_high": "%.2f" % item_df["pe_ttm"].quantile(0.75),
        "pe_middle": "%.2f" % item_df["pe_ttm"].quantile(0.5),
        "pe_low": "%.2f" % item_df["pe_ttm"].quantile(0.2),
        "pe_value": "%.2f" % item_df["pe_ttm"].values[-1],
        "pe_rate": "%.2f%%" % ((1 - pe_ranks.values[-1]) * 100),

        "pb_max": "%.2f" % item_df["pb"].max(),
        "pb_min": "%.2f" % item_df["pb"].min(),
        "pb_mean": "%.2f" % item_df["pb"].mean(),
        "pb_high": "%.2f" % item_df["pb"].quantile(0.75),
        "pb_middle": "%.2f" % item_df["pb"].quantile(0.5),
        "pb_low": "%.2f" % item_df["pb"].quantile(0.2),
        "pb_value": "%.2f" % item_df["pb"].values[-1],
        "pb_rate": "%.2f%%" % ((1 - pb_ranks.values[-1]) * 100),

        "dr_max": "%.2f%%" % (item_df["dr"].max() * 100),
        "dr_min": "%.2f%%" % (item_df["dr"].min() * 100),
        "dr_mean": "%.2f%%" % (item_df["dr"].mean() * 100),
        "dr_value": "%.2f%%" % (item_df["dr"].values[-1] * 100)
    })


@webapp.route('/index/<_code>/pe.json', methods=['GET', 'POST'])
def index_pe_json(_code: str = None):
    if _code is None or len(_code) < 8:
        return "error"
    _code = _code.upper()
    is_all = request.args.get('all')
    data = []
    _market = 1 if _code[:2] == "SH" else 0
    _idx_code = _code[2:]

    stock_model = StockModel()

    _filter = {"code": _idx_code, "market": _market}
    if is_all is None or len(is_all) <= 0:
        from_date = date.datetime_to_str(date.years_ago(10))
        _filter["date"] = {"$gte": from_date}

    _idx_list = stock_model.stock_list(_filter=_filter, _sort=[("date", pymongo.ASCENDING)],
                                       _fields={"date": 1, "pe_ttm": 1, "close": 1})

    item_df = pd.DataFrame(list(_idx_list), columns=["date", "pe_ttm", "close"])
    item_df = item_df.dropna(0)
    item_df = item_df.reset_index()

    _pe_series = 1 / item_df["pe_ttm"]
    pe_ranks = _pe_series.rank(pct=True)

    _pe_list = []
    for idx, row in item_df.iterrows():
        _pe_list.append(row["pe_ttm"])

        _pe_high = np.percentile(_pe_list, 75)
        _pe_middle = np.percentile(_pe_list, 50)
        _pe_low = np.percentile(_pe_list, 20)

        _item_rank = float("%.2f" % ((1 - pe_ranks.values[idx]) * 100))
        data.append([row["date"], float("%.2f" % row["pe_ttm"]), float("%.2f" % _pe_high),
                     float("%.2f" % _pe_middle), float("%.2f" % _pe_low), _item_rank,
                     float("%.2f" % row["close"])])

    return json.dumps(data)


@webapp.route('/index/<_code>/pb.json', methods=['GET', 'POST'])
def index_pb_json(_code=None):
    if _code is None or len(_code) < 8:
        return "error"
    _code = _code.upper()
    is_all = request.args.get('all')
    data = []
    _market = 1 if _code[:2] == "SH" else 0
    _idx_code = _code[2:]

    stock_model = StockModel()

    _filter = {"code": _idx_code, "market": _market}
    if is_all is None or len(is_all) <= 0:
        from_date = date.datetime_to_str(date.years_ago(10))
        _filter["date"] = {"$gte": from_date}

    _idx_list = stock_model.stock_list(_filter=_filter, _sort=[("date", pymongo.ASCENDING)],
                                       _fields={"date": 1, "pb": 1, "close": 1})

    item_df = pd.DataFrame(list(_idx_list), columns=["date", "pb", "close"])
    item_df = item_df.dropna(0)
    item_df = item_df.reset_index()

    _pb_series = 1 / item_df["pb"]
    pb_ranks = _pb_series.rank(pct=True)
    _pb_list = []
    for idx, row in item_df.iterrows():
        _pb_list.append(row["pb"])

        _pb_high = np.percentile(_pb_list, 75)
        _pb_middle = np.percentile(_pb_list, 50)
        _pb_low = np.percentile(_pb_list, 20)

        _item_rank = float("%.2f" % ((1 - pb_ranks.values[idx]) * 100))
        data.append([row["date"], float("%.2f" % row["pb"]), float("%.2f" % _pb_high),
                     float("%.2f" % _pb_middle), float("%.2f" % _pb_low), _item_rank,
                     float("%.2f" % row["close"])])

    return json.dumps(data)


@webapp.route('/index/<_code>/dr.json', methods=['GET', 'POST'])
def index_dr_json(_code=None):
    if _code is None or len(_code) < 8:
        return "error"
    _code = _code.upper()
    is_all = request.args.get('all')
    data = []
    _market = 1 if _code[:2] == "SH" else 0
    _idx_code = _code[2:]

    stock_model = StockModel()

    _filter = {"code": _idx_code, "market": _market}
    if is_all is None or len(is_all) <= 0:
        from_date = date.datetime_to_str(date.years_ago(10))
        _filter["date"] = {"$gte": from_date}

    _idx_list = stock_model.stock_list(_filter=_filter, _sort=[("date", pymongo.ASCENDING)],
                                       _fields={"date": 1, "dr": 1, "close": 1})

    item_df = pd.DataFrame(list(_idx_list), columns=["date", "dr", "close"])
    item_df = item_df.dropna(0)

    for idx, row in item_df.iterrows():
        data.append([row["date"], float("%.2f" % (row["dr"] * 100)), float("%.2f" % row["close"])])

    return json.dumps(data)


@webapp.route('/index/<code>/member', methods=['GET', 'POST'])
def member(code):
    """获取某个指数当前的成分股"""
    pass
