# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\podGuide\megaMenuManager.py
import carbonui.const as uiconst
from eve.client.script.ui.podGuide.megaMenu import MegaMenu

class MegaMenuManager(object):

    def ShowMegaMenu(self, options, categoryInfo, pos, openingButtonClass):
        uicore.layer.abovemain.megaMenuTest = MegaMenu(parent=uicore.layer.abovemain, megaMenuOptions=options, categoryInfo=categoryInfo, pos=pos, align=uiconst.TOPLEFT, openingButtonClass=openingButtonClass)

    def GetCurrentMegaMenu(self):
        megaMenu = getattr(uicore.layer.abovemain, 'megaMenuTest', None)
        if megaMenu and not megaMenu.destroyed:
            return megaMenu
        else:
            return

    def CloseMegaMenu(self):
        current = self.GetCurrentMegaMenu()
        if current:
            current.Close()