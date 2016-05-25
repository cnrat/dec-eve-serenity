# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\ccpmetrics\client.py
import json
import httplib
import time
import datetime
from socket import gethostname
from time import gmtime, strftime

class Client(object):

    def __init__(self, host, env_tags=None, port=80):
        self.host = host
        self.port = port
        self.env_tags = env_tags

    def gauge(self, metric, value, tags=None, secondaryValues=None, sample_rate=1):
        self._write_metric(metric, value, 'gauge', tags=None, secondaryValues=None, sample_rate=1)
        return

    def increment(self, metric, value=1, tags=None, secondaryValues=None, sample_rate=1):
        self._write_metric(metric, value, 'counter', tags, secondaryValues, sample_rate)

    def decrement(self, metric, value=1, tags=None, secondaryValues=None, sample_rate=1):
        self._write_metric(metric, -value, 'counter', secondaryValues, tags, sample_rate)

    def histogram(self, metric, value, tags=None, secondaryValues=None, sample_rate=1):
        self._write_metric(metric, value, 'histogram', secondaryValues, tags, sample_rate)

    def set(self, metric, value, tags=None, secondaryValues=None, sample_rate=1):
        self._write_metric(metric, value, 'set', secondaryValues, tags, sample_rate)

    def event(self, title, text, alert_type=None, aggregation_key=None, source_type_name=None, priority=None, tags=None, hostname=None, date_happened=None):
        tags = self.add_app_tags(tags)
        http_serv = httplib.HTTPConnection(self.host, self.port)
        output = json.dumps({'name': title,
         'text': text,
         'host': hostname,
         'alerttype': alert_type,
         'priority': priority,
         'timestamp': strftime('%a, %d %b %Y %H:%M:%S +0000', gmtime()),
         'AggregationKey': aggregation_key,
         'SourceType': source_type_name,
         'tags': tags})
        http_serv.request('POST', '/events', output)

    def add_app_tags(self, tags):
        if tags is None:
            return self.env_tags
        elif self.env_tags is not None:
            temp_tags = self.env_tags.copy()
            temp_tags.update(tags)
            return temp_tags
        else:
            return tags
            return

    def _write_metric(self, metric, value, metric_type, tags=None, secondaryValues=None, sample_rate=1):
        if secondaryValues is not None:
            for key in secondaryValues:
                if secondaryValues[key] == None:
                    raise ValueError("Secondary Value %s is None.\n                                     Can't Send None to CCP Metrics" % key)

        if tags is not None:
            for key in tags:
                if tags[key] == None:
                    raise ValueError("Tag %s is None. Can't send None\n                                     to CCP Metrics" % key)

        tags = self.add_app_tags(tags)
        if tags is None:
            tags = {}
        http_serv = httplib.HTTPConnection(self.host, self.port)
        hostname = gethostname()
        output = json.dumps({'name': metric,
         'host': hostname,
         'timestamp': time.time(),
         'type': metric_type,
         'value': value,
         'secondarydata': secondaryValues,
         'sampling': sample_rate,
         'tags': tags})
        http_serv.request('POST', '/metrics', output)
        return