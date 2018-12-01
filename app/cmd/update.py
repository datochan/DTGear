import asyncore
import time
from datetime import timedelta

import click

import pandas as pd
from pyquery import PyQuery as pq

from app import models
from app.comm.utils import netbase, crypto
from app.service import thsi
from app.service.tdx import TdxClient
from configure import *


@click.group()
def update():
    """更新类功能集合"""
    pass


@update.command(help="更新沪深股票基础数据及权息数据")
def basics():
    click.echo("开始更新沪深股票基础数据及权息数据...")

    def __update():
        c1.data_gen = c1.update_base()
        c1.proxy.send(next(c1.data_gen))

    c1 = TdxClient(callback=__update)
    c1.connect(config.get("tdx").get("server1").get("host"), config.get("tdx").get("server1").get("port"))

    asyncore.loop(timeout=10.0)

    click.echo("沪深股票基础数据及权息数据更新成功!")


@update.command(help="更新股票日线的交易数据")
def days():
    click.echo("开始更新股票日线数据...")
    def __update():
        # 当前交易日时，交易未结束则更新到昨天，交易结束则更新到今天。
        c1.data_gen = c1.update_history()
        c1.proxy.send(next(c1.data_gen))

    db_client = models.MongoDBClient(config.get("db").get("mongodb"), config.get("db").get("database"))

    c1 = TdxClient(db_client=db_client, callback=__update)
    c1.connect(config.get("tdx").get("server1").get("host"), config.get("tdx").get("server1").get("port"))

    asyncore.loop(timeout=10.0)  # 数据更新结束后会自动退出


@update.command(help="更新指数成分股")
def index():
    """todo 从金融街爬取成分股信息"""
    pass


@update.command(help="更新ST信息")
def st():
    db_client = models.MongoDBClient(config.get("db").get("mongodb"), config.get("db").get("database"))

    st_df = pd.read_csv(config.get("files").get("st"), header=0)
    st_df['code'] = st_df['code'].map(lambda x: str(x).zfill(6))

    for index, row in st_df.iterrows():
        db_client.upsert_one(_filter={"code": str(row["code"]), "market": row["market"], "date": str(row["date"])},
                             _value={"st": 1, "name": "%s"%row['name']}, _upsert=False)
        print("更新记录: %d" % index)


@update.command(help="更新股票财报信息")
def report():
    """更新基础财务信息"""
    # 获取所有财务数据的文件列表
    click.echo("开始更新基础财务信息...")
    data_list_url = "%s/%s" % (config.get("urls").get("stock_fin"), config.get("urls").get("fin_list_file"))
    http_client = netbase.HttpClient(data_list_url)
    content = http_client.value().decode("utf-8")
    cw_list = content.split('\n')

    # 过滤出所有需要下载更新的文件
    none_total = 0

    for idx in range(len(cw_list), 0, -1):
        # 按时间倒叙
        item = cw_list[idx-1]
        if len(item) <= 5:
            none_total += 1
            continue
        file_name = item.split(',')[0]
        file_hash = item.split(',')[1]
        file_name = file_name.split('.')[0]
        file_path = config.get("files").get("report_item") % (PROJECT_ROOT, file_name)
        hash_result = crypto.md5sum(file_path)
        click.echo("更新财报文件 %s ... " % file_name, nl=False)
        if file_hash != hash_result:
            # 如果文件已更新则删除本地文件重新下载
            if os.path.isfile(file_path):
                os.remove(file_path)

            # 下载文件
            data_client = netbase.HttpClient("%s/%s.zip" % (config.get("urls").get("stock_fin"), file_name))
            with open(file_path, 'wb') as outfile:
                outfile.write(data_client.value())
            click.echo("  更新完毕!")
        else:
            click.echo("  无变化, 不需要更新!")

    click.echo("所有基础财务数据更新完毕!")


@update.command(help="更新股票财报信息")
@click.option('--all', type=click.BOOL, default=False, help='是否更新全量数据, 默认只更新当前季度')
def rt(all):
    """
    年报: xxxx-12-31 至 xxxx-04-30
    一季: xxxx-03-31 至 xxxx-04-30
    年中: xxxx-06-30 至 xxxx-08-31
    三季: xxxx-09-30 至 xxxx-10-31
    :param all:
    :return:
    """
    print("准备更新财报披露时间数据...")
    date = None
    if all is False:
        # 如果不更新全量数据则只更新今天所属季度的部分数据
        date = "".join(time.strftime('%Y%m%d', time.localtime(time.time())))

    thsi.report_time(config.get("urls").get("server_time"), config.get("urls").get("report_time"),
                     config.get("files").get("rt_item"), date)

    print("财报披露时间数据更新完毕...")


