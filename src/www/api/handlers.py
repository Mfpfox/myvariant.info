# -*- coding: utf-8 -*-
import re
from tornado.web import RequestHandler
from biothings.www.api.handlers import MetaDataHandler, BiothingHandler, QueryHandler, StatusHandler, FieldsHandler
from settings import MyVariantSettings
from www.beacon.handlers import BeaconHandler, BeaconInfoHandler

myvariant_settings = MyVariantSettings()

class VariantHandler(BiothingHandler):
    ''' This class is for the /variant endpoint. '''
    def _examine_kwargs(self, action, kwargs):
        # subclassed to add redirection, assembly, etc
        if action == 'GET':
            m = re.search('chr.{1,2}(?P<delim>:[g\.]{0,2})\d+', self.request.uri)
            if m:
                de = m.group('delim')
                if de and de != ':g.':
                    self.redirect(':g.'.join(self.request.uri.split(de)), permanent=True)
        return None

class DemoHandler(RequestHandler):
    ''' For the /demo page. '''
    def get(self):
        with open('../../docs/demo/index.html', 'r') as demo_file:
            self.write(demo_file.read())

class QueryHandler(QueryHandler):
    ''' This class is for the /query endpoint. '''

class StatusHandler(StatusHandler):
    ''' This class is for the /status endpoint. '''

class FieldsHandler(FieldsHandler):
    ''' This class is for the /metadata/fields endpoint. '''

class MetaDataHandler(MetaDataHandler):
    ''' This class is for the /metadata endpoint. '''
    disable_caching = True
    boolean_parameters = set(['chromosome', 'dev'])

def return_applist():
    ret = [
        (r"/status", StatusHandler),
        (r"/metadata", MetaDataHandler),
        (r"/metadata/fields", FieldsHandler),
        (r"/demo/?$", DemoHandler),
        (r"/beacon/query?", BeaconHandler),
        (r"/beacon/info", BeaconInfoHandler)
    ]
    if myvariant_settings._api_version:
        ret += [
            (r"/" + myvariant_settings._api_version + "/metadata", MetaDataHandler),
            (r"/" + myvariant_settings._api_version + "/metadata/fields", FieldsHandler),
            (r"/" + myvariant_settings._api_version + "/variant/(.+)/?", VariantHandler),
            (r"/" + myvariant_settings._api_version + "/variant/?$", VariantHandler),
            (r"/" + myvariant_settings._api_version + "/query/?", QueryHandler),
        ]
    else:
        ret += [
            (r"/variant/(.+)/?", VariantHandler),
            (r"/variant/?$", VariantHandler),
            (r"/query/?", QueryHandler),
        ]
    return ret
