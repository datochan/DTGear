# DTGear
判断A股大盘及特定指数所处高低位的小工具, 整体思路是:

```
计算出大盘及特定指数所有成分股的PE、PB、ROE、股息率等指标数据，根据中位数计算大盘或相应指数的百分位，并以此来决策买入卖出操作。
```

本程序希望能提供的辅助功能有:
1. 根据特定的指数成分股计算出各指标的中位数和对应的百分位(参考: `https://xueqiu.com/3079173340/116571468` 和 `https://mp.weixin.qq.com/s/er0jExpS9qpMmnDiToF_hA`)。
1. 根据特定指数的成分股在对应的财报周期分析其整体的财务状况(参考: `https://mp.weixin.qq.com/s/oA2Dp5zlsGnaIzc0bAnhiw`)。
1. 根据A股个股的财务指标指定自己的指数基金(参考: `https://www.jisilu.cn/question/87517`)。
1. 根据以上功能定制自己的定投策略, 并针对相应策略进行回测。

---

### 目前已完成的功能:

1. 获取通达信的`高送转`、`日线行情`、`财报数据` 等信息。
1. 获取同花顺的财报披露时间(根据财报实际披露时间更新PE、PB等指标)。
1. 获取历年国债的几个月、1年、5年、10年期的利率收益率情况。
1. 计算个股的 股本、市值、静态市盈率、滚动市盈率、PB、ROE、股息率 信息。
1. 计算各指数的中位数、对应指标的百分位、盈利收益率等信息。

---

### Todolist

1. 加入执行日志,以便跟踪程序运行状态。
1. 加入 Web页面 可以围绕希望提供的辅助功能出具相应的报告及回测页面(各种图表)。

---

### 常见问题

