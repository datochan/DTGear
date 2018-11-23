# -*- coding: utf-8 -*-
"""
    date
    ~~~~~~~~~~~~~~
    股市交易中的时间计算模块

    :copyright: (c) 16/11/3 by datochan.
"""
from datetime import datetime, timedelta
import pandas as pd

from configure import *


CALENDAR_BUFFER = pd.DataFrame()  # 股市交易日历的全局缓存


def years_ago(years, from_date=None):
    """获取几年前的日期"""
    if from_date is None:
        from_date = datetime.now()
    try:
        return from_date.replace(year=from_date.year - years)
    except ValueError:
        # Must be 2/29!
        assert from_date.month == 2 and from_date.day == 29 # can be removed
        return from_date.replace(month=2, day=28,
                                 year=from_date.year-years)

def is_work_day(date:int):
    """
    当前指定日期是否是交易日
    :param int date: xxxxxxxx 格式
    :return:
    """
    try:
        global CALENDAR_BUFFER
        if len(CALENDAR_BUFFER) <= 0:
            CALENDAR_BUFFER = pd.read_csv(config.get("files").get("calendar"), header=0)

        filter_df = CALENDAR_BUFFER[CALENDAR_BUFFER['calendarDate'] == date]

        for index, row in filter_df.iterrows():
            if row['isOpen'] == 1:
                return True
        return False
    except Exception as ex:
        print(str(ex))
        return None


def next_day(date):
    """
    获取某个日期的下一个交易日
    :param date: str xxxxxxxx 格式
    :return:
    """
    try:
        global CALENDAR_BUFFER
        if len(CALENDAR_BUFFER) <= 0:
            CALENDAR_BUFFER = pd.read_csv(config.get("files").get("calendar"), header=0)

        filter_df = CALENDAR_BUFFER[CALENDAR_BUFFER['calendarDate'] > date]

        for index, row in filter_df.iterrows():
            if row['isOpen'] == 1:
                return int(row['calendarDate'])
        return None
    except Exception as ex:
        print(str(ex))
        return None


def prev_day(_date):
    """
    获取某个日期的上一个交易日
    :param int _date: xxxxxxxx 格式
    :return:
    """
    try:
        global CALENDAR_BUFFER
        if len(CALENDAR_BUFFER) <= 0:
            CALENDAR_BUFFER = pd.read_csv(config.get("files").get("calendar"), header=0)

        filter_df = CALENDAR_BUFFER[CALENDAR_BUFFER['calendarDate'] == _date]
        for index, row in filter_df.iterrows():
            return int(row[["prevTradeDate"]])
        return None

    except FileNotFoundError as ex:
        print(str(ex))
    except Exception as ex:
        print(str(ex))
        pass

    return None


def last_days(_start=19901219, _type=1, _all=False):
    """
    获取指定某周，某月，某季度的某年的最后一个交易日的列表
    :notice: 如果要获取第一个交易日就获取上一个最后交易日然后通过next_day获取
    :param _start: 开始日期，如果不指定则获取从沪市成立以来的所有
    :param _type: 指定类别: 0 表示自start以来第一周的交易日, 1表示自start以来月份的第一个交易日,
                          2 表示自start以来季度的第一个交易日, 3表示自start以来每年度的第一个交易日
    :param _all: True表示一直到今天为止符合条件的日期列表, False表示只获取下一个满足条件的日期
    :return:
    """
    last_day_list = []
    try:
        global CALENDAR_BUFFER
        if len(CALENDAR_BUFFER) <= 0:
            CALENDAR_BUFFER = pd.read_csv(config.get("files").get("calendar"), header=0)
        filter_df = CALENDAR_BUFFER[CALENDAR_BUFFER['calendarDate'] >= _start]

        for index, row in filter_df.iterrows():
            if row['isOpen'] != 1:
                continue

            if _type == 0 and row["isWeekEnd"] == 1:
                if _all is False:
                    return row['calendarDate']
                else:
                    last_day_list.append(row['calendarDate'])

            elif _type == 1 and row["isMonthEnd"] == 1:
                if _all is False:
                    return row['calendarDate']
                else:
                    last_day_list.append(row['calendarDate'])

            elif _type == 2 and row["isQuarterEnd"] == 1:
                if _all is False:
                    return row['calendarDate']
                else:
                    last_day_list.append(row['calendarDate'])

            elif _type == 3 and row["isYearEnd"] == 1:
                if _all is False:
                    return row['calendarDate']
                else:
                    last_day_list.append(row['calendarDate'])

        return None if len(last_day_list) <= 0 else last_day_list

    except Exception as ex:
        print(str(ex))
        return None


