# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\parklife\dungeonTracking.py
import service
import localization
from eve.common.script.sys.rowset import Rowset

class DungeonTracking(service.Service):
    __guid__ = 'svc.dungeonTracking'
    __notifyevents__ = ['ProcessSessionChange', 'OnDistributionDungeonEntered', 'OnEscalatingPathDungeonEntered']

    def __init__(self):
        service.Service.__init__(self)
        self.distributionDungeonsEntered = None
        self.escalatingPathDungeonsEntered = None
        return

    def Run(self, memStream=None):
        service.Service.Run(self, memStream)

    def ProcessSessionChange(self, isRemote, session, change):
        if change.has_key('locationid'):
            self.distributionDungeonsEntered = None
            self.escalatingPathDungeonsEntered = None
        return

    def OnDistributionDungeonEntered(self, row):
        if self.distributionDungeonsEntered is None:
            self.distributionDungeonsEntered = Rowset(row.header)
        self.distributionDungeonsEntered.append(row)
        return

    def OnEscalatingPathDungeonEntered(self, row):
        if self.escalatingPathDungeonsEntered is None:
            self.escalatingPathDungeonsEntered = Rowset(row.header)
        if row.dungeonNameID:
            row.name = localization.GetByMessageID(row.dungeonNameID)
        self.escalatingPathDungeonsEntered.append(row)
        return

    def GetDistributionDungeonsEntered(self):
        return self.distributionDungeonsEntered

    def GetEscalatingPathDungeonsEntered(self):
        return self.escalatingPathDungeonsEntered