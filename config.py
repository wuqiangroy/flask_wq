#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import os
import sys

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    WQ_MAIL_SUBJECT_PREFIX = '[WQ]'
    WQ_MAIL_SENDER = 'WQ Admin<wuqiangroy@live.com>'
    WQ_ADMIN = os.environ.get('WQ_ADMIN') or 'wuqiangroy@live.com'
    WQ_COMMENTS_PER_PAGE = 30
    WQ_POSTS_PER_PAGE = 20
    WQ_FOLLOWERS_PER_PAGE = 50
    WQ_USERS_PER_PAGE = 50
    WQ_SLOW_DB_QUERY_TIME = True
    WQ_DB_QUERY_TIMEOUT = 0.5
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.live.com'
    MAIL_PORT = 587
    MAIL_USE_SSL = True
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('USERNAME')
    MAIL_PASSWORD = os.environ.get('PASSWORD')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dav.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    SQLQLCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # 发送错误信息
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.WQ_MAIL_SENDER,
            toaddr=[cls.WQ_ADMIN],
            subject=cls.WQ_MAIL_SUBJECT_PREFIX + ' Application Error',
            credentials=credentials,
            secure=secure)
        mail_handler.setlevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig,
}