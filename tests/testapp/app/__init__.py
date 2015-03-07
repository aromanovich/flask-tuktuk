from flask import Flask, Blueprint, jsonify, request, abort
from flask.ext.tuktuk import APIManager



bp = Blueprint('projects', __name__)


api = APIManager()


from . import resources, helpers


@api.input(resources.User.Resource, helper='User')
@api.output({
    'GET': resources.User.Collection,
    'POST': {
        200: resources.User.Resource,
        201: resources.IdReference
    }
})
@bp.route('/users/', methods=('GET', 'POST'))
def users():
    if request.method == 'POST':
        data = helpers.User(**request.get_json())
        # pycharm autocompletes:
        print data.login
        return jsonify(data)
        # or
        return jsonify(helpers.IdReference(id=1)), 201
    elif request.method == 'GET':
        data = helpers.UserCollection()
        # pycharm autocompletes:
        data.total = 1000
        data.items = []
        data.length = 0
        data.offset = 0
        return jsonify(data)
        # pycharm highlights unexpected argument:
        helpers.UserCollection(blalba=123)


@api.input(resources.User.Resource, helper='User')
@api.output(resources.User.Resource)
@bp.route('/users/<int:id>/', methods=('GET', 'PUT'))
def user(id):
    if request.method == 'PUT':
        data = helpers.User(**request.get_json())
        return jsonify(data)
    return jsonify({
        'id': id,
        'login': 'aromanovich',
    })


@api.input(resources.Project)
@bp.route('/projects/<int:id>/', methods=('GET', 'POST'))
def project(id):
    if request.method == 'POST':
        data = helpers.Project(request.get_json())
        print data.latest_build.finished_at
    else:
        if id != 1:
            abort(404)
    return jsonify({
        'id': id,
    })


@bp.route('/abort_400_custom_detail/')
def abort_400_custom_detail():
    abort(400, description='Watch your payloads!')


@bp.route('/bad_404/')
def bad_404():
    return jsonify({
        'exception': 'whatever',
    }), 404



def create_app(config=None):
    app = Flask(__name__)
    if config:
        app.config.update(config)
    app.config.update(
        TUKTUK_HELPERS_MODULE='app.helpers'
    )
    app.register_blueprint(bp)
    api.init_app(app)
    return app
