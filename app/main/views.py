#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import sys
import uuid
from datetime import datetime

from flask import render_template, session, url_for, redirect,\
    abort, flash, request, current_app, make_response
from flask_login import current_user, login_required
from flask_sqlalchemy import get_debug_queries

from . import main
from .forms import NameForm, EditProfileForm, EditProfileAdminForm, PostForm,\
    CommentForm
from ..models import User, Role, Permission, Post, Comment
from .. import db

reload(sys)
sys.setdefaultencoding('utf-8')


@main.route('/', methods=['GET', 'POST'])
def index():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['WQ_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('index.html', posts=posts, pagination=pagination,
                           current_time=datetime.utcnow())


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=user, posts=posts)


@main.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash(u'个人信息已更新！')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if current_user.email != 'wuqiangroy@live.com':
        flash(u'非管理员账号！')
        return redirect(url_for('.user', username=user.username))
    else:
        if form.validate_on_submit():
            user.email = form.email.data
            user.username = form.username.data
            user.name = form.name.data
            user.location = form.location.data
            user.about_me = form.about_me.data
            db.session.add(user)
            db.session.commit()
            flash(u'个人资料已更新！')
            return redirect(url_for('main.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/write', methods=['GET', 'POST'])
@login_required
def write_post():
    form = PostForm()
    if form.validate_on_submit():
        pid = str(uuid.uuid1())
        post = Post(
            title=form.title.data,
            body=form.body.data,
            pid=pid,
            author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        post2 = Post.query.filter_by(pid=pid).first()
        return redirect(url_for('.post', id=post2.id))
    return render_template('write_post.html', form=form)


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and current_user.email != 'wuqiangroy@live.com':
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        db.session.add(post)
        flash(u'文章已成功更新！')
        return redirect(url_for('.post', id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


@main.route('/post/<int:id>', methods=['get', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            body=form.body.data,
            post=post,
            author=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash(u'您已成功评论！')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // \
            current_app.config['WQ_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['WQ_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('post.html', post=post, form=form,
                           comments=comments, pagination=pagination)


@main.route('/moderate')
@login_required
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['WQ_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                           pagination=pagination, page=page)

"""
@main.route('/moderate/enable/<int:id>')
@login_required
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))
"""


@main.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'用户不存在！')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash(u'你已经关注了此用户！')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash(u'你刚刚关注了%s。' % username)
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'用户不存在！')
        return redirect(url_for('.index'))
    if current_user.unfollow(user):
        flash(u'你没有关注此用户！')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash(u'你已取消关注%s。' % username)
    return redirect(url_for('.user', username=username))


@main.route('/follower/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'用户不存在！')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.follower.paginate(
        page, per_page=current_app.config['WQ_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower,
                'timestamp': item.timestamp, }
               for item in pagination.items]
    return render_template('followers.html', user=user, title=u'关注者',
                            endpoint='.followers', pagination=pagination,
                            follows=follows)


@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'用户不存在')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['WQ_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed,
                'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title=u'关注了谁',
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp


@main.route('/all_users')
def all_users():
    if current_user.email != 'wuqiangroy@live.com':
        flash(u'非管理员')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.member_since.desc()).paginate(
        page, per_page=current_app.config['WQ_USERS_PER_PAGE'],
        error_out=False)
    items = [item for item in pagination.items]
    return render_template('all_users.html', title=u'所有注册用户',
                           endpoint='.all_users', pagination=pagination,
                           items=items)


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['WQ_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %f\nContext: %s\n'
                % (query.statement, query.parameters, query.duration,
                   query.context))
    return response
