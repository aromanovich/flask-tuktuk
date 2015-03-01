# coding: utf-8
from __future__ import unicode_literals


def make_dot_expanded(data):
    if isinstance(data, DotExpandedDict):
        return data
    elif isinstance(data, dict):
        pairs = []
        for key, value in data.items():
            pairs.append((key, make_dot_expanded(value)))
        return DotExpandedDict(pairs)
    elif isinstance(data, list):
        return [make_dot_expanded(x) for x in data]
    return data


class DotExpandedDict(dict):
    def __init__(self, *args, **kwargs):
        super(DotExpandedDict, self).__init__(*args, **kwargs)
        for key, value in self.items():
            self[key] = make_dot_expanded(value)

    def __getattr__(self, attr):
        if attr in self:
            return self[attr]
        raise AttributeError('Attribute or key {0.__class__.__name__}.{1} '
                             'does not exist'.format(self, attr))

    def __setattr__(self, attr, value):
        self[attr] = value

    def __setitem__(self, key, value):
        if isinstance(value, (list, dict)) and not isinstance(value, DotExpandedDict):
            value = make_dot_expanded(value)
        super(DotExpandedDict, self).__setitem__(key, value)


class Attribute(object):
    def __init__(self, name):
        self.name = name

    def __get__(self, obj, objtype):
        if not obj:
            raise AttributeError("type object '{0}' has no attribute '{1}'".format(
                objtype.__name__, self.name))
        return obj.__getattr__(self.name)