@update.command(help="更新债券收益信息.")
def bond():
    click.echo("开始更新国债收益情况...")

    item_last = None
    result_df = pd.DataFrame([], columns=['date', '3month', '6month', '1year', '3year', '5year',
                                          '7year', '10year', '30year'])
    today = "".join(time.strftime('%Y-%m-%d', time.localtime(time.time())))
    bond_df = pd.read_csv(config.get("files").get("bond"), header=0, encoding="utf8")
    if len(bond_df) > 0:
        item_last = bond_df.loc[bond_df.index[-1]]
    last_day = datetime.strptime(str(int(item_last["date"])), "%Y%m%d")
    delta = timedelta(days=1)
    last_day = last_day + delta

    start = str(last_day)[0:10]
    click.echo("\t开始更新 %s ~ %s 的债券收益信息..." % (start, today))

    html_cnt = netbase.HttpClient(config.get('urls').get('china_bond_list') % (start, today))
    doc = pq(html_cnt.value().decode("utf-8"))

    is_header = True
    bond_list = []
    tr_list = doc("#gjqxData tr")
    for tr in tr_list.items():
        if is_header:
            # 跳过表头
            is_header = False
            continue

        if tr.children("td").length > 0:
            _date = tr.children("td").eq(1).text()
            _3_month = tr.children("td").eq(2).text()
            _6_month = tr.children("td").eq(3).text()
            _1_year  = tr.children("td").eq(4).text()
            _3_year  = tr.children("td").eq(5).text()
            _5_year  = tr.children("td").eq(6).text()
            _7_year  = tr.children("td").eq(7).text()
            _10_year  = tr.children("td").eq(8).text()
            _30_year  = tr.children("td").eq(9).text()

            bond_list.append([_date.replace('-', ''), _3_month, _6_month, _1_year, _3_year, _5_year,
                                _7_year, _10_year, _30_year])

    if len(bond_list) > 0:
        result_df = pd.DataFrame(bond_list, columns=['date', '3month', '6month', '1year', '3year', '5year',
                                                       '7year', '10year', '30year'])

    result_df = result_df.sort_values(['date'], ascending=1)
    result_df.to_csv(config.get("files").get("bond"), index=False, header=False, mode='a+',
                     encoding='utf8')

    click.echo("国债收益收据更新结束...")


@update.command(help="更新债券收益信息,第一次使用时更新，后面用bond方法更新.")
def bond_all():
    click.echo("开始更新国债收益情况...")

    start = ['2006-01-01', '2007-01-01', '2008-01-01', '2009-01-01', '2010-01-01', '2011-01-01', '2012-01-01',
             '2013-01-01', '2014-01-01', '2015-01-01', '2016-01-01', '2017-01-01', '2018-01-01']

    end = ['2006-12-31', '2007-12-31', '2008-12-31', '2009-12-31', '2010-12-31', '2011-12-31', '2012-12-31',
           '2013-12-31', '2014-12-31', '2015-12-31', '2016-12-31', '2017-12-31', '2018-12-31']

    is_first = True
    for idx in range(0, len(start)):
        click.echo("\t开始更新 %s ~ %s 的债券收益信息..." % (start[idx], end[idx]))

        html_cnt = netbase.HttpClient(config.get('urls').get('china_bond_list') % (start[idx], end[idx]))
        doc = pq(html_cnt.value().decode("utf-8"))


        is_header = True
        bond_list = []
        tr_list = doc("#gjqxData tr")
        for tr in tr_list.items():
            if is_header:
                # 跳过表头
                is_header = False
                continue

            if tr.children("td").length > 0:
                _date = tr.children("td").eq(1).text()
                _3_month = tr.children("td").eq(2).text()
                _6_month = tr.children("td").eq(3).text()
                _1_year  = tr.children("td").eq(4).text()
                _3_year  = tr.children("td").eq(5).text()
                _5_year  = tr.children("td").eq(6).text()
                _7_year  = tr.children("td").eq(7).text()
                _10_year  = tr.children("td").eq(8).text()
                _30_year  = tr.children("td").eq(9).text()

                bond_list.append([_date.replace('-', ''), _3_month, _6_month, _1_year, _3_year, _5_year,
                                    _7_year, _10_year, _30_year])

        if len(bond_list) > 0:
            result_df = pd.DataFrame(bond_list, columns=['date', '3month', '6month', '1year', '3year', '5year',
                                                           '7year', '10year', '30year'])

            result_df = result_df.sort_values(['date'], ascending=1)
            if is_first is True:
                result_df.to_csv(config.get("files").get("bond"), index=False, header=True, mode='w',
                                 encoding='utf8')
                is_first = False
            else:
                result_df.to_csv(config.get("files").get("bond"), index=False, header=False, mode='a+',
                                 encoding='utf8')

    click.echo("国债收益收据更新结束...")
