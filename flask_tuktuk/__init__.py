# coding: utf-8
from __future__ import unicode_literals

# Find the stack on which we want to store the database connection.
# Starting with Flask 0.9, the _app_ctx_stack is the correct one,
# before that we need to use the _request_ctx_stack.
try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack


from .blueprint import Blueprint


__title__ = 'Flask-TukTuk'
__author__ = 'Anton Romanovich'
__license__ = 'BSD'
__copyright__ = 'Copyright 2015 Anton Romanovich'
__version__ = '0.0.1'
__version_info__ = tuple(int(i) for i in __version__.split('.'))


class APIManager(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        pass
