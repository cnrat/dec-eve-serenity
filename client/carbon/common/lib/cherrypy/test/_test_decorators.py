# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\cherrypy\test\_test_decorators.py
from cherrypy import expose, tools
from cherrypy._cpcompat import ntob

class ExposeExamples(object):

    @expose
    def no_call(self):
        pass

    @expose()
    def call_empty(self):
        pass

    @expose('call_alias')
    def nesbitt(self):
        pass

    @expose(['alias1', 'alias2'])
    def andrews(self):
        pass

    @expose(alias='alias3')
    def watson(self):
        pass


class ToolExamples(object):

    @expose
    @tools.response_headers(headers=[('Content-Type', 'application/data')])
    def blah(self):
        yield ntob('blah')

    blah._cp_config['response.stream'] = True