"""
    配置信息
    ~~~~~~~~~~~~~~
    项目的基础配置信息.

    :copyright: (c) 2016-10-26 by datochan.
"""
import os
import logging
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

config = {
    "logger": {
        "level": logging.DEBUG,
        "format": '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
        "filename": "dtgear-%s.log" % str(datetime.now())[:10]
    },
    "urls": {
        "stock_fin": "http://down.tdx.com.cn:8001/fin",
        "fin_list_file": "gpcw.txt",  # 财务数据文件列表

        'china_bond_list': 'http://yield.chinabond.com.cn/cbweb-pbc-web/pbc/historyQuery?startDate=%s&endDate=%s'
                           '&gjqx=0&qxId=hzsylqx&locale=cn_ZH',
        'china_bond_item': 'http://yield.chinabond.com.cn/cbweb-pbc-web/pbc/queryGjqxInfo?&workTime=%s&locale=cn_ZH',
        "server_time": "https://s.thsi.cn/js/chameleon/time.%d.js",  # 用于更新同花顺服务器时间解密cookie信息
        "report_time": "http://data.10jqka.com.cn/financial/yypl/date/%s/board/ALL/field/stockcode/order/DESC/page/%d/ajax/1/"
    },
    "files": {
        'calendar': "%s/data/calendar.csv" % PROJECT_ROOT,  # 股票交易日历
        'bond': "%s/data/bond.csv" % PROJECT_ROOT,
        'stocks': "%s/data/stocks.csv" % PROJECT_ROOT,
        'stock_a': "%s/data/a.csv" % PROJECT_ROOT,
        'plots1': "%s/data/plots1.csv" % PROJECT_ROOT,
        'st': "%s/data/st.csv" % PROJECT_ROOT,
        'bonus': "%s/data/bonus.csv" % PROJECT_ROOT,
        'reports': "%s/data/reports.csv" % PROJECT_ROOT,         # 股票财报目录
        'report_item': "%s/data/reports/%s.zip",  # 股票财报目录
        'rt_item': "%s/data/reports/rt%s.csv",  # 股票财报目录
        'index': "%s/data/indexes/%s.csv",    # 指定指数的历史成分列表
    },
    "tdx": {
        "server1": {
            "host": "121.14.110.200",
            "port": 443
        },
        "server2": {
            "host": "121.14.110.200",
            "port": 443
        },

    },
    "db": {
        "mongodb": "mongodb://localhost:27017/",
        "database": "DTGear"
    }
}


class Config:
    def __init__(self):
        pass

    CACHE_TYPE = "simple"
    CACHE_DEFAULT_TIMEOUT = 300

    SECRET_KEY = 'hard to guess string'
    SSL_DISABLE = True

    LOGGER_LEVEL = logging.DEBUG
    LOGGER_FORMAT = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
    LOGGER_DATE_FORMAT = '%a, %d %b %Y %H:%M:%S'
    LOGGER_FILENAME = 'dtgear.log'
    LOGGER_FILEMODE = 'w'

    MONGO_URI = "%s%s"% (config.get("db").get("mongodb"), config.get("db").get("database"))
    MAKO_TRANSLATE_EXCEPTIONS = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    pass


# web应用的基础配置
settings = {
    "dev": DevelopmentConfig
}
