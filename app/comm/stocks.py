"""

"""
import pandas as pd

from struct import *
from zipfile import ZipFile

from configure import *
from app.comm import file_list_in_path

# 深交所股票代码规则
# 新证券代码编码规则升位后的证券代码采用6位数字编码，编码规则定义如下：顺序编码区：6位代码中的第3位到第6位，取值范围为0001-9999。
# 证券种类标识区：6位代码中的最左两位，其中第1位标识证券大类，第2位标识该大类下的衍生证券。
# 第1位、第2位、第3-6位，定义00xxxx A股证券，03xxxx A股A2权证，07xxxx A股增发，08xxxx A股A1权证，09xxxx A股转配，10xxxx 国债现货，
# 11xxxx 债券，12xxxx 可转换债券，13xxxx 国债回购, 150XXX是深市分级基金, 17xxxx 原有投资基金，18xxxx 证券投资基金，20xxxx B股证券，27xxxx B股增发，
# 28xxxx B股权证，30xxxx 创业板证券，37xxxx 创业板增发，38xxxx 创业板权证，39xxxx 综合指数/成份指数。
#
# 上交所股票代码规则
# 在上海证券交易所上市的证券，根据上交所“证券编码实施方案”，采用6位数编制方法，前3位数为区别证券品种，具体见下表所列：
# 001×××国债现货；110×××120×××企业债券；129×××100×××可转换债券；201×××国债回购；310×××国债期货；500×××510×××基金；
# 600×××A股；700×××配股；710×××转配股；701×××转配股再配股；711×××转配股再转配股；720×××红利；730×××新股申购；
# 735×××新基金申购；737×××新股配售；900×××B股。
#
# sh:
# 000xxx  指数
# 019xxx  上海债券
# 11xxxx  上海债券
# 12xxxx  上海债券
# 13xxxx  上海债券
# 14xxxx  上海债券
# 50xxxx  基金
# 51xxxx  基金
# 60xxxx  A股个股
# 900xxx  B股个股
#
#
# sz:
# 00xxxx  A股个股
# 111xxx  债券
# 120xxx  债券
# 150xxx  分级基金
# 159xxx  基金
# 16xxxx  基金
# 200xxx  B股个股
# 30xxxx  创业板
# 399xxx  指数

def market_with_code(code:str):
    """
    :param str code: 六位数的股票代码
    :return: 0 深交所, 1 上交所
    """
    if code.startswith("00") or code.startswith("30") or code.startswith("399") or \
        code.startswith("15") or code.startswith("16"):
        return 0
    return 1


REPORT_PUBLISH_BUFFER = {}  # 股市财报披露数据的全局缓存
def report_publish_time(_date, code):
    """
    获取某一季度中, 某只股票财报信息的实际披露时间
    :param _date:
    :param code:
    :return:
    """
    global REPORT_PUBLISH_BUFFER
    try:
        result_df = REPORT_PUBLISH_BUFFER.get(_date, None)
        if result_df is None or len(result_df) <= 0:
            REPORT_PUBLISH_BUFFER[_date] = pd.read_csv(config.get("files").get("rt_item") % (PROJECT_ROOT, _date), header=0)
            REPORT_PUBLISH_BUFFER[_date]['code'] = REPORT_PUBLISH_BUFFER[_date]['code'].map(lambda x: str(x).zfill(6))
            REPORT_PUBLISH_BUFFER[_date] = REPORT_PUBLISH_BUFFER[_date].fillna(0)

            REPORT_PUBLISH_BUFFER[_date]["act"] = REPORT_PUBLISH_BUFFER[_date]["act"].astype('str')
            REPORT_PUBLISH_BUFFER[_date]["change"] = REPORT_PUBLISH_BUFFER[_date]["change"].astype('str')
            REPORT_PUBLISH_BUFFER[_date]["first"] = REPORT_PUBLISH_BUFFER[_date]["first"].astype('str')

        filter_df = REPORT_PUBLISH_BUFFER[_date][REPORT_PUBLISH_BUFFER[_date]['code'] == code]
        if len(filter_df) <= 0:
            return _date

        if filter_df.values[0][3] != '0': return filter_df.values[0][3]
        if filter_df.values[0][2] != '0': return filter_df.values[0][2]
        if filter_df.values[0][1] != '0': return filter_df.values[0][1]
    except FileNotFoundError as ex:
        pass

    return _date


