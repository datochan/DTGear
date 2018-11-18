"""
    models
    ~~~~~~~~~~~~~~
    持久层操作实例

    :copyright: (c) 18/10/19 by datochan.
"""
import json
import pandas as pd
import pymongo
from pymongo.database import Database
from pymongo.collection import Collection


class MongoDBClient:
    __client: pymongo.MongoClient
    __db: Database
    __stock: Collection

    def __init__(self, uri="mongodb://localhost:27017/", db_name="DTGear"):
        self.__client = pymongo.MongoClient(uri)
        self.__db = self.__client[db_name]
        self.__stock = self.__db["stocks"]

    def find_stock_item(self, _filter=None, _sort=None, _fields=None):
        """
        获取某只股票后复权数据最后更新时间
        :param _filter: 查询条件 如: {"code": _code, "market": _market, "fixed": {"$exists": True}}
        :param _sort: 排序条件 如: [("date", pymongo.DESCENDING)]
        :param _fields: 查询返回的字段 如: {"code": 1, "market":1}
        :return:
        """
        return self.__stock.find_one(_filter, sort=_sort, projection=_fields)

    def find_stock_list(self, _filter=None, _sort=None, _fields=None):
        """查询股票列表 todo: 待完善 暂时没有分页需求, 后补"""
        return list(self.__stock.find(_filter, sort=_sort, projection=_fields))


    def insert_json(self, _dataframe:pd.DataFrame):
        if _dataframe.empty:
            return
        self.__stock.insert_many(json.loads(_dataframe.to_json(orient='records')))

    def upsert_one(self, _market, _code:str, _date:str, _value, _upsert=True):
        """
        有则更新，无则插入
        :param _market:
        :param _code:
        :param _date:
        :param _value:
        :param _upsert: 如果要更新的数据不存在是否插入
        :return:
        """
        try:
            self.__stock.update_one({"code": "%s" % _code, "market": _market, "date": "%s"%_date}, {
                '$set': _value
            }, upsert=_upsert)
        except Exception as ex:
            print(str(ex))

if __name__ == "__main__":
    db_client = MongoDBClient("mongodb://localhost:27017/", "DTGear")
    date = db_client.find_stock_item({"code": "399001", "market": 0})
    print("hello world!")