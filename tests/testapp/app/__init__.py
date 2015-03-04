from flask import Flask, jsonify, request, abort
from flask.ext.tuktuk import Blueprint, APIManager, register

from . import resources, helpers


bp = Blueprint('projects', __name__)

@register(resource_cls=resources.Project)
@bp.route('/projects/<int:id>/', methods=('GET', 'POST'))
def project(id):
    if request.method == 'POST':
        data = helpers.Project(request.get_json())
        print data.latest_build.finished_at
    else:
        if id != 1:
            abort(404)
    return jsonify({
        'id': 1,
    })


@bp.route('/bad_404/')
def bad_404():
    return jsonify({
        'exception': 'whatever',
    }), 404


api_manager = APIManager()

def create_app(config):
    app = Flask(__name__)
    app.config.update(config)
    app.config.update(
        TUKTUK_HELPERS_MODULE='app.helpers'
    )
    app.register_blueprint(bp)
    api_manager.init_app(app)
    return app
