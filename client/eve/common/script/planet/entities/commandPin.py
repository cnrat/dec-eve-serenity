# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\script\planet\entities\commandPin.py
import eve.common.script.util.planetCommon as planetCommon
from eve.common.script.planet.entities.spaceportPin import SpaceportPin

class CommandPin(SpaceportPin):
    __guid__ = 'planet.CommandPin'
    __slots__ = []

    def OnStartup(self, id, ownerID, latitude, longitude):
        SpaceportPin.OnStartup(self, id, ownerID, latitude, longitude)

    def IsCommandCenter(self):
        return True

    def CanImportCommodities(self, commodities):
        return False

    def GetPowerOutput(self):
        level = self.eventHandler.level
        return planetCommon.GetPowerOutput(level)

    def GetCpuOutput(self):
        level = self.eventHandler.level
        return planetCommon.GetCPUOutput(level)


exports = {'planet.CommandPin': CommandPin}