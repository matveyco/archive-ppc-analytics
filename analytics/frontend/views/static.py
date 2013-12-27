# -*- coding: utf-8 -*-
from flask import Blueprint
from flask.helpers import send_from_directory

static_blueprint = Blueprint('static_blueprint', __name__)

@static_blueprint.route('/img/<path:filename>')
def send_img(filename):
    return send_from_directory('static/img', filename)

@static_blueprint.route('/css/<path:filename>')
def send_css(filename):
    return send_from_directory('static/css', filename)

@static_blueprint.route('/js/<path:filename>')
def send_js(filename):
    return send_from_directory('static/js', filename)
@static_blueprint.route('/fonts/<path:filename>')
def send_fonts(filename):
    return send_from_directory('static/fonts', filename)