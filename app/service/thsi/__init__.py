import datetime

import pandas as pd
from pyquery import PyQuery as pq

from app.service.thsi import session
from app.comm.utils import netbase
from app.comm import date
from configure import PROJECT_ROOT



def __report_time(time_url, format_str, rt_file_path, date_str):
    """更新股票披露日期"""
    cur_page = 1
    max_page = 0
    data_list = []
    print("\t开始更新 %s 的财报披露时间..." % date_str)

    while True:
        client = session.C10JQKASession()
        client.update_server_time(time_url)

        html_cnt = netbase.HttpClient(format_str % (date_str, cur_page), cookie="v=%s"%client.encode())

        doc = pq(html_cnt.value().decode("gbk"))
        tr_node = doc("table tbody tr")
        for tr in tr_node.items():
            code_str = tr.children("td").eq(1).text().strip(' ')  # 股票代码
            first  = tr.children("td").eq(3).text().strip(' ')    # 首次预约时间
            changed = tr.children("td").eq(4).text().strip(' ')   # 变更时间
            act = tr.children("td").eq(5).text().strip(' ')       # 实际披露时间

            first = first.replace("-", "").replace("00000000", "")
            changed = changed.replace("-", "")
            act = act.replace("-", "").replace("00000000", "")

            data_list.append([code_str, first, changed, act])

        if 1 == cur_page:
            span_text = doc("div.m-page.J-ajax-page span").text()
            last_page = span_text.split("/")
            max_page = int(last_page[1])

        if cur_page > max_page:
            break

        print("\t\t已处理完 %s 财报的第 %d 页 数据, 共计 %d 页.." % (date_str, cur_page, max_page))
        cur_page += 1


    rt_list = pd.DataFrame(data_list, columns=["code", "first", "change", "act"])
    rt_list = rt_list.sort_values(['code'], ascending=1)

    rt_list.to_csv(rt_file_path, index=False, mode="w", encoding='utf8')

    print("\t%s 的财报披露时间更新结束..." % date_str)


def report_time(time_url, format_str, rt_file_path, date_str=None):
    """

    :param time_url:
    :param format_str:
    :param rt_file_path:
    :param date_str:
    :return:
    """
    date_list = []
    today = datetime.datetime.now()

    if date_str is not None:
        target = date.str_to_datetime(date_str)

        if today.year >= target.year:
            q1 = date.str_to_datetime("%d0331" % target.year)
            q2 = date.str_to_datetime("%d0630" % target.year)
            q3 = date.str_to_datetime("%d0930" % target.year)

            if q3 <= target: date_list.append("%d0930"%target.year)
            elif q2 <= target: date_list.append("%d0630"%target.year)
            elif q1 <= target: date_list.append("%d0331"%target.year)
            else: date_list.append("%d1231"%target.year-1)

            if today.year == target.year and today.month == 4:
                # 当年的4月份也得更新年报
                date_list.append("%d1231" % target.year - 1)
        else:
            print("指定的年报披露日期有误,不能超过当前日期!")
            return
    else:
        date_list = date.report_data()

    for item in date_list:
        _rt_file_path = rt_file_path % (PROJECT_ROOT, item)
        __report_time(time_url, format_str, _rt_file_path, item)
