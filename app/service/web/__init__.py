# -*- coding: utf-8 -*-
"""
    common.lib.bootstrap
    ~~~~~~~~~~~~~~
    项目的入口文件, 用来启动项目加载相应的模块.

    :copyright: (c) 2016-1-26 by datochan.
"""
import os
from flask import Flask
from flask import Blueprint
from app.comm.lib.extensions import mongo, mako
from configure import settings

PROJECT_WEB_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)), "materials")

webapp = Blueprint("webapp", __name__)


def configure_extensions(app):
    """初始化现有组件"""
    mongo.init_app(app)
    mako.init_app(app)


def configure_modules(app, modules):
    for module in modules:
        app.register_blueprint(module.get("entry", None), url_prefix=module.get("prefix", None))


def create_app(config_name=None, modules=None):
    """创建WEB服务器"""
    if modules is None:
        modules = []

    app = Flask("DTGear", template_folder=os.path.join(PROJECT_WEB_ROOT, "tpl"),
                   static_folder=os.path.join(PROJECT_WEB_ROOT, "static"))
    app.config.from_object(settings.get(config_name, "default"))

    configure_extensions(app)
    configure_modules(app, modules)

    return app

from . import views