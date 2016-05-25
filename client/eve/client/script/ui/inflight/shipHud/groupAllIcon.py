# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\shipHud\groupAllIcon.py
from eve.client.script.ui.control.eveIcon import Icon
import carbonui.const as uiconst

class GroupAllIcon(Icon):
    default_left = 0
    default_top = 9
    default_width = 16
    default_height = 16
    default_state = uiconst.UI_HIDDEN
    default_icon = 'ui_73_16_251'
    default_name = 'groupAllIcon'

    def ApplyAttributes(self, attributes):
        Icon.ApplyAttributes(self, attributes)
        self.orgPos = self.top

    def OnClick(self, *args):
        if settings.user.ui.Get('lockModules', 0):
            return
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        if dogmaLocation.CanGroupAll(session.shipid):
            dogmaLocation.LinkAllWeapons(session.shipid)
        else:
            dogmaLocation.UnlinkAllWeapons(session.shipid)

    def OnMouseDown(self, *args):
        self.top = self.orgPos + 1

    def OnMouseUp(self, *args):
        self.top = self.orgPos

    def OnMouseExit(self, *args):
        self.top = self.orgPos