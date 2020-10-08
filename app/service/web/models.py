from app.comm.lib.extensions import mongo


class StockModel:
    __stock = None

    def __init__(self):
        self.__stock = mongo.db.stocks

    def stock_list(self, _filter=None, _sort=None, _fields=None):
        """获取指定指数的PB值列表"""
        return self.__stock.find(_filter, sort=_sort, projection=_fields)

    def stock_item(self, _filter=None, _sort=None, _fields=None):
        """
        :param _filter: 查询条件 如: {"code": _code, "market": _market, "fixed": {"$exists": True}}
        :param _sort: 排序条件 如: [("date", pymongo.DESCENDING)]
        :param _fields: 查询返回的字段 如: {"code": 1, "market":1}
        :return:
        """
        return self.__stock.find_one(_filter, sort=_sort, projection=_fields)
