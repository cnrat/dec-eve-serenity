# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\industry\views\skillEntry.py
from eve.client.script.ui.shared.shipTree.infoBubble import SkillEntry
from eve.client.script.ui.shared.monetization.trialPopup import ORIGIN_INDUSTRY

class IndustrySkillEntry(SkillEntry):

    def OpenSubscriptionPage(self, *args):
        uicore.cmd.OpenSubscriptionPage(origin=ORIGIN_INDUSTRY, reason=':'.join(['skill', str(self.typeID)]))