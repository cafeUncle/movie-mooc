# coding:utf8
from flask import render_template, redirect, url_for, flash, session, request
from app.admin import admin
from app.admin.forms import LoginForm
from app.models import Admin


@admin.route("/")
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
        else:
            session['admin'] = data['account']
            return redirect(request.args.get("next") or url_for('admin.index'))
        return redirect(url_for('admin.index'))

    return render_template('admin/login.html', form=form)


@admin.route("/logout")
def logout():
    return redirect(url_for("admin.login"))


@admin.route("/pwd")
def pwd():
    return render_template("admin/pwd.html")


@admin.route("/tag/add")
def tag_add():
    return render_template("admin/tag_add.html")


@admin.route("/tag/list")
def tag_list():
    return render_template("admin/tag_list.html")


@admin.route("/movie/add")
def movie_add():
    return render_template("admin/movie_add.html")


@admin.route("/movie/list")
def movie_list():
    return render_template("admin/movie_list.html")


@admin.route("/preview/add")
def preview_add():
    return render_template("admin/preview_add.html")


@admin.route("/preview/list")
def preview_list():
    return render_template("admin/preview_list.html")


@admin.route("/user/list")
def user_list():
    return render_template("admin/user_list.html")


@admin.route("/comment/list")
def comment_list():
    return render_template("admin/comment_list.html")


@admin.route("/movie_col/list")
def movie_col_list():
    return render_template("admin/movie_col_list.html")


@admin.route("/op_log/list")
def op_log_list():
    return render_template("admin/op_log_list.html")


@admin.route("/admin_login_log/list")
def admin_login_log_list():
    return render_template("admin/admin_login_log_list.html")


@admin.route("/user_login_log/list")
def user_login_log_list():
    return render_template("admin/user_login_log_list.html")


@admin.route("/auth/add")
def auth_add():
    return render_template("admin/auth_add.html")


@admin.route("/auth/list")
def auth_list():
    return render_template("admin/auth_list.html")


@admin.route("/role/add")
def role_add():
    return render_template("admin/role_add.html")


@admin.route("/role/list")
def role_list():
    return render_template("admin/role_list.html")


@admin.route("/admin/add")
def admin_add():
    return render_template("admin/admin_add.html")


@admin.route("/admin/list")
def admin_list():
    return render_template("admin/admin_list.html")