def str_to_datetime(_date:str):
    """将字符串转换成datetime类型"""
    try:
        return datetime.strptime(str(_date), "%Y%m%d")
    except Exception as ex:
        print("----->%s" % str(ex))


def datetime_to_str(date):
    """将datetime类型转换为日期型字符串,格式为2008-08-02"""
    return str(date)[0:10].replace("-", "")


def today():
    return datetime_to_str(datetime.now())


def add_days(start="19901219", delta=1):
    """
    获取指定日期后第几个交易日的日期
    :param start: 指定日期
    :param delta: 第几个交易日
    :return: 返回指定交易日的日期
    """
    try:
        calendar_df = pd.read_csv(config.get("files").get("calendar"), header=0)
        filter_df = calendar_df[calendar_df['calendarDate'] > start]
        delta_idx = 0

        for index, row in filter_df.iterrows():
            if row['isOpen'] == 1:
                delta_idx += 1
            if delta_idx >= delta:
                return row['calendarDate']

        return None
    except Exception as ex:
        print("获取 N个交易日后的日期时发生错误: %s" % str(ex))
        return None


def add_days_except_weekend(start, days):
    """
    在指定日期中增加指定的天数(跳过周末)
    :param start: 指定的日期 YYYYMMDD
    :param int days: 增加的天数
    :return: str YYYYMMDD
    """
    idx = 0
    dt_idx = 0
    dt_start = str_to_datetime(start)
    dt_current = dt_start

    while idx < days*2:
        idx += 1
        dt_current = dt_start + timedelta(days=idx)
        if dt_current.weekday() != 5 and dt_current.weekday() != 6:
            # 不是周末就 增加一天
            dt_idx += 1

        if dt_idx >= days:
            break

    return datetime_to_str(dt_current)


def quarter(_date:int):
    """
    获取指定日期属于第几季度
    :param int _date: yyyymmdd 格式的日期字符串
    :return: 0表示第一季度，1表示第二季度 ...
    """
    year = int(_date/10000)
    month = int(_date%10000/100)

    if month in [1, 2, 3]:
        return year, 0

    if month in [4, 5, 6]:
        return year, 1

    if month in [7, 8, 9]:
        return year, 2

    if month in [10, 11, 12]:
        return year, 3

    return None


def report_date_with(_date:int):
    """
    根据当前日期获取标准的财报日期
    :param _date: 指定日期时间yyyymmdd
    :return:
    """
    quarter_date = ["1231", "0331", "0630", "0930"]

    (_year, _quarter) = quarter(_date)

    month_day = "%02d%02d" % (int(_date%10000/100), int(_date%100))

    if month_day in quarter_date:
        return _date

    if _quarter == 0:
        return int("%d%s" % (int(_year)-1, quarter_date[_quarter]))

    return int("%d%s" % (_year, quarter_date[_quarter]))


def report_date_list_with(_date=None):
    """获取指定日期所有的财报"""
    date_list = ["19980630", "19981231", "19990630", "19991231", "20000630", "20001231",
                 "20010630", "20010930", "20011231"]

    _today = datetime.today()
    if _date is not None:
        _today = str_to_datetime(_date)

    idx = 2002
    while idx < _today.year:
        date_list.append("%d0331" % idx)
        date_list.append("%d0630" % idx)
        date_list.append("%d0930" % idx)
        date_list.append("%d1231" % idx)

        idx += 1

    # 超过3月份的就需要更新一季度
    target = str_to_datetime("%d0331" % _today.year)
    if target <= _today:
        date_list.append("%d0331" % _today.year)

    target = str_to_datetime("%d0630" % _today.year)
    if target <= _today:
        date_list.append("%d0630" % _today.year)

    target = str_to_datetime("%d0930" % _today.year)
    if target <= _today:
        date_list.append("%d0930" % _today.year)

    target = str_to_datetime("%d1231" % _today.year)
    if target <= _today:
        date_list.append("%d1231" % _today.year)

    return date_list


def prev_report_date_with(_date):
    """获取指定财报日期的前一个财报日期"""
    date_list = report_date_list_with(str(_date))


    if str(_date) not in date_list:
        # 不存在或者已经是第一个了没有前一份财报了
        return None

    idx = date_list.index(str(_date))
    return int(date_list[idx-1])