1. 获取指数成分股的方法
之前是试用通联数据的接口抓的初始数据，之后都是根据中证指数公司的公告手工维护，很是辛苦。后来发现[优矿](https://uqer.datayes.com/)可以无限使用通联数据的接口，这里将更新成分股的脚本共享出来:

``` python
"""
获取指数成分股
成分股变更记录
"""
import time
import datetime
import pandas as pd

index_list = [
    # 上证50, 代码, 基准日
    {"code": "000016", "date": "20040102"}, 
    # 沪深300, 代码, 基准日
    {"code": "000300", "date": "20050408"}, 
    # 中证500, 代码, 基准日
    {"code": "000905", "date": "20070115"}, 
    # 中证1000, 代码, 基准日
    {"code": "000852", "date": "20141017"}
]

def str_to_datetime(_date):
    """将字符串转换成datetime类型"""
    try:
        return datetime.datetime.strptime(str(_date), "%Y%m%d")
    except Exception as ex:
        print("----->%s" % str(ex))


def datetime_to_str(date):
    """将datetime类型转换为日期型字符串,格式为2008-08-02"""
    return str(date)[0:10].replace("-", "")


def next_day(date):
    """
    获取某个日期的下一个交易日
    :param date: str xxxxxxxx 格式
    :return:
    """
    if len(date) <= 0:
        return u""
    
    current = str_to_datetime(date)
    delta = datetime.timedelta(days=1)
    target = current + delta
    return datetime_to_str(target)

def last_date(code):
    """
    获取指定指数成分股最后更新的日期
    没找到返回空字符串
    """
    try:
        idx_df = pd.read_csv("%s.csv" % code)
        item_last = idx_df.loc[idx_df.index[-1]]
        return str(item_last["intoDate"])
    except Exception, ex:
        return u""


def index_member(code, _init_date):
    print("\t开始获取 %s 的成分股数据..." % code)
    is_first = False
    current_count = 0
    begin_date = next_day(last_date(code))
    
    if len(begin_date) <= 0:
        begin_date = _init_date
        is_first = True

    today = "".join(time.strftime('%Y%m%d', time.localtime(time.time())))
    calendar_df = DataAPI.TradeCalGet(exchangeCD=u"XSHG,XSHE",beginDate=begin_date,endDate=today,field=u"", pandas="1")
    
    for index, row in calendar_df.iterrows():
        if row['isOpen'] != 1:
            continue
            
        print("\t --> 开始处理 %s 当日的成分股信息..." % row['calendarDate'])
        idx_df = DataAPI.IdxConsGet(secID=u"",ticker=code,isNew=u"",intoDate=row['calendarDate'],field=u"",pandas="1")
        
        filter_df = idx_df[idx_df["intoDate"]==row['calendarDate']]
        if len(filter_df) == current_count:
            continue

        currnet_count = len(filter_df)

        filter_df['intoDate'] = filter_df['intoDate'].astype(str).str.replace('-', '').replace('nan', '')
        filter_df['outDate'] = filter_df['outDate'].astype(str).str.replace('-', '').replace('nan', '')

        if is_first is True:
            filter_df.to_csv('%s.csv' % code, index=False, mode="w", header=True, encoding='utf8', float_format="%.6f")
            is_first = False
        else:
            filter_df.to_csv('%s.csv' % code, index=False, header=False, mode='a+', encoding='utf8', float_format="%.6f")

    print("\t获取 %s 的成分股数据完成..." % code)

def main():
    for item in index_list:
        index_member(item.get("code"), item.get("date"))
    print("任务完成！！！")


main()
```

获取到的数据直接扔到 `/data/indexes` 目录下即可

2. 股票ST标识的获取及更新方法

默认情况下, 只要将 `/update_all.sh` 文件添加到定时任务中, 每次更新日线数据时会自动更新ST标记;由于我程序是放在家用的小服务器中，经常遇到停电断网导致ST标记缺失。需要补齐ST标记， 这里分享[优矿](https://uqer.datayes.com/)更新ST标识的脚本:

``` python
"""
增量获取历年来的股票ST标志信息
"""
import time
import datetime
import pandas as pd

filename = "st.csv"

def str_to_datetime(_date):
    """将字符串转换成datetime类型"""
    try:
        return datetime.datetime.strptime(str(_date), "%Y-%m-%d")
    except Exception as ex:
        print("----->%s" % str(ex))


def datetime_to_str(date):
    """将datetime类型转换为日期型字符串,格式为2008-08-02"""
    return str(date)[0:10]


def next_day(date):
    """
    获取某个日期的下一日
    :param date: str xxxx-xx-xx 格式
    :return:
    """
    if len(date) <= 0:
        return u""
    
    current = str_to_datetime(date)
    delta = datetime.timedelta(days=1)
    target = current + delta
    return datetime_to_str(target)


def last_date(filename):
    """
    获取上次抓取ST股的日期
    没找到返回空字符串
    """
    try:
        idx_df = pd.read_csv(filename)
        item_last = idx_df.loc[idx_df.index[-1]]
        return str(item_last["tradeDate"])
    except Exception, ex:
        return u""


def main():
    print("开始更新股票的ST状态信息:")
    while True:
        try:
            _append = True
            start = next_day(last_date(filename))
            if len(start) <= 0:
                start = "1998-01-01"
                _append = False

            now_time = datetime.datetime.now()
            end_time = str_to_datetime(start)
            if end_time > now_time:
                raise Exception("当前ST信息已是最新, 无需更新.")

            end_time += datetime.timedelta(days=6*30)
            if now_time > end_time:
                end = end_time.strftime("%Y-%m-%d")
            else:
                end = now_time.strftime("%Y-%m-%d")

            print("\t开始更新 %s 至 %s 之间的ST信息" % (start, end))

            df = DataAPI.SecSTGet(beginDate=start.replace('-', ''),endDate=end.replace('-', ''),secID=u"",ticker=u"",field=["tradeDate", "ticker", "exchangeCD", "tradeAbbrName", "STflg"], pandas="1")

            df = df.sort_values(['tradeDate'], ascending=1)
            if _append:
                df.to_csv(filename, index=False, header=False, mode='a+',encoding='utf8')
            else:
                df.to_csv(filename, index=False, mode="w", encoding='utf8')

        except Exception as ex:
                print("\t更新 股票的ST状态信息 失败, 详细错误信息: %s" % str(ex))
                break

    print("股票的ST状态已更新完毕!")

main()
```

更新完成后, 下载替换 `/data/st.csv` 即可!