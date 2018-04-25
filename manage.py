# coding:utf8
from app import app
from flask_script import Manager


manager = Manager(app)

if __name__ == "__main__":
    # Manager 可以帮flask程序指定端口
    manager.run()
