# coding:utf8
from flask import render_template, redirect, url_for, flash, session, request

from app import db
from app.admin import admin
from app.admin.forms import LoginForm, TagForm
from app.models import Admin, Tag
from functools import wraps


def admin_login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' not in session:
            return redirect(url_for('admin.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@admin.route("/")
@admin_login_req
def index():
    return render_template('admin/index.html')


@admin.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        admin_i = Admin.query.filter_by(name=data['account']).first()
        print(admin)
        if not admin_i.check_pwd(data['pwd']):
            flash("密码错误")
            return redirect(url_for('admin.login'))
        session['admin'] = data['account']
        return redirect(request.args.get("next") or url_for('admin.index'))

    return render_template('admin/login.html', form=form)


@admin.route("/logout")
@admin_login_req
def logout():
    session.pop('admin', None)
    return redirect(url_for("admin.login"))


@admin.route("/pwd")
@admin_login_req
def pwd():
    return render_template("admin/pwd.html")


@admin.route("/tag/add", methods=['get', 'post'])
@admin_login_req
def tag_add():
    tag_form = TagForm()
    if tag_form.validate_on_submit():
        data = tag_form.data
        tag = Tag.query.filter_by(name=data['name']).count()
        if tag == 1:
            flash("名称已存在", "err")
            return redirect(url_for('admin.tag_add'))
        tag = Tag(
            name=data['name']
        )
        db.session.add(tag)
        db.session.commit()
        flash('添加标签成功', 'ok')
        return redirect(url_for('admin.tag_add'))
    return render_template("admin/tag_add.html", form=tag_form)


# 标签列表
@admin.route("/tag/list/<int:page>/", methods=['get', 'post'])
@admin_login_req
def tag_list(page=None):
    if page is None:
        page = 1
    page_data = Tag.query.order_by(
        Tag.add_time.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/tag_list.html", page_data=page_data)


# 标签编辑删除
@admin.route('/tag/del/<int:id>/', methods=['GET'])
@admin_login_req
def tag_del(id=None):
    tag = Tag.query.filter_by(id=id).first_or_404()
    db.session.delete(tag)
    db.session.commit()
    flash('删除成功', 'ok')
    return redirect(url_for('admin.tag_list', page=1))


@admin.route("/movie/add")
@admin_login_req
def movie_add():
    return render_template("admin/movie_add.html")


@admin.route("/movie/list")
@admin_login_req
def movie_list():
    return render_template("admin/movie_list.html")


@admin.route("/preview/add")
@admin_login_req
def preview_add():
    return render_template("admin/preview_add.html")


@admin.route("/preview/list")
@admin_login_req
def preview_list():
    return render_template("admin/preview_list.html")


@admin.route("/user/list")
@admin_login_req
def user_list():
    return render_template("admin/user_list.html")


@admin.route("/comment/list")
@admin_login_req
def comment_list():
    return render_template("admin/comment_list.html")


@admin.route("/movie_col/list")
@admin_login_req
def movie_col_list():
    return render_template("admin/movie_col_list.html")


@admin.route("/op_log/list")
@admin_login_req
def op_log_list():
    return render_template("admin/op_log_list.html")


@admin.route("/admin_login_log/list")
@admin_login_req
def admin_login_log_list():
    return render_template("admin/admin_login_log_list.html")


@admin.route("/user_login_log/list")
@admin_login_req
def user_login_log_list():
    return render_template("admin/user_login_log_list.html")


@admin.route("/auth/add")
@admin_login_req
def auth_add():
    return render_template("admin/auth_add.html")


@admin.route("/auth/list")
@admin_login_req
def auth_list():
    return render_template("admin/auth_list.html")


@admin.route("/role/add")
@admin_login_req
def role_add():
    return render_template("admin/role_add.html")


@admin.route("/role/list")
@admin_login_req
def role_list():
    return render_template("admin/role_list.html")


@admin.route("/admin/add")
@admin_login_req
def admin_add():
    return render_template("admin/admin_add.html")


@admin.route("/admin/list")
@admin_login_req
def admin_list():
    return render_template("admin/admin_list.html")
