# coding:utf8
from flask import Flask, render_template
from app.home import home as home_blueprint
from app.admin import admin as admin_blueprint
from flask_sqlalchemy import SQLAlchemy
import pymysql

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:123456@localhost:3306/movie"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.debug = True
db = SQLAlchemy(app)

app.register_blueprint(home_blueprint)
app.register_blueprint(admin_blueprint, url_prefix="/admin")


@app.errorhandler(404)
def page_not_found(error):
    print(error)
    return render_template('home/404.html'), 404
