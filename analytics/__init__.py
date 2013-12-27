# -*- coding: utf-8 -*-
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from flask import Flask
from frontend.views.main import front_blueprint
from frontend.views.static import static_blueprint
from frontend.views.ajax import ajax_blueprint
from frontend.views.admin import admin_blueprint
from api import api_blueprint
from tools.regexroute import RegexConverter

application = Flask(__name__)

application.url_map.converters['regex'] = RegexConverter

application.register_blueprint(front_blueprint)
application.register_blueprint(static_blueprint)
application.register_blueprint(ajax_blueprint)
application.register_blueprint(admin_blueprint)
application.register_blueprint(api_blueprint)