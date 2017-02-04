#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import re
import unittest
from flask import url_for
from app import create_app, db
from app.models import User, Role


class FlaskClientTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get(url_for('main.index'))
        self.assertTrue('Stranger' in response.get_data(as_text=True))

    # 使用Flask测试客户端模拟新用户注册的整个流程

    def test_register_and_login(self):
        # register
        response = self.client.post(url_for('auth.register'), data={
            'email': 'john@live.com',
            'username': 'john',
            'password': '123',
            'password2': '123'})
        self.assertTrue(response.status_code == 302)

        # use new account to login
        response = self.client.post(url_for('auth.login'), data={
            'username': 'john',
            'password': '123'}, follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertTrue(re.search(u'您好，john', data))

        # logout
        response = self.client.get(url_for('auth.logout'),
                                   follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertTrue(u'您已经退出！'in data)

