#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import sys

from flask import render_template, url_for, redirect, request, flash, abort
from flask_login import login_user, login_required, logout_user, current_user

from . import auth
from .. import db
from ..models import User
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, \
        ChangeEmailForm, ResetPasswordForm

reload(sys)
sys.setdefaultencoding('utf-8')


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verity_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash(u'用户名或密码错误')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash(u'您已经退出！')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
                    email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(u'现在可以登陆！')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/change/password', methods=['get', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verity_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            db.session.commit()
            flash(u'密码已更改！')
            return redirect(url_for('auth.logout'))
        else:
            flash(u'密码错误！')
    return render_template('auth/change_password.html', form=form)


@auth.route('/change/email', methods=['GET', 'POST'])
@login_required
def change_email():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verity_password(form.password.data):
            current_user.email = form.new_email.data
            db.session.add(current_user)
            db.session.commit()
            flash(u'邮箱已更改！')
            return redirect(url_for('main.index'))
    return render_template('auth/change_email.html', form=form)


@auth.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user1 = User.query.filter_by(email=form.email.data).first()
        user2 = User.query.filter_by(username=form.username.data).first()
        if user1 is not None and user2 is not None and user1 is user2:
            user1.password = form.new_password.data
            db.session.add(user1)
            db.session.commit()
            flash(u'密码已重置！')
            return redirect(url_for('auth.login'))
        else:
            flash(u'邮箱或用户名错误！')
    return render_template('auth/reset_password.html', form=form)


