import pandas as pd

from app.comm import date
from configure import config

BONUS_BUFFER = pd.DataFrame()

def bonus_with(_code=None):
    """ 获取某只股票的高送转信息"""
    global BONUS_BUFFER

    if len(BONUS_BUFFER) <= 0:
        BONUS_BUFFER = pd.read_csv(config.get("files").get("bonus"), header=0, encoding="utf8")
        BONUS_BUFFER['code'] = BONUS_BUFFER['code'].map(lambda x: str(x).zfill(6))

    if _code is not None:
        bonus_df = BONUS_BUFFER[BONUS_BUFFER["code"] == _code]
        return bonus_df

    return BONUS_BUFFER


def dividend_rate_with(_date:int, _code:str, _price:float):
    """
    求某只股票在指定时间点的三年平均股息率
    :param _date:
    :param _code:
    :param _price:
    :return:
    """
    end = date.str_to_datetime(str(_date))
    start = date.years_ago(years=3, from_date=end)
    bonus_df = bonus_with(_code=_code).sort_values(['date'], ascending=True)
    filter_df = bonus_df[(bonus_df["type"] == 1) &
                         (bonus_df["date"] >= int(date.datetime_to_str(start))) &
                         (bonus_df["date"] <= int(date.datetime_to_str(end)))]

    total_money = 0.0
    for idx, item in filter_df.iterrows():
        # 每股分红的三年之和
        total_money += item["money"]/10

    return total_money / (3*_price)