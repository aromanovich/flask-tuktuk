# coding: utf-8
from __future__ import unicode_literals

import jsl

from .._compat import iteritems, iterkeys


def _indent(line, spaces=4):
    return ' ' * spaces + line


def _get_type_hint(name, field):
    """
    :param name: field name
    :type name: str
    :param field: field to get a hint for
    :type field: instance of :class:`jsl.BaseField`
    :rtype: list of strings
    """
    hint = None
    if isinstance(field, jsl.BooleanField):
        hint = 'bool'
    elif isinstance(field, jsl.StringField):
        hint = 'str'
    elif isinstance(field, jsl.IntField):
        hint = 'int'
    elif isinstance(field, jsl.NumberField):
        hint = 'numbers.Number'
    elif isinstance(field, jsl.ArrayField):
        nested_field_hint = _get_type_hint(field.items)
        hint = 'list[{}]'.format(nested_field_hint)
    elif isinstance(field, jsl.DictField):
        hint = 'dict'
    elif isinstance(field, jsl.OneOfField):
        nested_field_hints = [_get_type_hint(f) for f in field.fields]
        hint = ' | '.join(nested_field_hints)
    elif isinstance(field, jsl.DocumentField):
        hint = field.document_cls.__name__
    return [':type {0}: {1}'.format(name, hint)] if hint else []


def _get_cls_docstring(document_cls):
    """
    :type document_cls: :class:`jsl.Document`
    :rtype: list of strings
    """
    lines = ['"""']
    for name, field in iteritems(document_cls._fields):
        hint_lines = _get_type_hint(name, field)
        lines.extend(hint_lines)
    lines.append('"""')
    return lines


def _get_cls_fields(document_cls):
    """
    :type document_cls: :class:`jsl.Document`
    :rtype: list of strings
    """
    lines = []
    for name in iterkeys(document_cls._fields):
        lines.append('{0} = Attribute(\'{0}\')'.format(name))
    return lines


def _get_class(name, document_cls):
    """
    :type name: str
    :type document_cls: :class:`jsl.Document`
    :rtype: list of strings
    """
    lines = ['class {0}(DotExpandedDict):'.format(name)]
    lines.extend(_indent(line) for line in _get_cls_docstring(document_cls))
    lines.extend(_indent(line) for line in _get_cls_fields(document_cls))
    return lines


def generate_module(classes):
    """
    :param classes: a dictionary maping helper names to their JSL-documents
    :type classes: dict from str to :class:`jsl.Document`
    :rtype: list of strings
    """
    lines = ['from flask.ext.tuktuk.helpers import DotExpandedDict, Attribute', '', '']
    for helper_name, document_cls in iteritems(classes):
        lines.extend(_get_class(helper_name, document_cls))
        lines.extend(['', ''])
    return lines
