#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import sys

from flask_wtf import Form
from flask_pagedown.fields import PageDownField
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, Regexp, ValidationError
from ..models import Role, User

reload(sys)
sys.setdefaultencoding('utf-8')


class NameForm(Form):
    name = StringField("what's your name?", validators=[DataRequired()])
    submit = SubmitField('submit')


class EditProfileForm(Form):
    name = StringField('真实姓名', validators=[Length(0, 64)])
    location = StringField('住址', validators=[Length(0, 64)])
    about_me = TextAreaField('一句话介绍你自己')
    submit = SubmitField('提交')


class EditProfileAdminForm(Form):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    username = StringField('用户名', validators=[
        DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                              '用户名只能由字母,'
                                              '数字,点或下划线组成')])
    role = SelectField('角色', coerce=int)
    name = StringField('真实姓名', validators=[Length(1, 64)])
    location = StringField('住址', validators=[Length(1, 64)])
    about_me = TextAreaField('一句话介绍你自己')
    submit = SubmitField('提交')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choice = [
            (role.id, role.name)
            for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已被注册')


class PostForm(Form):
    title = StringField('标题', validators=[DataRequired("不能为空！")])
    body = PageDownField('内容', validators=[DataRequired("不能为空！")])
    submit = SubmitField('发布')