def stock_a_list():
    """获取沪深股票列表"""
    try:
        base_df = pd.read_csv(config.get("files").get("stocks"), header=0)
        base_df['code'] = base_df['code'].map(lambda x: str(x).zfill(6))

        filter_df = base_df[((base_df['code'].str.startswith("00")) & (base_df['market'] == 0)) |
                            ((base_df['code'].str.startswith("30")) & (base_df['market'] == 0)) |
                            ((base_df['code'].str.startswith("60")) & (base_df['market'] == 1))]

        filter_df = filter_df.reset_index()
        return filter_df
    except Exception as ex:
        print(str(ex))
        return None


def index_a_list():
    """获取沪深股指列表"""
    try:
        base_df = pd.read_csv(config.get("files").get("stocks"), header=0)
        base_df['code'] = base_df['code'].map(lambda x: str(x).zfill(6))
        filter_df = base_df[((base_df['code'].str.startswith("399")) & (base_df['market'] == 0)) |
                            ((base_df['code'].str.startswith("000")) & (base_df['market'] == 1))]

        filter_df = filter_df.sort_index(ascending=False)
        return filter_df
    except Exception as ex:
        print(str(ex))
        return None


def funds_a_list():
    """获取沪深基金列表"""
    try:
        base_df = pd.read_csv(config.get("files").get("stocks"), header=0)
        base_df['code'] = base_df['code'].map(lambda x: str(x).zfill(6))
        filter_df = base_df[((base_df['code'].str.startswith("15")) & (base_df['market'] == 0)) |
                            ((base_df['code'].str.startswith("16")) & (base_df['market'] == 0)) |
                            ((base_df['code'].str.startswith("50")) & (base_df['market'] == 1)) |
                            ((base_df['code'].str.startswith("51")) & (base_df['market'] == 1)) ]

        filter_df = filter_df.sort_index(ascending=False)
        return filter_df
    except Exception as ex:
        print(str(ex))
        return None


def all_list_except_bond():
    """获取股票、基金、指数"""
    try:
        base_df = pd.read_csv(config.get("files").get("stocks"), header=0)
        base_df['code'] = base_df['code'].map(lambda x: str(x).zfill(6))
        filter_df = base_df[((base_df['code'].str.startswith("00")) & (base_df['market'] == 0)) |
                            ((base_df['code'].str.startswith("30")) & (base_df['market'] == 0)) |
                            ((base_df['code'].str.startswith("60")) & (base_df['market'] == 1)) |

                            ((base_df['code'].str.startswith("399")) & (base_df['market'] == 0)) |
                            ((base_df['code'].str.startswith("000")) & (base_df['market'] == 1)) |

                            ((base_df['code'].str.startswith("15")) & (base_df['market'] == 0)) |
                            ((base_df['code'].str.startswith("16")) & (base_df['market'] == 0)) |
                            ((base_df['code'].str.startswith("50")) & (base_df['market'] == 1)) |
                            ((base_df['code'].str.startswith("51")) & (base_df['market'] == 1)) ]

        filter_df = filter_df.sort_index(ascending=True)
        return filter_df
    except Exception as ex:
        print(str(ex))
        return None


# todo 可以根据需求再增加创业版，指数，债券等信息


def _report_list(_date, code=None):
    """
    获取指定日期中某只股票或者所有股票的财报信息
    :param _date: yyyy-mm-dd
    :param code:
    :return:
    """
    item_all_list = []

    file_name = 'gpcw%s' % _date
    file_path = "%s/data/reports/%s.zip" % (PROJECT_ROOT, file_name)
    if not os.path.isfile(file_path):
        return None

    with ZipFile(file_path) as myzip:
        with myzip.open('%s.dat' % file_name) as cw_file:
            cw_data = cw_file.read()

            header_size = calcsize("<3h1H3L")
            stock_item_size = calcsize("<6s1c1L")
            data_header = cw_data[:header_size]
            stock_header = unpack("<3h1H3L", data_header)
            max_count = stock_header[3]
            for stock_idx in range(0, max_count):
                start = header_size + stock_idx * stock_item_size
                si = cw_data[start:start + stock_item_size]
                stock_item = unpack("<6s1c1L", si)
                _code = stock_item[0].decode()
                if code is not None:
                    if _code == code:
                        foa = stock_item[2]
                        tmp_size = calcsize('<264f')
                        info_data = cw_data[foa:foa + tmp_size]
                        cw_info_list = unpack('<264f', info_data)
                        cw_info_list = list(map((lambda x: 0.0 if x < -1000000000.0 else x), cw_info_list))

                        item_info_list = [_date, _code]
                        item_info_list.extend(cw_info_list)
                        item_all_list.append(item_info_list)
                else:
                    foa = stock_item[2]
                    info_data = cw_data[foa:foa + calcsize('<264f')]
                    cw_info_list = unpack('<264f', info_data)
                    cw_info_list = list(map((lambda x: 0.0 if x < -1000000000.0 else x), cw_info_list))

                    item_info_list = [_date, _code]
                    item_info_list.extend(cw_info_list)
                    item_all_list.append(item_info_list)

    return item_all_list


