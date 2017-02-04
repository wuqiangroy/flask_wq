#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import sys

from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User

reload(sys)
sys.setdefaultencoding('utf-8')


class LoginForm(Form):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('保持登陆状态')
    submit = SubmitField('登陆')


class RegistrationForm(Form):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    username = StringField('用户名', validators=[
        DataRequired(), Length(1, 64),Regexp('^[A-Za-z][A-za-z0-9_.]*$', 0,
                                             '用户名只能是字母,'
                                             '数字, 点或是下划线')])
    password = PasswordField('密码', validators=[DataRequired(),
                                                     EqualTo('password2',
                                                             message='两次密码不匹配')])
    password2 = PasswordField('再次输入密码', validators=[DataRequired()])
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已被注册')


class ChangePasswordForm(Form):
    old_password = PasswordField('旧密码', validators=[DataRequired()])
    new_password = PasswordField('新密码', validators=[DataRequired(),
                                                             EqualTo('new_password2',
                                                                     message='两次密码不匹配')])
    new_password2 = PasswordField('再次输入新密码', validators=[DataRequired()])
    submit = SubmitField('确认更改')


class ChangeEmailForm(Form):
    new_email = StringField('新邮箱', validators=[DataRequired(), Length(1, 64),
                                                     Email()])
    password = PasswordField('请输入密码', validators=[DataRequired()])
    subumit = SubmitField('确认更改')

    def validata_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise AttributeError('邮箱已被注册！')


class ResetPasswordForm(Form):
    email = StringField('邮箱', validators=[DataRequired(), Length(1,64),
                                                  Email()])
    username = StringField('用户名', validators=[DataRequired(),
                                                        Length(1, 64)])
    new_password = PasswordField('新密码', validators=[DataRequired()])





