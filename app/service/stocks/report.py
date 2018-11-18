import pandas as pd

from app.comm import date
from configure import config

REPORT_PUBLISH_BUFFER = pd.DataFrame()

def report_with_plan(_date:int, _str_code=None):
    """根据财报的标准时间后去财报信息"""
    global REPORT_PUBLISH_BUFFER

    if len(REPORT_PUBLISH_BUFFER) <= 0:
        REPORT_PUBLISH_BUFFER = pd.read_csv(config.get("files").get("reports"), header=0)

    report_date = date.report_date_with(_date)
    filter_df = REPORT_PUBLISH_BUFFER[(REPORT_PUBLISH_BUFFER["date"]==int(report_date)) &
                                      (REPORT_PUBLISH_BUFFER["code"]==int(_str_code))]
    if filter_df is None or len(filter_df) <= 0:
        return None

    return filter_df.loc[filter_df.index.values[0]]

def report_with_act(_date:int, _str_code=None):
    """
    实际当前的实际日期获取财报信息
    :param _date:
    :param _str_code:
    :return:
    """
    report_date = date.report_date_with(_date)
    _item = report_with_plan(report_date, _str_code)

    if _item is None:
        return None

    # 判断当前日期是否大于披露时间，否则取用上一个财报信息
    if _item['publish'] <= _date:
        return _item

    report_date = date.prev_report_date_with(report_date)
    if report_date is None:
        # 已经是第一份财报了
        return None

    return report_with_plan(int(report_date), _str_code)


def pb_with(_date, _stock, _price):
    """
    获取某只股票某个时段的PB值
    :param _date:
    :param _stock:
    :param _price:
    :return:
    """
    _item = report_with_act(_date, _stock)
    if _item is None or _item['bps'] == 0:
        return 0.0

    return _price / _item['bps']


def lyr_with(_date, _stock, _price):
    """
    获取某只股票某个时段的静态市盈率
    :param _date:
    :param _stock:
    :param _price:
    :return:
    """
    _today = date.str_to_datetime(str(_date))
    _cur_item = report_with_act(_date, _stock)
    if _cur_item is None or _cur_item['tcs'] == 0.0:
        # 刚上市还没公布最新财报或者没有股本信息
        return 0.0

    _year_report = report_with_plan(int("%d1231" % (_today.year-1)), _stock)

    if _year_report is None or _year_report["publish"] > _date:
        # 去年的年报还没披露, 取前年的
        _year_report = report_with_plan(int("%d1231" % (_today.year-2)), _stock)
        # 前年还没上市，也没财报信息
        if _year_report is None:
            return 0.0

    if _year_report['eps'] == 0.0 or _year_report['tcs'] == 0.0:
        # 前年还没上市，也没足够的财报信息
        return 0.0

    # 用年报的每股收益* 因股本变动导致的稀释
    lyr_eps = _year_report['eps'] * (_year_report['tcs']/_cur_item['tcs'])
    return 0.0 if lyr_eps == 0 else _price / lyr_eps


def pe_ttm_with(_date, _stock, _price):
    """
    获取指定日志的滚动市盈率(从2003年开始计算)
    :param _date:
    :param _stock:
    :param _price:
    :return:
    """
    _today = date.str_to_datetime(str(_date))
    if _today.year <= 2002 or (_today.year == 2003 and _today.month < 4):
        # 2002年以前没有四季宝，只算静态市盈率
        return lyr_with(_date, _stock, _price)

    _cur_item = report_with_act(_date, _stock)
    if _cur_item is None or _cur_item['tcs'] == 0.0:
        return 0.0

    (__year, _report_quarter) = date.quarter(int(_cur_item['date']))
    if _report_quarter == 3:
        # 刚公布了年报,直接以年报计算
        return _price / _cur_item['eps']

    if _report_quarter == 2:
        # 当前是三季报, 还需要 上一年年报 - 上一年三季报 + 当前的三季报
        _year_report = report_with_plan(int("%d1231" % (__year-1)), _stock)
        _q3_report = report_with_plan(int("%d0930" % (__year-1)), _stock)
        if _year_report is None or _q3_report is None:
            # 上市不足一年
            return _price / (_cur_item['np'] / _cur_item['tcs'])

        _current_eps = (_year_report['np'] - _q3_report['np'] + _cur_item['np']) / _cur_item['tcs']
        return 0.0 if _current_eps == 0 else _price / _current_eps

    if _report_quarter == 1:
        # 当前是当前年中报, 还需要 上一年年报 - 上一年年中报 + 当前年中报
        _year_report = report_with_plan(int("%d1231" % (__year-1)), _stock)
        _q2_report = report_with_plan(int("%d0630" % (__year-1)), _stock)
        if _year_report is None or _q2_report is None:
            # 上市不足一年
            return _price / (_cur_item['np'] / _cur_item['tcs'])

        _current_eps = (_year_report['np'] - _q2_report['np'] + _cur_item['np']) / _cur_item['tcs']
        return 0.0 if _current_eps == 0 else _price / _current_eps

    if _report_quarter == 0:
        # 当前是一季报, 还需要 上一年年报 - 上一年一季报 + 当前的一季报
        _year_report = report_with_plan(int("%d1231" % (__year-1)), _stock)
        _q1_report = report_with_plan(int("%d0331" % (__year-1)), _stock)
        if _year_report is None or _q1_report is None:
            # 上市不足一年
            return _price / (_cur_item['np'] / _cur_item['tcs'])

        _current_eps = (_year_report['np'] - _q1_report['np'] + _cur_item['np']) / _cur_item['tcs']
        return 0.0 if _current_eps == 0 else _price / _current_eps

    return 0.0


if __name__ == "__main__":
    item = pe_ttm_with(20181114, "300104", 3.61)
    # item = pb_with(20181109, "601318", 64.62)
    print(item)
