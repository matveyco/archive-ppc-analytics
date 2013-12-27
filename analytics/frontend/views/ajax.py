# -*- coding: utf-8 -*-
from flask import Blueprint, request
from tools.singleton import SingleMongo
import settings
from datetime import datetime

mng = SingleMongo(**settings.MONGO)
mng_db = mng[settings.MONGO_DATABASE]

ajax_blueprint = Blueprint('ajax_blueprint', __name__, template_folder='../templates')
today = datetime.utcnow()   
 
@ajax_blueprint.route('/update/js/<int:web_id>/<int:sub_id>/<int:host_id>/<int:hit_id>/', methods=['PUT'])
def real_js(web_id, sub_id, host_id, hit_id):
    selector = {'web_id': web_id, 'sub_id': sub_id, 'host_id': host_id, 'hit_id': hit_id}
    chunk = {'$set': {'real_js': True}}
    mng_db.hits.update(selector, chunk)
    return '[LOG] Real JS capability for WM [%s][%s] at host [%s] by hit [%s] updated' % (web_id, sub_id, host_id, hit_id)

@ajax_blueprint.route('/update/cookies/<int:web_id>/<int:sub_id>/<int:host_id>/<int:hit_id>/', methods=['PUT'])
def real_cookie(web_id, sub_id, host_id, hit_id):
    selector = {'web_id': web_id, 'sub_id': sub_id, 'host_id': host_id, 'hit_id': hit_id}
    chunk = {'$set': {'real_cookie': True}}
    mng_db.hits.update(selector, chunk)
    return '[LOG] Real cookies capability for WM [%s][%s] at host [%s] by hit [%s] updated' % (web_id, sub_id, host_id, hit_id)

@ajax_blueprint.route('/update/autoplay/<int:web_id>/<int:sub_id>/<int:host_id>/<int:hit_id>/', methods=['PUT'])
def real_autoplay(web_id, sub_id, host_id, hit_id):
    selector = {'web_id': web_id, 'sub_id': sub_id, 'host_id': host_id, 'hit_id': hit_id}
    chunk = {'$set': {'real_autoplay': True}}
    mng_db.hits.update(selector, chunk)
    return '[LOG] HTML5 video autoplay capability for WM [%s][%s] at host [%s] by hit [%s] updated' % (web_id, sub_id, host_id, hit_id)

@ajax_blueprint.route('/update/flash/<int:web_id>/<int:sub_id>/<int:host_id>/<int:hit_id>/', methods=['PUT'])
def update_flash(web_id, sub_id, host_id, hit_id):
    if bool(int(request.values['flash_enabled'])):
        selector = {'web_id': web_id, 'sub_id': sub_id, 'host_id': host_id, 'hit_id': hit_id}
        chunk = {'$set': {'flash_version': request.values['flash_version']}}
        mng_db.hits.update(selector, chunk)
    return '[LOG] Flash version (%s) for WM [%s][%s] at host [%s] by hit [%s] updated' % (request.values['flash_version'], web_id, sub_id, host_id, hit_id)

@ajax_blueprint.route('/click/flash/<int:hit_id>/', methods=['PUT'])
def flash_click(hit_id):
    selector = {'hit_id': hit_id}
    chunk = {'$inc': {'flash_click': 1}}
    mng_db.hits.update(selector, chunk)
    return '[LOG] Click on SWF by hit [%s] sent' % hit_id

@ajax_blueprint.route('/click/js/<int:hit_id>/', methods=['PUT'])
def js_click(hit_id):
    selector = {'hit_id': hit_id}
    chunk = {'$inc': {'js_click': 1}}
    mng_db.hits.update(selector, chunk)
    return '[LOG] Click on JS-link by hit [%s] sent' % hit_id

@ajax_blueprint.route('/click/outer/<int:hit_id>/', methods=['PUT'])
def outer_click(hit_id):
    selector = {'hit_id': hit_id}
    chunk = {'$inc': {'outer_click': 1}}
    mng_db.hits.update(selector, chunk)
    return '[LOG] Click on outer link by hit [%s] sent' % hit_id

@ajax_blueprint.route('/click/inner/<int:hit_id>/', methods=['PUT'])
def inner_click(hit_id):
    selector = {'hit_id': hit_id}
    chunk = {'$inc': {'inner_click': 1}}
    mng_db.hits.update(selector, chunk)
    return '[LOG] Click on inner link by hit [%s] sent' % hit_id

@ajax_blueprint.route('/click/video/<int:hit_id>/', methods=['PUT'])
def video_click(hit_id):
    selector = {'hit_id': hit_id}
    chunk = {'$inc': {'h5v_click': 1}}
    mng_db.hits.update(selector, chunk)
    return '[LOG] Click on HTML5 video by hit [%s] sent' % hit_id

@ajax_blueprint.route('/update/time/<int:host_id>/<int:hit_id>/', methods=['PUT'])
def update_time(host_id, hit_id):
    selector = {'host_id': host_id, 'hit_id': hit_id}
    chunk = {'$inc': {'time': int(request.values['time'])}}
    mng_db.hits.update(selector, chunk)
    return '[LOG] Time spent on site at host [%s] by hit [%s] — [%s]s' % (host_id, hit_id, request.values['time'])