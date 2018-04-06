# coding:utf8
import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config("SQLALCHEMY_DATABASE_URL") = "mysql://root:123456@localhost:3306/movie"
app.config("SQLALCHEMY_TRACK_MODIFICATIONS") = True

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    pwd = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(11), unique=True)
    info = db.Column(db.Text)
    face = db.Column(db.String(255), unique=True)
    addtime = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    uuid = db.Column(db.String(255), unique=True)
    userlogs = db.relationship("Userlog", backref="user") # 外键关系关联

    def __repr__(self):
        return "<User %r>" % self.name

class Userlog(db.Model):
    __tablename__ = "userlog"
    id = db.column(db.Integer, primary_key=True)
    user_id = db.column(db.Integer, db.ForeignKey('user.id'))
    ip = db.column(db.String(100))
    addtime = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return "<Userlog %r>" % self.id
