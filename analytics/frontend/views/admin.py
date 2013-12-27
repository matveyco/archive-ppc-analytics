# -*- coding: utf-8 -*-
from flask import Blueprint, request
from flask.templating import render_template
from tools.process import get_data
from datetime import date

today = date.today()
admin_blueprint = Blueprint('admin_blueprint', __name__, template_folder='../templates')

@admin_blueprint.route('/admin/<int:web_id>/', defaults={'sub_id': None, 'year': None, 'month': None, 'day': None})
@admin_blueprint.route('/admin/<int:web_id>/<int:sub_id>/', defaults={'year': None, 'month': None, 'day': None})
@admin_blueprint.route('/admin/<int:web_id>/<int:sub_id>/<int:year>/<int:month>/<int:day>/')
def admin(web_id, sub_id, year, month, day):
    if year is None and month is None and day is None:
        year = today.year
        month = today.month
        day = today.day
    data = get_data(web_id, sub_id, year, month, day)
    context = {'year': year, 'month': month, 'day': day, 'web_id': web_id, 'data': data, 'sub_id': sub_id}
    if request.is_xhr:
        return render_template('admin_ajax.html', **context)
    else:
        return render_template('admin.html', **context)   