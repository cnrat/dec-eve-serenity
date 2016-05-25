# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\services\structure\structureDirectory.py
import service

class StructureDirectory(service.Service):
    __guid__ = 'svc.structureDirectory'
    __notifyevents__ = ['OnCorporationStructuresUpdated', 'OnSessionChanged']
    __dependencies__ = ['objectCaching']

    def GetStructures(self):
        return sm.RemoteSvc('structureDirectory').GetMyCharacterStructures(session.regionid)

    def GetCorporationStructures(self):
        return sm.RemoteSvc('structureDirectory').GetMyCorporationStructures(session.corpid)

    def GetStructuresInSystem(self):
        if session.solarsystemid2:
            return sm.RemoteSvc('structureDirectory').GetMyDockableStructures(session.solarsystemid2)
        return set()

    def OnCorporationStructuresUpdated(self):
        self.objectCaching.InvalidateCachedMethodCall('structureDirectory', 'GetMyCorporationStructures', session.corpid)
        sm.ScatterEvent('OnCorporationStructuresReloaded')

    def Reload(self):
        self.objectCaching.InvalidateCachedMethodCall('structureDirectory', 'GetMyDockableStructures', session.solarsystemid2)
        self.objectCaching.InvalidateCachedMethodCall('structureDirectory', 'GetMyCharacterStructures', session.regionid)
        self.objectCaching.InvalidateCachedMethodCall('structureDirectory', 'GetMyCorporationStructures', session.corpid)
        sm.ScatterEvent('OnStructuresReloaded')

    def OnSessionChanged(self, isRemote, sess, change):
        if 'solarsystemid2' in change:
            sm.ScatterEvent('OnStructuresReloaded')