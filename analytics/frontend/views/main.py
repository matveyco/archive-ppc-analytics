# -*- coding: utf-8 -*-
from flask import Blueprint, request, redirect
from flask.helpers import make_response
from flask.templating import render_template
from tools.process import visit_page, log_redirect

front_blueprint = Blueprint('front_blueprint', __name__, template_folder='../templates')

# Глагне
@front_blueprint.route('/', defaults={'web_id': 0, 'code': 0, 'sub_id': 0})
@front_blueprint.route('/<int:web_id>/<int:sub_id>/', defaults={'code': 0})
@front_blueprint.route('/<int:web_id>/<int:sub_id>/redirect/<int:code>/')
def index(web_id, sub_id, code):
    current_hit_id, current_host_id = visit_page(web_id, sub_id, request)
    log_redirect(code, current_hit_id, current_host_id)
    context = {'current_hit_id': current_hit_id, 'current_host_id': current_host_id, 'web_id': web_id, 'sub_id': sub_id}
    resp = make_response(render_template('index.html', **context))
    resp.set_cookie('current_hit_id', str(current_hit_id))
    resp.set_cookie('current_host_id', str(current_host_id))
    resp.set_cookie('current_web_id', str(web_id))
    resp.set_cookie('current_sub_id', str(sub_id))
    return resp

# Тест разных кодов ответа
@front_blueprint.route('/test/<regex("(301|302)"):response_code>/', defaults={'web_id': 0, 'sub_id': 0})
@front_blueprint.route('/<int:web_id>/<int:sub_id>/test/<regex("(301|302)"):response_code>/')
def test_code(web_id, sub_id, response_code):
    return redirect('/%s/%s/redirect/%s/' % (web_id, sub_id, response_code), code=response_code)

# Страничка с JS-перенаправлением на главную
# Использует HTTP 307 как маркер перенаправления по JS.
@front_blueprint.route('/test/js_redirect/<int:host_id>/', defaults={'web_id': 0, 'sub_id': 0})
@front_blueprint.route('/<int:web_id>/<int:sub_id>/test/js_redirect/<int:host_id>/')
def js_redirect(web_id, sub_id, host_id):
    context = {'host_id': host_id, 'web_id': web_id, 'sub_id': sub_id}
    return render_template('js_redirect.html', **context)

@front_blueprint.route('/<path:name>/', defaults={'web_id': 0, 'sub_id': 0})
@front_blueprint.route('/<int:web_id>/<int:sub_id>/<path:name>/')
def stub(web_id, sub_id, name):
    current_hit_id, current_host_id = visit_page(web_id, sub_id, request)
    context = {'current_hit_id': current_hit_id, 'current_host_id': current_host_id, 'web_id': web_id, 'sub_id': sub_id}
    resp = make_response(render_template('%s.html' % name, **context))
    resp.set_cookie('current_hit_id', str(current_hit_id))
    resp.set_cookie('current_host_id', str(current_host_id))
    resp.set_cookie('current_web_id', str(web_id))
    resp.set_cookie('current_sub_id', str(sub_id))
    return resp