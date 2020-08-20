import json

import pandas as pd
import pymongo
from flask_mako import render_template

from app.comm import date
from app.service.web import webapp
from app.service.web.models import StockModel


@webapp.route('/', methods=['GET', 'POST'])
def home():
    """首页 """
    return render_template('home.mako', ctx={
        "title": "宽基PB走势图",
        "start_date": date.datetime_to_str(date.years_ago(years=3))
    })


@webapp.route('/pb.json', methods=['GET', 'POST'])
def pb_json():
    """首页图标需要的数据 """
    data = []

    stockModel = StockModel()
    # '上证50', '沪深300', '中证500', '中小板指', '创业扳指'
    _idx_list = stockModel.stock_list(_filter={"code": "000016", "market": 1}, _sort=[("date", pymongo.ASCENDING)],
                                      _fields={"date": 1, "pb": 1})

    _idx_df_50 = pd.DataFrame(list(_idx_list), columns=["date", "pb"])
    _tmp_list_pb = _idx_df_50.pop("pb")
    _idx_df_50.insert(1, 'pb50', _tmp_list_pb)

    _idx_list = stockModel.stock_list(_filter={"code": "000300", "market": 1}, _sort=[("date", pymongo.ASCENDING)],
                                      _fields={"date": 1, "pb": 1})
    _idx_df_300 = pd.DataFrame(list(_idx_list), columns=["date", "pb"])
    _tmp_list_pb = _idx_df_300.pop("pb")
    _idx_df_300.insert(1, 'pb300', _tmp_list_pb)

    _idx_list = stockModel.stock_list(_filter={"code": "000905", "market": 1}, _sort=[("date", pymongo.ASCENDING)],
                                      _fields={"date": 1, "pb": 1})
    _idx_df_500 = pd.DataFrame(list(_idx_list), columns=["date", "pb"])
    _tmp_list_pb = _idx_df_500.pop("pb")
    _idx_df_500.insert(1, 'pb500', _tmp_list_pb)

    _idx_list = stockModel.stock_list(_filter={"code": "399005", "market": 0}, _sort=[("date", pymongo.ASCENDING)],
                                      _fields={"date": 1, "pb": 1})
    _idx_df_zx = pd.DataFrame(list(_idx_list), columns=["date", "pb"])
    _tmp_list_pb = _idx_df_zx.pop("pb")
    _idx_df_zx.insert(1, 'pbzx', _tmp_list_pb)

    _idx_list = stockModel.stock_list(_filter={"code": "399006", "market": 0}, _sort=[("date", pymongo.ASCENDING)],
                                      _fields={"date": 1, "pb": 1})
    _idx_df_cy = pd.DataFrame(list(_idx_list), columns=["date", "pb"])
    _tmp_list_pb = _idx_df_cy.pop("pb")
    _idx_df_cy.insert(1, 'pbcy', _tmp_list_pb)

    df = pd.merge(_idx_df_50, _idx_df_300, how='left', on=['date', 'date'])
    df = pd.merge(df, _idx_df_500, how='left', on=['date', 'date'])
    df = pd.merge(df, _idx_df_zx, how='left', on=['date', 'date'])
    df = pd.merge(df, _idx_df_cy, how='left', on=['date', 'date'])
    df = df.fillna('')
    for _, row in df.iterrows():
        data.append([row["date"],
                     "" if row["pb50"] == "" else float("%.3f" % row["pb50"]),
                     "" if row["pb300"] == "" else float("%.3f" % row["pb300"]),
                     "" if row["pb500"] == "" else float("%.3f" % row["pb500"]),
                     "" if row["pbzx"] == "" else float("%.3f" % row["pbzx"]),
                     "" if row["pbcy"] == "" else float("%.3f" % row["pbcy"])])

    return json.dumps(data)


from . import indexes
from . import stocks
