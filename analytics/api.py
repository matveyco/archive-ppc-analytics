# -*- coding: utf-8 -*-
from flask import Blueprint, Response
from datetime import date
from tools.process import get_data
from dicttoxml import dicttoxml
from json import dumps
from tools.singleton import SingleRedis
import settings

rds = SingleRedis(**settings.REDIS)
today = date.today()
api_blueprint = Blueprint('api_blueprint', __name__)

@api_blueprint.route('/api/<regex("(xml|json)"):response_type>/<int:web_id>/', defaults={'sub_id': None, 'year': None, 'month': None, 'day': None}, methods=['GET'])
@api_blueprint.route('/api/<regex("(xml|json)"):response_type>/<int:web_id>/<int:sub_id>/<int:year>/<int:month>/<int:day>/', methods=['GET'])
def get_api(response_type, web_id, sub_id, year, month, day):
    if year is None and month is None and day is None:
        year = today.year
        month = today.month
        day = today.day
    
    sub_id_key = '-' if sub_id is None else sub_id
    cache_key = 'apicache:%s:%s:%s:%s:%s:%s' % (response_type, web_id, sub_id_key, year, month, day)
    req_date = date(year, month, day)
    
    # Get data from cache
    cache_result = rds.get(cache_key) if today != req_date else None
           
    if response_type == 'xml':
        if cache_result:
            resp = cache_result
        else:
            resp = dicttoxml(get_data(web_id, sub_id, year, month, day))
    elif response_type == 'json':
        if cache_result:
            resp = cache_result
        else:
            resp = dumps(get_data(web_id, sub_id, year, month, day))
    
    if today != req_date:
        rds.set(cache_key, resp)

    if response_type == 'xml':
        return Response(resp, mimetype='text/xml')
    elif response_type == 'json':
        return Response(resp, mimetype='application/json')