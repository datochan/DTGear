# -*- coding: utf-8 -*-
"""
    stocks
    ~~~~~~~~~~~~~~
    获取股票相关的信息

    :copyright: (c) 18/11/21 by datochan.
"""

import json

import numpy as np
import pandas as pd
import pymongo
from flask import request
from flask_mako import render_template

from app.comm import date
from app.service.web import webapp
from app.service.web.models import StockModel


@webapp.route('/stock/<_code>', methods=['GET', 'POST'])
def stock(_code):
    """获取某只股票的详情"""
    if _code is None or len(_code) < 8:
        return "error"

    _market = 1 if _code[:2] == "SH" else 0
    _st_code = _code[2:]

    stock_model = StockModel()

    _filter = {"code": _st_code, "market": _market, "date": {"$gte": date.datetime_to_str(date.years_ago(10))}}

    _idx_list = stock_model.stock_list(_filter=_filter, _sort=[("date", pymongo.ASCENDING)],
                                      _fields={"date": 1, "name": 1, "pe_ttm": 1, "pb": 1, "dr": 1})

    item_df = pd.DataFrame(list(_idx_list), columns=["date", "name", "pe_ttm", "pb", "dr"])
    item_df = item_df.dropna(0)

    _pe_series = 1 / item_df["pe_ttm"]
    pe_ranks = _pe_series.rank(pct=True)

    _pb_series = 1 / item_df["pb"]
    pb_ranks = _pb_series.rank(pct=True)

    return render_template('stocks/detail.mako', ctx={
        "stock_name": item_df["name"].values[0],
        "stock_code": _code,
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


@webapp.route('/stock/<_code>/pe.json', methods=['GET', 'POST'])
def stock_pe_json(_code: str = None):
    if _code is None or len(_code) < 8:
        return "error"
    _code = _code.upper()
    is_all = request.args.get('all')
    data = []
    _market = 1 if _code[:2] == "SH" else 0
    _idx_code = _code[2:]

    stockModel = StockModel()

    _filter = {"code": _idx_code, "market": _market}
    if is_all is None or len(is_all) <= 0:
        from_date = date.datetime_to_str(date.years_ago(10))
        _filter["date"] = {"$gte": from_date}

    _idx_list = stockModel.stock_list(_filter=_filter, _sort=[("date", pymongo.ASCENDING)],
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


@webapp.route('/stock/<_code>/pb.json', methods=['GET', 'POST'])
def stock_pb_json(_code=None):
    if _code is None or len(_code) < 8:
        return "error"
    _code = _code.upper()
    is_all = request.args.get('all')
    data = []
    _market = 1 if _code[:2] == "SH" else 0
    _idx_code = _code[2:]

    stockModel = StockModel()

    _filter = {"code": _idx_code, "market": _market}
    if is_all is None or len(is_all) <= 0:
        from_date = date.datetime_to_str(date.years_ago(10))
        _filter["date"] = {"$gte": from_date}

    _idx_list = stockModel.stock_list(_filter=_filter, _sort=[("date", pymongo.ASCENDING)],
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
