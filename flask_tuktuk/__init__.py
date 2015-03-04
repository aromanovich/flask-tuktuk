# coding: utf-8
from __future__ import unicode_literals

# Find the stack on which we want to store the database connection.
# Starting with Flask 0.9, the _app_ctx_stack is the correct one,
# before that we need to use the _request_ctx_stack.
import json
import jsl
import jsonschema
from werkzeug.exceptions import HTTPException
from werkzeug.http import HTTP_STATUS_CODES

try:
    from flask import _app_ctx_stack as ctx_stack, request, current_app, jsonify, abort
except ImportError:
    from flask import _request_ctx_stack as ctx_stack


from .blueprint import Blueprint, validate_schema


__title__ = 'Flask-TukTuk'
__author__ = 'Anton Romanovich'
__license__ = 'BSD'
__copyright__ = 'Copyright 2015 Anton Romanovich'
__version__ = '0.0.1'
__version_info__ = tuple(int(i) for i in __version__.split('.'))


class Error(jsl.Document):
    # https://tools.ietf.org/html/draft-ietf-appsawg-http-problem-00
    class Options(object):
        title = 'An API error'
        description = 'See https://tools.ietf.org/html/draft-ietf-appsawg-http-problem-00 for details'

    type = jsl.UriField(default='about:blank', description='An absolute URI (RFC3986] that '
                                                           'identifies the problem type.')
    title = jsl.StringField(description='A short, human-readable summary of the problem type.')
    detail = jsl.StringField(description='A human-readable explanation specific to this '
                                         'occurrence of the problem.')
    instance = jsl.UriField(description='An absolute URI that identifies the specific '
                                        'occurrence of the problem')
    status = jsl.IntField(description='An HTTP status code.')
    extra = jsl.DictField(description='Additional data describing this occurence of the problem.')


def preprocess_request():
    view_func = current_app.view_functions[request.endpoint]
    resource_cls = getattr(view_func, 'resource_cls', None)
    if resource_cls is not None:
        schema = resource_cls.get_schema()
        if request.method in ('POST', 'PUT'):
            if request.mimetype != 'application/json':
                abort(400)
            data = request.get_json()
            if data is not None:
                validate_schema(data, schema)


def postprocess_http_exception(response):
    """:type response: flask.Response"""
    if not current_app.config['TUKTUK_RAISE_ON_INVALID_RESPONSE']:
        return response

    data = json.loads(response.data)
    if response.status_code >= 400:
        resource_cls = get_state(current_app).error_resource_cls
    else:
        view_func = current_app.view_functions[request.endpoint]
        resource_cls = getattr(view_func, 'resource_cls', None)
    if resource_cls is not None:
        schema = resource_cls.get_schema()
        validate(data, schema)
    return response


def validate(data, schema):
    errors = jsonschema.Draft4Validator(
        schema, format_checker=jsonschema.FormatChecker()).iter_errors(data)
    best_match = jsonschema.exceptions.best_match(errors)
    if best_match:
        raise best_match


def default_jsonschema_error_handler(e):
    """:type e: jsonschema.ValidationError"""
    return jsonify({
        'title': 'Bad Request',
        'status': 400,
        'detail': e.message,
        # 'instance': 'about:blank',  # TODO
        'extra': {
            'path': list(e.path),  # e.path is deque which is not JSON-serializable
            'validator': e.validator,
        }
    }), 400


def default_httpexception_handler(e):
    """:type e: HTTPException"""
    return jsonify({
        'title': HTTP_STATUS_CODES.get(e.code),
        'status': e.code,
        'detail': e.description,
    }), e.code


def register_error_handlers(app):
    app.register_error_handler(jsonschema.ValidationError, default_jsonschema_error_handler)
    for status_code in HTTP_STATUS_CODES:
        if status_code >= 400:
            app.register_error_handler(status_code, default_httpexception_handler)


def register(resource_cls=None):
    def decorator(f):
        f.resource_cls = resource_cls
        return f
    return decorator


class _APIManagerState(object):
    """Remembers configuration for the app."""
    def __init__(self, api_manager, app):
        self.api_manager = api_manager
        self.app = app
        self.error_resource_cls = None


def get_state(app):
    """Gets the state for the application"""
    assert 'tuktuk' in app.extensions, \
        'The Flask-TukTuk extension was not registered to the current ' \
        'application.  Please make sure to call init_app() first.'
    return app.extensions['tuktuk']


class APIManager(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """:type app: flask.Flask"""
        app.config.setdefault('TUKTUK_RAISE_ON_INVALID_RESPONSE', False)
        if not app.propagate_exceptions and app.config['TUKTUK_RAISE_ON_INVALID_RESPONSE']:
            from warnings import warn
            warn('TUKTUK_RAISE_ON_INVALID_RESPONSE is set, but the application will '
                 'not propagate exceptions raised by invalid responses. Consider '
                 'setting TESTING, DEBUG or PROPAGATE_EXCEPTIONS.')
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['tuktuk'] = _APIManagerState(self, app)

        app.before_request(preprocess_request)
        app.after_request(postprocess_http_exception)
        register_error_handlers(app)
        self.register_error_resource_cls(Error, app=app)

    def get_app(self, reference_app=None):
        """Helper method that implements the logic to look up an application."""
        if reference_app is not None:
            return reference_app
        if self.app is not None:
            return self.app
        ctx = ctx_stack.top
        if ctx is not None:
            return ctx.app
        raise RuntimeError('application not registered on APIManager '
                           'instance and no application bound '
                           'to current context')

    def register_error_resource_cls(self, resource_cls, app=None):
         get_state(self.get_app(app)).error_resource_cls = resource_cls