def report_list(code=None, _date=None):
    """
    获取财报信息
    :param code: 指定股票
    :param _date: yyyymmdd 指定日期
    :return:
    * 什么参数不指定返回所有股票的最后一季财报信息。
    * 仅指定code，返回该股票历年所有的财报信息。
    * 仅指定date，返回该日期所有股票的财报信息
    :notice :
    ————-每股指标—————————–
    | 1–基本每股收益 | 2–扣除非经常性损益每股收益 | 3–每股未分配利润 | 4–每股净资产 |
    | 5–每股资本公积金 | 6–净资产收益率 | 7–每股经营现金流量 |                 |
    ————-资产负债表—————————-
    | 8.货币资金 | 9.交易性金融资产 | 10.应收票据 | 11.应收账款 | 12.预付款项 | 13.其他应收款 |
    | 14.应收关联公司款 | 15.应收利息 | 16.应收股利 | 17.存货 | 18.其中：消耗性生物资产 |
    | 19.一年内到期的非流动资产 | 20.其他流动资产 | 21.流动资产合计 | 22.可供出售金融资产 |
    | 23.持有至到期投资 | 24.长期应收款 | 25.长期股权投资 | 26.投资性房地产 | 27.固定资产 |
    | 28.在建工程 | 29.工程物资 | 30.固定资产清理 | 31.生产性生物资产 | 32.油气资产 | 33.无形资产 |
    | 34.开发支出 | 35.商誉 | 36.长期待摊费用 | 37.递延所得税资产 | 38.其他非流动资产 | 39.非流动资产合计 |
    | 40.资产总计 | 41.短期借款 | 42.交易性金融负债 | 43.应付票据 | 44.应付账款 | 45.预收款项 | 46.应付职工薪酬 |
    | 47.应交税费 | 48.应付利息 | 49.应付股利 | 50.其他应付款 | 51.应付关联公司款 | 52.一年内到期的非流动负债
    | 53.其他流动负债 | 54.流动负债合计 | 55.长期借款 | 56.应付债券 | 57.长期应付款 | 58.专项应付款 |
    | 59.预计负债 | 60.递延所得税负债 | 61.其他非流动负债 | 62.非流动负债合计 | 63.负债合计 |
    | 64.实收资本（或股本）| 65.资本公积 | 66.盈余公积 | 67.减：库存股 | 68.未分配利润 |
    | 69.少数股东权益 | 70.外币报表折算价差 | 71.非正常经营项目收益调整 | 72.所有者权益（或股东权益）合计 |
    | 73.负债和所有者（或股东权益）合计 |

    ————-利润表—————————
    | 74.其中：营业收入 | 75.其中：营业成本 | 76.营业税金及附加 | 77.销售费用 | 78.管理费用 |
    | 79.堪探费用 | 80.财务费用 | 81.资产减值损失 | 82.加：公允价值变动净收益 | 83.投资收益 |
    | 84.其中：对联营企业和合营企业的投资收益 | 85.影响营业利润的其他科目 | 86.三、营业利润 |
    | 87.加：补贴收入 | 88.营业外收入 | 89.减：营业外支出 | 90.其中：非流动资产处置净损失 |
    | 91.加：影响利润总额的其他科目 | 92.四、利润总额 | 93.减：所得税 | 94.加：影响净利润的其他科目 |
    | 95.五、净利润 | 96.归属于母公司所有者的净利润 | 97.少数股东损益 |

    ——————现金流量表———————
    | 98.销售商品、提供劳务收到的现金 | 99.收到的税费返还 | 100.收到其他与经营活动有关的现金 |
    | 101.经营活动现金流入小计 | 102.购买商品、接受劳务支付的现金 | 103.支付给职工以及为职工支付的现金 |
    | 104.支付的各项税费 | 105.支付其他与经营活动有关的现金 | 106.经营活动现金流出小计 |
    | 107.经营活动产生的现金流量净额 | 108.收回投资收到的现金 | 109.取得投资收益收到的现金 |
    | 110.处置固定资产、无形资产和其他长期资产收回的现金净额 | 111.处置子公司及其他营业单位收到的现金净额 |
    | 112.收到其他与投资活动有关的现金 | 113.投资活动现金流入小计 |
    | 114.购建固定资产、无形资产和其他长期资产支付的现金 | 115.投资支付的现金 |
    | 116.取得子公司及其他营业单位支付的现金净额 | 117.支付其他与投资活动有关的现金 |
    | 118.投资活动现金流出小计 | 119.投资活动产生的现金流量净额 | 120.吸收投资收到的现金 |
    | 121.取得借款收到的现金 | 122.收到其他与筹资活动有关的现金 | 123.筹资活动现金流入小计 |
    | 124.偿还债务支付的现金 | 125.分配股利、利润或偿付利息支付的现金 | 126.支付其他与筹资活动有关的现金 |
    | 127.筹资活动现金流出小计 | 128.筹资活动产生的现金流量净额 | 129.四、汇率变动对现金的影响 |
    | 130.四(2)、其他原因对现金的影响 | 131.五、现金及现金等价物净增加额 | 132.期初现金及现金等价物余额 |
    | 133.期末现金及现金等价物余额 | 134.净利润 | 135.加：资产减值准备 |
    | 136.固定资产折旧、油气资产折耗、生产性生物资产折旧 | 137.无形资产摊销 | 138.长期待摊费用摊销 |
    | 139.处置固定资产、无形资产和其他长期资产的损失 | 140.固定资产报废损失 | 141.公允价值变动损失 |
    | 142.财务费用 | 143.投资损失 | 144.递延所得税资产减少 | 145.递延所得税负债增加 | 146.存货的减少 |
    | 147.经营性应收项目的减少 | 148.经营性应付项目的增加 | 149.其他 | 150.经营活动产生的现金流量净额2 |
    | 151.债务转为资本 | 152.一年内到期的可转换公司债券 | 153.融资租入固定资产 | 154.现金的期末余额 |
    | 155.减：现金的期初余额 | 156.加：现金等价物的期末余额 | 157.减：现金等价物的期初余额 |
    | 158.现金及现金等价物净增加额 |

    ———————偿债能力分析————————
    | 159.流动比率 | 160.速动比率 | 161.现金比率 | 162.利息保障倍数 | 163.非流动负债比率 |
    | 164.流动负债比率 | 165.现金到期债务比率 | 166.有形资产净值债务率 | 167.权益乘数(%) |
    | 168.股东的权益/负债合计(%) | 169.有形资产/负债合计(%) | 170.经营活动产生的现金流量净额/负债合计(%) |
    | 171.EBITDA/负债合计(%) |

    ———————经营效率分析————————
    | 172.应收帐款周转率 | 173.存货周转率 | 174.运营资金周转率 | 175.总资产周转率 | 176.固定资产周转率 |
    | 177.应收帐款周转天数 | 178.存货周转天数 | 179.流动资产周转率 | 180.流动资产周转天数 |
    | 181.总资产周转天数 | 182.股东权益周转率 |

    ———————发展能力分析————————
    | 183.营业收入增长率 | 184.净利润增长率 | 185.净资产增长率 | 186.固定资产增长率 | 187.总资产增长率 |
    | 188.投资收益增长率 | 189.营业利润增长率 | 190.暂无 | 191.暂无 | 192.暂无 |

    ———————获利能力分析————————
    | 193.成本费用利润率(%) | 194.营业利润率 | 195.营业税金率 | 196.营业成本率 | 197.净资产收益率 |
    | 198.投资收益率 | 199.销售净利率(%) | 200.总资产报酬率 | 201.净利润率 | 202.销售毛利率(%) |
    | 203.三费比重 | 204.管理费用率 | 205.财务费用率 | 206.扣除非经常性损益后的净利润 |
    | 207.息税前利润(EBIT) | 208.息税折旧摊销前利润(EBITDA) | 209.EBITDA/营业总收入(%) |

    ———————资本结构分析———————
    | 210.资产负债率(%) | 211.流动资产比率 | 212.货币资金比率 | 213.存货比率 | 214.固定资产比率 |
    | 215.负债结构比 | 216.归属于母公司股东权益/全部投入资本(%) | 217.股东的权益/带息债务(%) |
    | 218.有形资产/净债务(%) |

    ———————现金流量分析———————
    | 219.每股经营性现金流(元) | 220.营业收入现金含量(%) | 221.经营活动产生的现金流量净额/经营活动净收益(%) |
    | 222.销售商品提供劳务收到的现金/营业收入(%) | 223.经营活动产生的现金流量净额/营业收入 | 224.资本支出/折旧和摊销 |
    | 225.每股现金流量净额(元) | 226.经营净现金比率（短期债务） | 227.经营净现金比率（全部债务） |
    | 228.经营活动现金净流量与净利润比率 | 229.全部资产现金回收率 |

    ———————单季度财务指标———————
    | 230.营业收入 | 231.营业利润 | 232.归属于母公司所有者的净利润 | 233.扣除非经常性损益后的净利润 |
    | 234.经营活动产生的现金流量净额 | 235.投资活动产生的现金流量净额 | 236.筹资活动产生的现金流量净额 |
    | 237.现金及现金等价物净增加额 |

    ———————股本股东———————
    | 238.总股本 | 239.已上市流通A股 | 240.已上市流通B股 | 241.已上市流通H股 | 242.股东人数(户) |
    | 243.第一大股东的持股数量 | 244.十大流通股东持股数量合计(股) | 245.十大股东持股数量合计(股) |

    ———————机构持股———————
    | 246.机构总量（家） | 247.机构持股总量(股) | 248.QFII机构数 | 249.QFII持股量 | 250.券商机构数 |
    | 251.券商持股量 | 252.保险机构数 | 253.保险持股量 | 254.基金机构数 | 255.基金持股量 | 256.社保机构数 |
    | 257.社保持股量 | 258.私募机构数 | 259.私募持股量 | 260.财务公司机构数 | 261.财务公司持股量 |
    | 262.年金机构数 | 263.年金持股量 |

    ———————新增指标———————
    | 264.十大流通股东中持有A股合计(股) [注：季度报告中，若股东同时持有非流通A股性质的股份(如同时持有流通A股和流通B股）,
      指标264取的是包含同时持有非流通A股性质的流通股数] |
    """
    all_date_list = []   # 所有财报日期
    file_list = file_list_in_path("%s/data/reports/" % PROJECT_ROOT)

    headers = ['date', 'code']
    headers.extend([idx for idx in range(1, 265)])

    for file_name in file_list:
        if file_name.startswith("."):
            continue

        file_name = file_name.split('.')[0]
        ymd_str = file_name[4:]
        all_date_list.append(ymd_str)

    if _date is not None:
        if _date not in all_date_list:
            print("指定的财报日期不存在, 请确认财报数据是否已是最新或者重新指定!")
            return pd.DataFrame([], columns=headers)
        # 指定某一个日期了可以直接得到此日期的文件
        _result_df = pd.DataFrame(_report_list(_date, code), columns=headers)
        _result_df['code'] = _result_df['code'].map(lambda x: str(x).zfill(6))
        return _result_df

    report_result = []
    for current in all_date_list:
        _result_df = _report_list(current, code)
        report_result.extend(_result_df)

    _result_df = pd.DataFrame(_report_list(_date, code), columns=headers)
    _result_df['code'] = _result_df['code'].map(lambda x: str(x).zfill(6))
    return _result_df


if __name__ == "__main__":
    report_publish_time("20171231", "000001")
    # import datetime
    #
    # stock_df = pd.DataFrame()
    # start = datetime.datetime.now()
    # result_df = report_list("000001", "20171231")
    # result_df = result_df.sort_values(['date'], ascending=1)
    # print("分红: %f" % result_df[125])
    # print("总股本: %f" % result_df[238])
    # print("流通股本: %f" % result_df[239])
    # end = datetime.datetime.now()
    #
    # m, s = divmod((end - start).seconds, 60)
    # h, m = divmod(m, 60)
    # print("耗时: %d:%02d:%02d" % (h, m, s))s
    # stock_df["date"] = result_df["date"]
    # stock_df["code"] = result_df["code"]
    # stock_df[95] = result_df[95]
    # stock_df[96] = result_df[96]     # 归属于母公司所有者的净利润
    # stock_df[206] = result_df[206]
    # stock_df[233] = result_df[233]
    # stock_df[238] = result_df[238]
    # stock_df[239] = result_df[239]
    #
    # stock_df.to_csv("/Users/datochan/WorkSpace/PycharmProjects/DatoQuant/data/base/000017.csv",
    #                 index=False, mode="w", encoding='utf8')
