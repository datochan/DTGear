"""
启动WEB服务
"""
from flask_script import Manager
from app.service import web
from app.service.web import webapp

APP_MODULES = (
    {"entry": webapp},
)


app = web.create_app("dev", APP_MODULES)
manager = Manager(app)

if __name__ == '__main__':
    manager.run()
