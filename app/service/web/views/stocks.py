# -*- coding: utf-8 -*-
"""
    stocks
    ~~~~~~~~~~~~~~
    获取股票相关的信息

    :copyright: (c) 18/11/21 by datochan.
"""

from app.service.web import webapp

@webapp.route('/stock/<code>', methods=['GET', 'POST'])
def stock(code):
    """获取某只股票的详情"""
    pass

