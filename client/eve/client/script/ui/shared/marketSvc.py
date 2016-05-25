# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\marketSvc.py
from service import Service

class Market(Service):
    __exportedcalls__ = {'GetMarket': []}
    __guid__ = 'svc.market'
    __notifyevents__ = ['ProcessSessionChange']
    __servicename__ = 'Market'
    __displayname__ = 'Market Service'
    __dependencies__ = []
    __notifyevents__ = ['ProcessSessionChange']

    def __init__(self):
        Service.__init__(self)

    def Run(self, memStream=None):
        self.market = None
        return

    def Stop(self, memStream=None):
        self.market = None
        return

    def GetMarket(self):
        if self.market is None:
            self.market = sm.RemoteSvc('marketBroker').GetMarketRegion()
        return self.market

    def ProcessSessionChange(self, isremote, sess, change):
        if change.has_key('regionid'):
            self.market = None
        return