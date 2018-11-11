import click
import pandas as pd

from app import comm
from app.comm import stocks
from configure import PROJECT_ROOT, config


@click.group()
def convert():
    """更新类功能集合"""
    pass


@convert.command(help="转换股票财报数据的指标")
def report():
    """
    转换PE、PB、ROE、股息率 四个指标需要的信息
    1.基本每股收益、4.每股净资产、96.归属于母公司所有者的净利润、238.总股本、239.已上市流通A股
        PE=股价/利润
        PB=股价/每股净资产
        ROE=利润/每股净资产
        因此：PB=PE*ROE
        总市值=当前股价×总股本
    """
    click.echo("转换股票财报数据的指标...")

    all_date_list = []
    file_list = comm.file_list_in_path("%s/data/reports/" % PROJECT_ROOT)

    for file_name in file_list:
        if file_name.startswith(".") or file_name.startswith("rt"):
            continue

        file_name = file_name.split('.')[0]
        ymd_str = file_name[4:]
        all_date_list.append(ymd_str)

    all_date_list.sort()

    is_first = True
    for date_item in all_date_list:

        click.echo("\t开始转换 %s 的财报数据..." % date_item)
        report_list = []
        report_df = stocks.report_list(_date=date_item)

        for idx, row in report_df.iterrows():
            market = stocks.market_with_code(row['code'])
            act = stocks.report_publish_time(row['date'], row['code'])
            report_list.append([row['date'], market, row['code'], row[1], row[2], row[4], row[96], row[238], row[239], act])

        #date, market, code, 1.基本每股收益、2.扣非每股收益、4.每股净资产、96.归属于母公司所有者的净利润、238.总股本、239.已上市流通A股、披露时间
        result_df = pd.DataFrame(report_list, columns=['date', 'market', 'code', 'eps', 'neps','bps', 'np', 'tcs', 'ccs', "publish"])

        result_df = result_df.sort_values(['code'], ascending=1)
        if is_first is True:
            result_df.to_csv(config.get("files").get("reports"), index=False, header=True, mode='w',
                             encoding='utf8')
            is_first = False
        else:
            result_df.to_csv(config.get("files").get("reports"), index=False, header=False, mode='a+',
                             encoding='utf8')
    click.echo("股票财报数据转换完毕...")

