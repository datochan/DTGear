import pandas as pd

from app.comm import date
from configure import config

REPORT_PUBLISH_BUFFER = pd.DataFrame()


def report_with_plan(_date: int, _str_code=None):
    """根据财报的标准时间获取财报信息"""
    global REPORT_PUBLISH_BUFFER

    if len(REPORT_PUBLISH_BUFFER) <= 0:
        REPORT_PUBLISH_BUFFER = pd.read_csv(config.get("files").get("reports"), header=0)

    report_date = date.report_date_with(_date)
    filter_df = REPORT_PUBLISH_BUFFER[(REPORT_PUBLISH_BUFFER["date"] == int(report_date)) &
                                      (REPORT_PUBLISH_BUFFER["code"] == int(_str_code))]
    if filter_df is None or len(filter_df) <= 0:
        return None

    return filter_df.loc[filter_df.index.values[0]]


def report_with_act(_date: int, _str_code=None):
    """
    取指定日期中实际最近的一次财报信息
    :param _date:
    :param _str_code:
    :return:
    """
    report_date = date.report_date_with(_date)
    _item = report_with_plan(report_date, _str_code)

    if _item is not None and _item['publish'] <= _date:
        # 判断当前日期是否大于披露时间
        return _item

    # 财报还未披露，只能取再上一次的财报信息
    report_date = date.prev_report_date_with(report_date)
    _item = report_with_plan(report_date, _str_code)
    if _item is not None and _item['publish'] <= _date:
        return _item

    # 上一次的财报还未披露(例如一季报没出来，年报也未出), 则取再上一次的财报信息
    report_date = date.prev_report_date_with(report_date)
    _item = report_with_plan(report_date, _str_code)
    if _item is not None and _item['publish'] <= _date:
        return _item

    # 再上一次没有财报或者没有披露，则当作没有财报数据了
    return None


def pb_with(_date, _stock, _price):
    """
    获取某只股票某个时段的PB值
    以当时日期最新的年报计算
    :param int _date:
    :param str _stock:
    :param _price:
    :return:
    """
    # 取最近一次财报，看总股本
    _cur_item = report_with_act(_date, _stock)
    if _cur_item is None or _cur_item['tcs'] == 0.0:
        # 最近三期都没有财报，说明股票财报数据无效，Pb未0
        return 0

    return _price / _cur_item['bps']


def lyr_with(_date, _stock, _price):
    """
    获取某只股票某个时段的静态市盈率
    也就是以当时日期最新的年报数据计算
    :param _date:
    :param _stock:
    :param _price:
    :return:
    """
    (_year, _quarter) = date.quarter(_date)

    _year_report = report_with_plan(int("%d1231" % (_year - 1)), _stock)
    if _year_report is None or _year_report["publish"] > _date:
        # 去年的年报还没披露, 取前年的
        _year_report = report_with_plan(int("%d1231" % (_year - 2)), _stock)
        if _year_report is None:
            # 前年还没上市，也没财报信息，PE无效
            return 0.0

    if _year_report['eps'] == 0.0 or _year_report['tcs'] == 0.0:
        # 没有有效数据，pe没有参考意义
        return 0.0

    # 取最近一次财报，看总股本
    _cur_item = report_with_act(_date, _stock)
    if _cur_item is None or _cur_item['tcs'] == 0.0:
        # 最近三期都没有财报，说明股本不会有什么变化，直接用上面年报的eps即可
        return _price / _year_report['eps']

    # 因股本变动会导致eps被稀释
    lyr_eps = _year_report['eps'] * (_year_report['tcs'] / _cur_item['tcs'])
    return 0.0 if lyr_eps == 0 else _price / lyr_eps


def ttm_with(_date, _stock, _price):
    """
    获取指定日志的滚动市盈率(从2003年开始计算)
    :param _date:
    :param _stock:
    :param _price:
    :return:
    """
    _today = date.str_to_datetime(str(_date))
    if _today.year <= 2002 or (_today.year == 2003 and _today.month < 4):
        # 2002年以前没有四季报，以静态市盈率代替
        return lyr_with(_date, _stock, _price)

    _cur_item = report_with_act(_date, _stock)
    if _cur_item is None or _cur_item['tcs'] == 0.0:
        # 最近三期都没有财报信息，说明pe无参考意义
        return 0.0

    (__year, _report_quarter) = date.quarter(int(_cur_item['date']))
    if _report_quarter == 3:
        # 取到的财报所属季度是四季度的年报，则可以直接以年报计算
        return _price / _cur_item['eps']

    if _report_quarter == 2:
        # 取到的财报是三季报, 还需要 上一年年报 - 上一年三季报 + 当前的三季报
        _year_report = report_with_plan(int("%d1231" % (__year - 1)), _stock)
        _q3_report = report_with_plan(int("%d0930" % (__year - 1)), _stock)
        if _year_report is None or _q3_report is None:
            # 上市不足一年
            return _price / (_cur_item['np'] / _cur_item['tcs'])

        _current_eps = (_year_report['np'] - _q3_report['np'] + _cur_item['np']) / _cur_item['tcs']
        return 0.0 if _current_eps == 0 else _price / _current_eps

    if _report_quarter == 1:
        # 当前是当前年中报, 还需要 上一年年报 - 上一年年中报 + 当前年中报
        _year_report = report_with_plan(int("%d1231" % (__year - 1)), _stock)
        _q2_report = report_with_plan(int("%d0630" % (__year - 1)), _stock)
        if _year_report is None or _q2_report is None:
            # 上市不足一年
            return _price / (_cur_item['np'] / _cur_item['tcs'])

        _current_eps = (_year_report['np'] - _q2_report['np'] + _cur_item['np']) / _cur_item['tcs']
        return 0.0 if _current_eps == 0 else _price / _current_eps

    if _report_quarter == 0:
        # 当前是一季报, 还需要 上一年年报 - 上一年一季报 + 当前的一季报
        _year_report = report_with_plan(int("%d1231" % (__year - 1)), _stock)
        _q1_report = report_with_plan(int("%d0331" % (__year - 1)), _stock)
        if _year_report is None or _q1_report is None:
            # 上市不足一年
            return _price / (_cur_item['np'] / _cur_item['tcs'])

        _current_eps = (_year_report['np'] - _q1_report['np'] + _cur_item['np']) / _cur_item['tcs']
        return 0.0 if _current_eps == 0 else _price / _current_eps

    return 0.0


if __name__ == "__main__":
    item = ttm_with(20190424, "002027", 7.03)
    # item = pb_with(20181109, "601318", 64.62)
    print(item)
