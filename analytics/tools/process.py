# -*- coding: utf-8 -*-
from tools.singleton import SingleRedis, SingleMongo, TZ
import settings
from datetime import datetime, date, time, timedelta
from redis.exceptions import WatchError
from tools.browscap import BrowserCapabilities
from pickle import loads, dumps

rds = SingleRedis(**settings.REDIS)
mng = SingleMongo(**settings.MONGO)
mng_db = mng[settings.MONGO_DATABASE]
pipe = rds.pipeline(True)
bc = BrowserCapabilities()
tz = TZ()
today = datetime.now(tz)

def visit_page(web_id, sub_id, request):
    cps = bc(request.user_agent.string)
    
    try:
        pipe.watch('counter:hit', 'counter:host')
        pipe.multi()
        # Counters initialization
        if not rds.get('counter:hit'):
            rds.set('counter:hit', 0)
        if not rds.get('counter:host'):
            rds.set('counter:host', 0)
        
        # Processing new hit
        rds.incr('counter:hit')
        current_hit_id = rds.get('counter:hit')
        current_host_id = request.cookies.get('current_host_id')
        if not current_host_id:
            # New host
            rds.incr('counter:host')
            current_host_id = rds.get('counter:host')
    except WatchError:
        pass
    finally:
        pipe.reset()
        
    # Create hit document
    hit = {
            'hit_id': int(current_hit_id),
            'host_id': int(current_host_id),
            'web_id': int(web_id),
            'sub_id': int(sub_id),
            'date': today,
            'mobile': cps.is_mobile(),
            'decl_js': cps.supports_javascript(),
            'decl_java': cps.supports_java(),
            'browser_name': cps.name(),
            'browser_version': '.'.join(cps.version()),
            'css_version': int(cps.css_version()),
            'ip': request.remote_addr,
            'referrer': request.referrer or None,
            'user_agent_raw': request.user_agent.string,
        }
    # Insert it
    mng_db.hits.insert(hit)
    return int(current_hit_id), int(current_host_id)

