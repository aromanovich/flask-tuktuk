import jsl

from flask.ext.tuktuk import get_resource_cls_from_spec


def test_get_resource_cls_from_spec():
    get = type('get', (jsl.Document,), {})
    post_200 = type('post_200', (jsl.Document,), {})
    post_201 = type('post_201', (jsl.Document,), {})
    post_2xx = type('post_2xx', (jsl.Document,), {})
    spec = {
        'GET': get,
        'POST': {
            200: post_200,
            201: post_201,
            (200, 299): post_2xx,
        }
    }
    assert get_resource_cls_from_spec(spec, 'GET', 200) is get
    assert get_resource_cls_from_spec(spec, 'POST', 200) is post_200
    assert get_resource_cls_from_spec(spec, 'POST', 201) is post_201
    assert get_resource_cls_from_spec(spec, 'POST', 206) is post_2xx
