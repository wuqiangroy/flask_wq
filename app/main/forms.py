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
    username = StringField(u'用户名', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField(u'密码', validators=[DataRequired()])
    remember_me = BooleanField(u'保持登陆状态')
    submit = SubmitField(u'登陆')


class RegistrationForm(Form):
    email = StringField(u'邮箱', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    username = StringField(u'用户名', validators=[
        DataRequired(), Length(1, 64),Regexp('^[A-Za-z][A-za-z0-9_.]*$', 0,
                                             u'用户名只能是字母,'
                                             u'数字, 点或是下划线')])
    password = PasswordField(u'密码', validators=[DataRequired(),
                                                     EqualTo('password2',
                                                             message=u'两次密码不匹配')])
    password2 = PasswordField(u'再次输入密码', validators=[DataRequired()])
    submit = SubmitField(u'注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(u'邮箱已被注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已被注册')


class ChangePasswordForm(Form):
    old_password = PasswordField(u'旧密码', validators=[DataRequired()])
    new_password = PasswordField(u'新密码', validators=[DataRequired(),
                                                             EqualTo('new_password2',
                                                                     message=u'两次密码不匹配')])
    new_password2 = PasswordField(u'再次输入新密码', validators=[DataRequired()])
    submit = SubmitField(u'确认更改')


class ChangeEmailForm(Form):
    new_email = StringField(u'新邮箱', validators=[DataRequired(), Length(1, 64),
                                                     Email()])
    password = PasswordField(u'请输入密码', validators=[DataRequired()])
    subumit = SubmitField(u'确认更改')

    def validata_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise AttributeError(u'邮箱已被注册！')


class ResetPasswordForm(Form):
    email = StringField(u'邮箱', validators=[DataRequired(), Length(1,64),
                                                  Email()])
    username = StringField(u'用户名', validators=[DataRequired(),
                                                        Length(1, 64)])
    new_password = PasswordField(u'新密码', validators=[DataRequired()])
    submit = SubmitField(u'确认重置')





