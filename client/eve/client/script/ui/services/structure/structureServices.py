# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\services\structure\structureServices.py
import service
import structures

class StructureServices(service.Service):
    __guid__ = 'svc.structureServices'
    __notifyevents__ = ['OnSessionChanged', 'OnStructureServiceChanged']

    def Run(self, *args):
        self.onlineServices = None
        return

    def OnSessionChanged(self, isRemote, session, change):
        if 'structureid' in change and session.structureid:
            self._FetchOnlineServices()

    def GetCurrentStructureServices(self):
        return structures.SERVICES_ACCESS_SETTINGS.keys()

    def IsServiceAvailable(self, serviceID):
        if serviceID in structures.ONLINE_SERVICES:
            return True
        return serviceID in self.onlineServices

    def OnStructureServiceChanged(self, structureID):
        if structureID == session.structureid:
            self._FetchOnlineServices()
        sm.ScatterEvent('OnStructureServiceUpdated')

    def _FetchOnlineServices(self):
        self.onlineServices = sm.RemoteSvc('structureSettings').CharacterGetServices(session.structureid)