# -*- coding: utf-8 -*-
"""
    common.lib.extensions
    ~~~~~~~~~~~~~~
    项目的扩展模块, 如果有新的扩展可在这里添加集中导入.

    :copyright: (c) 2016-1-26 by datochan.
"""
from flask_pymongo import PyMongo
from flask_mako import MakoTemplates

__all__ = ['mongo', 'mako']
mongo = PyMongo()
mako = MakoTemplates()
