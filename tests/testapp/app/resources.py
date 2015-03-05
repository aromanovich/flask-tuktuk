import jsl

from . import api


def make_collection(resource_cls):
    fields = {
        'total': jsl.IntField(required=True, minimum=0),
        'offset': jsl.IntField(required=True, minimum=0),
        'length': jsl.IntField(required=True, minimum=0),
        'items': jsl.ArrayField(jsl.DocumentField(resource_cls), required=True),
    }
    return type('{0}Collection'.format(resource_cls.__name__), (jsl.Document,), fields)


@api.helper('IdReference')
class IdReference(jsl.Document):
    id = jsl.IntField(required=True)


class Build(jsl.Document):
    id = jsl.IntField(required=True)
    result = jsl.StringField(enum=('SUCCEDED', 'FAILED'), required=True)
    finished_at = jsl.DateTimeField(required=True)


class Project(jsl.Document):
    id = jsl.IntField(required=True)
    name = jsl.StringField(required=True, min_length=10, max_length=20)
    latest_build = jsl.DocumentField(Build)


class User(object):
    # suppose User is a MongoEngine model
    # and it has a nested JSL-document
    class Resource(jsl.Document):
        id = jsl.IntField(required=True)
        login = jsl.StringField(required=True)

    Collection = api.helper('UserCollection')(make_collection(Resource))
