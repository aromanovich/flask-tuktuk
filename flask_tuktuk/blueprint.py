import functools

import jsonschema
from flask import Blueprint as BaseBlueprint, request


def validate_schema(data, schema):
    jsonschema.validate(data, schema, format_checker=jsonschema.FormatChecker())


class Blueprint(BaseBlueprint):
    """
    def route(self, rule, resource_cls=None, **options):
        schema = resource_cls and resource_cls.get_schema()
        def decorator(func):
            base_cls = super(Blueprint, self)
            @base_cls.route(rule, **options)
            @functools.wraps(func)
            def decorated_function(*args, **kwargs):
                if request.method in ('POST', 'PUT'):
                    data = request.get_json()
                    validate_schema(data, schema)
                return func(*args, **kwargs)

            return decorated_function

        return decorator
    """