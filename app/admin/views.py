# coding:utf8
import datetime
import os
import uuid
from functools import wraps

from flask import render_template, redirect, url_for, flash, session, request
from werkzeug.utils import secure_filename

from app import db, app
from app.admin import admin
from app.admin.forms import LoginForm, TagForm, MovieForm
from app.models import Admin, Tag, Movie, OpLog, AdminLog


# 上下文应用处理器 封装全局变量，展现到模板中
@admin.context_processor
def tpl_extra():
    data = dict(
        online_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )
    return data

def admin_login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' not in session:
            return redirect(url_for('admin.login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function


# 修改文件名称
def change_filename(filename):
    fileinfo = os.path.splitext(filename)
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + fileinfo[-1]
    return filename


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
        print(admin_i)
        if not admin_i.check_pwd(data['pwd']):
            flash("密码错误")
            return redirect(url_for('admin.login'))
        session['admin'] = data['account']
        session['admin_id'] = admin_i.id
        admin_log = AdminLog(
            admin_id=admin_i.id,
            ip=request.remote_addr
        )
        db.session.add(admin_log)
        db.session.commit()
        return redirect(request.args.get("next") or url_for('admin.index'))

    return render_template('admin/login.html', form=form)


@admin.route("/logout")
@admin_login_req
def logout():
    session.pop('admin', None)
    session.pop('admin_id', None)
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
        op_log = OpLog(
            admin_id=session['admin_id'],
            ip=request.remote_addr,
            reason="添加标签%s" % data['name']
        )
        db.session.add(op_log)
        db.session.commit()
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


# 标签删除
@admin.route('/tag/del/<int:id>/', methods=['GET'])
@admin_login_req
def tag_del(id=None):
    # tag = Tag.query.get(id=id)
    tag = Tag.query.filter_by(id=id).first_or_404()
    db.session.delete(tag)
    db.session.commit()
    flash('删除标签成功', 'ok')
    return redirect(url_for('admin.tag_list', page=1))


# 标签编辑
@admin.route('/tag/edit/<int:id>/', methods=['GET', 'POST'])
@admin_login_req
def tag_edit(id=None):
    form = TagForm()
    # tag = Tag.query.filter_by(id=id).first_or_404()
    tag = Tag.query.get_or_404(id)
    if form.validate_on_submit():
        data = form.data
        tag_count = Tag.query.filter_by(name=data['name']).count()
        if tag.name != data['name'] and tag_count == 1:
            flash("名称已存在", "err")
            return redirect(url_for('admin.tag_edit', id=id))
        tag.name = data['name']
        db.session.add(tag)
        db.session.commit()
        flash('修改标签成功', 'ok')
        return redirect(url_for('admin.tag_edit', id=id))
    return render_template('admin/tag_edit.html', form=form, tag=tag)


@admin.route("/movie/add", methods=['GET', 'POST'])
@admin_login_req
def movie_add():
    form = MovieForm()
    if form.validate_on_submit():
        data = form.data
        file_url = secure_filename(form.url.data.filename)
        file_logo = secure_filename(form.logo.data.filename)
        if not os.path.exists(app.config["UP_DIR"]):
            os.makedirs(app.config["UP_DIR"])
            os.chmod(app.config["UP_DIR"], "rw")
        url = change_filename(file_url)
        logo = change_filename(file_logo)
        form.url.data.save(app.config["UP_DIR"] + url)
        form.logo.data.save(app.config["UP_DIR"] + logo)
        movie = Movie(
            title=data['title'],
            url=url,
            info=data['info'],
            logo=logo,
            star=int(data['star']),
            play_num=0,
            comment_num=0,
            tag_id=int(data['tag_id']),
            area=data['area'],
            length=data['length'],
            release_time=data['release_time']
        )
        db.session.add(movie)
        db.session.commit()
        flash('添加电影成功', 'ok')
        return redirect(url_for('admin.movie_add', form=form))
    return render_template("admin/movie_add.html", form=form)


@admin.route("/movie/list/<int:page>", methods=['GET'])
@admin_login_req
def movie_list(page=None):
    if page is None:
        page = 1
    page_data = Movie.query.join(Tag).filter(
        Movie.tag_id == Tag.id
    ).order_by(
        Movie.add_time.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/movie_list.html", page_data=page_data)


@admin.route('/movie/del/<int:id>', methods=['GET'])
@admin_login_req
def movie_del(id=None):
    movie = Movie.query.get_or_404(int(id))
    db.session.delete(movie)
    db.session.commit()
    flash('删除电影成功', 'ok')
    return redirect(url_for('admin.movie_list', page=1))


@admin.route('/movie/edit/<int:id>', methods=['GET', 'POST'])
@admin_login_req
def movie_edit(id=None):
    form = MovieForm()
    form.url.validators = []
    form.logo.validators = []
    movie = Movie.query.get_or_404(int(id))
    if request.method == 'GET':
        form.info.data = movie.info
        form.tag_id.data = movie.tag_id
        form.star.data = movie.star
    if form.validate_on_submit():
        data = form.data
        movie_count = Movie.query.filter_by(title=data['title']).count()
        if movie.title != data['title'] and movie_count == 1:
            flash("片名已存在", "err")
            return redirect(url_for('admin.movie_edit', id=id))

        if not os.path.exists(app.config["UP_DIR"]):
            os.makedirs(app.config["UP_DIR"])
            os.chmod(app.config["UP_DIR"], "rw")

        if form.url.data != "":
            file_url = secure_filename(form.url.data.filename)
            movie.url = change_filename(file_url)
            form.url.data.save(app.config["UP_DIR"] + url)
        if form.logo.data != "":
            file_logo = secure_filename(form.logo.data.filename)
            movie.logo = change_filename(file_logo)
            form.logo.data.save(app.config["UP_DIR"] + logo)

        movie.star = data['star']
        movie.tag_id = data['tag_id']
        movie.info = data['info']
        movie.title = data['title']
        movie.area = data['area']
        movie.length = data['length']
        movie.release_time = data['release_time']
        db.session.add(movie)
        db.session.commit()
        flash('修改电影成功', 'ok')
        return redirect(url_for('admin.movie_edit', id=id))
    return render_template('admin/movie_edit.html', form=form, movie=movie)


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
