from flask.ext.webtest import TestApp

from tests.testapp import app


def test_hello_world():
    w = TestApp(app)
    r = w.get('/projects/1/')
    print r.json
