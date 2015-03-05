from flask import Flask, Blueprint, jsonify, request, abort
from flask.ext.tuktuk import APIManager

from . import resources, helpers


bp = Blueprint('projects', __name__)


api = APIManager()


@api.register(resource=resources.User.Validator, helper='User')
@bp.route('/users/<int:id>/', methods=('GET', 'POST'))
def user(id):
    if request.method == 'POST':
        data = helpers.User(request.get_json())
        print data.login
    return jsonify({
        'id': id,
        'login': 'aromanovich',
    })


@api.register(resource=resources.Project)
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
