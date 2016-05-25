# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\probeBracket.py
from eve.client.script.ui.inflight.bracket import SimpleBracket

class ProbeBracket(SimpleBracket):
    __guid__ = 'xtriui.ProbeBracket'

    def Startup(self, itemID, typeID, iconNo):
        SimpleBracket.Startup(self, itemID, None, None, iconNo)
        self.typeID = typeID
        return

    def GetMenu(self):
        return sm.GetService('scanSvc').GetProbeMenu(self.itemID)

    def OnDblClick(self, *args):
        sm.GetService('systemmap').OnBracketDoubleClick(self)