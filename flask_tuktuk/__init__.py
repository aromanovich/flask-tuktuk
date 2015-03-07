# coding: utf-8
from __future__ import unicode_literals

import json
import jsl
import jsonschema
from werkzeug.exceptions import HTTPException
from werkzeug.http import HTTP_STATUS_CODES

# Find the stack on which we want to store the extension state.
# Starting with Flask 0.9, the _app_ctx_stack is the correct one,
# before that we need to use the _request_ctx_stack.
from flask.ext.tuktuk._compat import iteritems

try:
    from flask import _app_ctx_stack as ctx_stack, request, current_app, jsonify, abort
except ImportError:
    from flask import _request_ctx_stack as ctx_stack


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


def validate_schema(data, schema):
    jsonschema.validate(data, schema, format_checker=jsonschema.FormatChecker())


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


def get_resource_cls_from_spec(spec, method, status_code):
    resource_cls = None
    if isinstance(spec, type) and issubclass(spec, jsl.Document):
        resource_cls = spec
    elif isinstance(spec, dict):
        if method in spec:
            method_spec = spec[method]
            if isinstance(method_spec, type) and issubclass(method_spec, jsl.Document):
                resource_cls = method_spec
            elif isinstance(method_spec, dict):
                if status_code in method_spec:
                    resource_cls = method_spec[status_code]
                else:
                    for k, v in iteritems(method_spec):
                        if isinstance(k, tuple) and len(k) == 2:
                            if k[0] <= status_code <= k[1]:
                                resource_cls = v
                                break
    return resource_cls


def postprocess_http_exception(response):
    """:type response: flask.Response"""
    if not current_app.config['TUKTUK_RAISE_ON_INVALID_RESPONSE']:
        return response

    resource_cls = None
    if response.status_code >= 400:
        resource_cls = get_state(current_app).error_resource_cls
    else:
        view_func = current_app.view_functions[request.endpoint]
        if hasattr(view_func, 'spec'):
            resource_cls = get_resource_cls_from_spec(view_func.spec, request.method, response.status_code)

    if resource_cls is None:
        pass  # TODO show warning?
    else:
        schema = resource_cls.get_schema()
        data = json.loads(response.data)
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
        # TODO
        # flask-principal sets description to 'flask_principal.Permission'
        # and it breaks things
        'detail': e.description,
    }), e.code


def register_error_handlers(app):
    app.register_error_handler(jsonschema.ValidationError, default_jsonschema_error_handler)
    for status_code in HTTP_STATUS_CODES:
        if status_code >= 400:
            app.register_error_handler(status_code, default_httpexception_handler)


class _APIManagerState(object):
    """Remembers configuration for the app."""
    def __init__(self, api_manager, app):
        self.api_manager = api_manager
        self.app = app
        self.error_resource_cls = None
        self.resources_registry = {}


def get_state(app):
    """Gets the state for the application"""
    assert 'tuktuk' in app.extensions, \
        'The Flask-TukTuk extension was not registered to the current ' \
        'application.  Please make sure to call init_app() first.'
    return app.extensions['tuktuk']


class APIManager(object):
    def __init__(self, app=None):
        self.after_init_functions = []
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
        for func in self.after_init_functions:
            func(app=app)

    def get_app_or_none(self, reference_app=None):
        """Helper method that implements the logic to look up an application."""
        if reference_app is not None:
            return reference_app
        if self.app is not None:
            return self.app
        ctx = ctx_stack.top
        if ctx is not None:
            return ctx.app
        return None

    def get_app(self, reference_app=None):
        """Helper method that implements the logic to look up an application."""
        app = self.get_app_or_none(reference_app=reference_app)
        if app is None:
            raise RuntimeError('application not registered on APIManager '
                               'instance and no application bound '
                               'to current context')
        return app


    def register_error_resource_cls(self, resource_cls, app=None):
        app = self.get_app(app)
        get_state(app).error_resource_cls = resource_cls

    def _register_helper(self, app, helper_name, resource_cls):
        get_state(app).resources_registry[helper_name] = resource_cls

    def register_helper(self, helper_name, resource_cls, app=None):
        app = self.get_app_or_none(app)
        if app is not None:
            self._register_helper(app, helper_name, resource_cls)
        else:
            self.after_init_functions.append(lambda app: self._register_helper(app, helper_name, resource_cls))
        return resource_cls

    def helper(self, name, app=None):
        """A decorator that registers a :class:`jsl.Document` as a helper.

        :param name: a helper class name
        :type name: str
        """
        def decorator(resource_cls):
            self.register_helper(name, resource_cls, app=app)
            return resource_cls
        return decorator

    def input(self, resource, helper=None):
        app = self.get_app_or_none()
        helper_name = helper or resource.__name__
        self.register_helper(helper_name, resource, app=app)

        def decorator(view):
            view.resource_cls = resource
            return view
        return decorator

    def output(self, spec):
        # TODO
        # warn if a resource specified for 204 response
        def decorator(view):
            view.spec = spec
            return view
        return decorator