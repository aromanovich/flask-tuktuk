from flask import Flask, jsonify, request
from flask.ext.tuktuk import Blueprint

from . import resources, helpers


app = Flask(__name__)
app.config.update(
    TUKTUK_HELPERS_MODULE='app.helpers'
)
bp = Blueprint('projects', __name__)


@bp.route('/projects/<id>/', methods=('GET',), resource_cls=resources.Project)
def project(id):
    data = helpers.Project(request.get_json())
    data.latest_build.finished_at
    return jsonify({
        'id': 1,
    })


app.register_blueprint(bp)
