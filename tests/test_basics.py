import jsonschema
import mock
import pytest
from flask.ext.webtest import TestApp

from flask.ext.tuktuk import validate
from tests.testapp.app import create_app


@pytest.fixture
def app():
    return create_app({'TESTING': True})


@pytest.fixture
def w(app):
    return TestApp(app)


def test_hello_world(w):
    r = w.get('/projects/1/')
    assert r.json == {'id': 1}

    r = w.get('/projects/2/', status=404)
    assert r.json == {
        'status': 404,
        'title': 'Not Found',
        'detail': ('The requested URL was not found on the server.  '
                   'If you entered the URL manually please check your spelling and try again.'),
    }

    r = w.post_json('/projects/1/', {'id': 'string'}, status=400)
    assert r.json == {
        'status': 400,
        'title': 'Bad Request',
        'detail': "'name' is a required property",
        'extra': {
            'path': [],
            'validator': 'required',
        },
    }

    r = w.get('/users/')
    assert r.json == {
        'items': [],
        'length': 0,
        'total': 1000,
        'offset': 0
    }


def test_abort_400_custom_detail(w):
    r = w.get('/abort_400_custom_detail/', status=400)
    assert r.json == {
        'status': 400,
        'detail': 'Watch your payloads!',
        'title': 'Bad Request'
    }


def test_204_annotated_with_resource():
    app = create_app({
        'TESTING': True,
        'TUKTUK_RAISE_ON_INVALID_RESPONSE': True,
    })
    w = TestApp(app)
    w.get('/204_annotated_with_resource/', status=204)


def test_raise_on_invalid_response_with_testing():
    app = create_app({
        'TESTING': True,
        'TUKTUK_RAISE_ON_INVALID_RESPONSE': True,
    })
    w = TestApp(app)
    with pytest.raises(jsonschema.ValidationError) as e:
        w.get('/bad_404/', status=404)


def test_raise_on_invalid_response_without_testing():
    with mock.patch('warnings.warn') as warn:
        create_app({
            'TESTING': False,
            'TUKTUK_RAISE_ON_INVALID_RESPONSE': True,
        })
    assert warn.called
    args, kwargs = warn.call_args
    assert len(args) == 1
    assert 'Consider setting TESTING, DEBUG or PROPAGATE_EXCEPTIONS' in args[0]


def test_validate():
    data = {'x': 123}
    schema = {
        'type': 'object',
        'properties': {
            'x': {'type': 'string'},
        }
    }
    with pytest.raises(jsonschema.ValidationError):
        validate(data, schema)