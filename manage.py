#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import os
import sys

from app import create_app, db
from app.models import User, Role, Permission, Follow, Comment
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('WQ_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

reload(sys)
sys.setdefaultencoding('utf-8')

COV = None
if os.environ.get('WQ_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Follow=Follow,
                Comment=Comment, Permission=Permission)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test(coverage=False):
    """Run the unit tests."""
    if coverage and not os.environ.get('WQ_COVERAGE'):
        import sys
        os.environ['WQ_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print(u'覆盖测试总结：')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'temp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


@manager.command
def profile(length=25, profile_dir=None):
        """Start the application under the code profile."""
        from werkzeug.contrib.profiler import ProfilerMiddleware
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                          profile_dir=profile_dir)
        app.run()


@manager.command
def deploy():
    """Run deployment tasks."""
    from flask_migrate import upgrade
    from app.models import Role, User

    # 迁移数据
    upgrade()

    # 创建用户角色
    Role.insert_roles()

if __name__ == '__main__':
    manager.run()