def get_data(web_id, sub_id, year, month, day):
    data = {'web_id': web_id, 'sub_id': sub_id, 'year': year, 'month': month, 'day': day}
    cache_key = 'cache-%s:%s-%s:%s:%s' % (web_id, sub_id, year, month, day)
    req_date = date(year, month, day)
    date_fiter = {'$gte': datetime.combine(req_date, time(0)), '$lt': datetime.combine(req_date, time(0)) + timedelta(days=1)}

    # Get data from cache
    if today.date() != req_date:
        cache_result = rds.get(cache_key)
        if cache_result:
            return loads(cache_result)
    
    # Hosts # aggregation filter
    gen_hosts = [{'$match': {'web_id': web_id}},
                {'$project': {'host_id': 1, '_id': 0}},
                {'$group': {'_id': '$host_id'}},
                {'$project': {'count': {'$add': [1]}, 'host_id': 1, '_id': 0}},
                {'$group': {'host_count': {'$sum': '$count'}, '_id': 's'}},
                {'$project': {'host_count': 1, '_id': 0}}]

    gen_filter = {'web_id': web_id, 'date': date_fiter}
    sub_filter = {'web_id': web_id, 'date': date_fiter, 'sub_id': sub_id}
    
    # Count hits
    if sub_id is None:
        pp_gen = [{'$match': gen_filter}]
        data['count_hits'] = mng_db.hits.find(gen_filter).count()
        data['count_hosts'] = mng_db.hits.aggregate(pp_gen+gen_hosts)['result'][0]['host_count'] if data['count_hits'] else None
    else:
        pp_gen = [{'$match': sub_filter}]
        data['count_hits'] = mng_db.hits.find(sub_filter).count()
        data['count_hosts'] = mng_db.hits.aggregate(pp_gen+gen_hosts)['result'][0]['host_count'] if data['count_hits'] else None
 
    pp_time_host = pp_gen + [
        {'$match': {'time': {'$exists': True}}},
        {'$project': {'host_id': 1, 'time': 1, '_id': 0}},
        {'$group': {'_id': '$host_id', 'host_time': {'$sum': '$time'}}},
        {'$group': {'_id': 'all', 'avg_host_time': {'$avg': '$host_time'}}},
        {'$project': {'avg_host_time': 1, '_id': 0}},
        ]

    pp_time_hit = pp_gen + [
        {'$match': {'time': {'$exists': True}}},
        {'$project': {'hit_id': 1, 'time': 1, '_id': 0}},
        {'$group': {'_id': '$hit_id', 'hit_time': {'$sum': '$time'}}},
        {'$group': {'_id': 'all', 'avg_hit_time': {'$avg': '$hit_time'}}},
        {'$project': {'avg_hit_time': 1, '_id': 0}},
        ]
    
    pp_flash_click_host = pp_gen + [
        {'$match': {'flash_click': {'$exists': True}}},
        {'$project': {'host_id': 1, 'flash_click': 1, '_id': 0}},
        {'$group': {'_id': '$host_id', 'flash_click_host': {'$sum': '$flash_click'}}},
        {'$group': {'_id': 'all', 'flash_click_host_avg': {'$avg': '$flash_click_host'}, 'flash_click_host_sum': {'$sum': '$flash_click_host'}}},
        {'$project': {'flash_click_host_avg': 1, 'flash_click_host_sum': 1, '_id': 0}},
        ]
    pp_flash_click_hit = pp_gen + [
        {'$match': {'flash_click': {'$exists': True}}},
        {'$project': {'hit_id': 1, 'flash_click': 1, '_id': 0}},
        {'$group': {'_id': '$hit_id', 'flash_click_hit': {'$sum': '$flash_click'}}},
        {'$group': {'_id': 'all', 'flash_click_hit_avg': {'$avg': '$flash_click_hit'}, 'flash_click_hit_sum': {'$sum': '$flash_click_hit'}}},
        {'$project': {'flash_click_hit_avg': 1, 'flash_click_hit_sum': 1, '_id': 0}},
        ]
    
    pp_js_click_host = pp_gen + [
        {'$match': {'js_click': {'$exists': True}}},
        {'$project': {'host_id': 1, 'js_click': 1, '_id': 0}},
        {'$group': {'_id': '$host_id', 'js_click_host': {'$sum': '$js_click'}}},
        {'$group': {'_id': 'all', 'js_click_host_avg': {'$avg': '$js_click_host'}, 'js_click_host_sum': {'$sum': '$js_click_host'}}},
        {'$project': {'js_click_host_avg': 1, 'js_click_host_sum': 1, '_id': 0}},
        ]
    pp_js_click_hit = pp_gen + [
        {'$match': {'js_click': {'$exists': True}}},
        {'$project': {'hit_id': 1, 'js_click': 1, '_id': 0}},
        {'$group': {'_id': '$hit_id', 'js_click_hit': {'$sum': '$js_click'}}},
        {'$group': {'_id': 'all', 'js_click_hit_avg': {'$avg': '$js_click_hit'}, 'js_click_hit_sum': {'$sum': '$js_click_hit'}}},
        {'$project': {'js_click_hit_avg': 1, 'js_click_hit_sum': 1, '_id': 0}},
        ]
    
    # Avg + Sum # html5 video clicks by host on all pages
    pp_h5v_click_host = pp_gen + [
        {'$match': {'h5v_click': {'$exists': True}}},
        {'$project': {'host_id': 1, 'h5v_click': 1, '_id': 0}},
        {'$group': {'_id': '$host_id', 'h5v_click_host': {'$sum': '$h5v_click'}}},
        {'$group': {'_id': 'all', 'h5v_click_host_avg': {'$avg': '$h5v_click_host'}, 'h5v_click_host_sum': {'$sum': '$h5v_click_host'}}},
        {'$project': {'h5v_click_host_avg': 1, 'h5v_click_host_sum': 1, '_id': 0}},
        ]
    # Avg + Sum # html5 video clicks by each hit per page
    pp_h5v_click_hit = pp_gen + [
        {'$match': {'h5v_click': {'$exists': True}}},
        {'$project': {'hit_id': 1, 'h5v_click': 1, '_id': 0}},
        {'$group': {'_id': '$hit_id', 'h5v_click_hit': {'$sum': '$h5v_click'}}},
        {'$group': {'_id': 'all', 'h5v_click_hit_avg': {'$avg': '$h5v_click_hit'}, 'h5v_click_hit_sum': {'$sum': '$h5v_click_hit'}}},
        {'$project': {'h5v_click_hit_avg': 1, 'h5v_click_hit_sum': 1, '_id': 0}},
        ]
    
    # Avg + Sum # inner clicks by host on all pages
    pp_inner_click_host = pp_gen + [
        {'$match': {'inner_click': {'$exists': True}}},
        {'$project': {'host_id': 1, 'inner_click': 1, '_id': 0}},
        {'$group': {'_id': '$host_id', 'inner_click_host': {'$sum': '$inner_click'}}},
        {'$group': {'_id': 'all', 'inner_click_host_avg': {'$avg': '$inner_click_host'}, 'inner_click_host_sum': {'$sum': '$inner_click_host'}}},
        {'$project': {'inner_click_host_avg': 1, 'inner_click_host_sum': 1, '_id': 0}},
        ]

    # Avg + Sum # inner clicks by host on all pages
    pp_outer_click_host = pp_gen + [
        {'$match': {'outer_click': {'$exists': True}}},
        {'$project': {'host_id': 1, 'outer_click': 1, '_id': 0}},
        {'$group': {'_id': '$host_id', 'outer_click_host': {'$sum': '$outer_click'}}},
        {'$group': {'_id': 'all', 'outer_click_host_avg': {'$avg': '$outer_click_host'}, 'outer_click_host_sum': {'$sum': '$outer_click_host'}}},
        {'$project': {'outer_click_host_avg': 1, 'outer_click_host_sum': 1, '_id': 0}},
        ]
    
    # Host-specific filters
    f_real_js = [{'$match': {'real_js': True}}]
    f_decl_js = [{'$match': {'decl_js': True}}]
    f_decl_java = [{'$match': {'decl_java': True}}]
    f_flash = [{'$match': {'flash_version': {'$exists': True}}}]
    f_cookie = [{'$match': {'real_cookie': True}}]
    f_real_autoplay = [{'$match': {'real_autoplay': True}}]
    f_redirect_301 = [{'$match': {'redirect': 301}}]
    f_redirect_302 = [{'$match': {'redirect': 302}}]
    f_redirect_307 = [{'$match': {'redirect': 307}}]
    
    if data['count_hits']:
        
        r_time_host = mng_db.hits.aggregate(pp_time_host)['result']
        r_time_hit = mng_db.hits.aggregate(pp_time_hit)['result']
        
        r_flash_click_host = mng_db.hits.aggregate(pp_flash_click_host)['result']
        r_flash_click_hit = mng_db.hits.aggregate(pp_flash_click_hit)['result']
        
        r_js_click_host = mng_db.hits.aggregate(pp_js_click_host)['result']
        r_js_click_hit = mng_db.hits.aggregate(pp_js_click_hit)['result']
        
        r_h5v_click_host = mng_db.hits.aggregate(pp_h5v_click_host)['result']
        r_h5v_click_hit = mng_db.hits.aggregate(pp_h5v_click_hit)['result']

        r_inner_click_host = mng_db.hits.aggregate(pp_inner_click_host)['result']
        r_outer_click_host = mng_db.hits.aggregate(pp_outer_click_host)['result']
        
        r_real_js_host = mng_db.hits.aggregate(f_real_js+pp_gen+gen_hosts)['result']
        r_decl_js_host = mng_db.hits.aggregate(f_decl_js+pp_gen+gen_hosts)['result']
        
        r_decl_java_host = mng_db.hits.aggregate(f_decl_java+pp_gen+gen_hosts)['result']
        r_flash_host = mng_db.hits.aggregate(f_flash+pp_gen+gen_hosts)['result']
        r_cookie_host = mng_db.hits.aggregate(f_cookie+pp_gen+gen_hosts)['result']
        r_autoplay_host = mng_db.hits.aggregate(f_real_autoplay+pp_gen+gen_hosts)['result']
        
        r_redirect_301_host = mng_db.hits.aggregate(f_redirect_301+pp_gen+gen_hosts)['result']
        r_redirect_302_host = mng_db.hits.aggregate(f_redirect_302+pp_gen+gen_hosts)['result']
        r_redirect_307_host = mng_db.hits.aggregate(f_redirect_307+pp_gen+gen_hosts)['result']

        data['avg_host_time'] = r_time_host[0]['avg_host_time'] if r_time_host else 0
        data['avg_hit_time'] = r_time_hit[0]['avg_hit_time'] if r_time_hit else 0

        if r_flash_click_host:
            data.update(r_flash_click_host[0])
        if r_flash_click_hit:
            data.update(r_flash_click_hit[0])  
        if r_js_click_host:
            data.update(r_js_click_host[0])  
        if r_js_click_hit:
            data.update(r_js_click_hit[0])  
        if r_h5v_click_host:
            data.update(r_h5v_click_host[0])  
        if r_h5v_click_hit:
            data.update(r_h5v_click_hit[0])  
        if r_inner_click_host:
            data.update(r_inner_click_host[0])  
        if r_outer_click_host:
            data.update(r_outer_click_host[0])  

        data['real_js_host'] = r_real_js_host[0]['host_count'] if r_real_js_host else 0
        data['decl_js_host'] = r_decl_js_host[0]['host_count'] if r_decl_js_host else 0
   
        data['decl_java_host'] = r_decl_java_host[0]['host_count'] if r_decl_java_host else 0
        data['flash_host'] = r_flash_host[0]['host_count'] if r_flash_host else 0
        data['cookie_host'] = r_cookie_host[0]['host_count'] if r_cookie_host else 0
        data['autoplay_host'] = r_autoplay_host[0]['host_count'] if r_autoplay_host else 0
        
        data['redirect_301_host'] = r_redirect_301_host[0]['host_count'] if r_redirect_301_host else 0
        data['redirect_302_host'] = r_redirect_302_host[0]['host_count'] if r_redirect_302_host else 0
        data['redirect_307_host'] = r_redirect_307_host[0]['host_count'] if r_redirect_307_host else 0
    
    if today != req_date:
        rds.set(cache_key, dumps(data))

    return data

def log_redirect(code, hit_id, host_id):
    selector = {'host_id': host_id, 'hit_id': hit_id}
    chunk = {'$set': {'redirect': code}}
    mng_db.hits.update(selector, chunk)