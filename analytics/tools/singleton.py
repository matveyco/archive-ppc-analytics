# -*- coding: utf-8 -*-
from redis import Redis
from pymongo import MongoClient
import settings
from datetime import tzinfo, timedelta

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class SingleRedis(Redis):
    __metaclass__ = Singleton
    
class SingleMongo(MongoClient):
    __metaclass__ = Singleton

class TZ(tzinfo):
    __metaclass__ = Singleton
    
    __shift = timedelta(seconds=settings.TZ_SHIFT)
    def utcoffset(self, dt):
        return self.__shift

    def tzname(self, dt):
        return "Custom"

    def dst(self, dt):
        return self.__shift