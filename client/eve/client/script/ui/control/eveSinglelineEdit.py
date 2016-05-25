# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\control\eveSinglelineEdit.py
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.control.singlelineedit import SinglelineEditCore
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.eveWindowUnderlay import BumpedUnderlay
import carbonui.const as uiconst
from eve.client.script.ui.control.tooltips import TooltipGeneric
from eve.client.script.ui.util.linkUtil import GetItemIDFromTextLink, GetCharIDFromTextLink
import evetypes
import localization
import util
import uiutil
import trinity

class SinglelineEdit(SinglelineEditCore):
    __guid__ = 'uicontrols.SinglelineEdit'
    default_left = 0
    default_top = 2
    default_width = 80
    default_height = 18
    default_align = uiconst.TOPLEFT
    capsWarning = None
    capsLockUpdateThread = None

    def ApplyAttributes(self, attributes):
        SinglelineEditCore.ApplyAttributes(self, attributes)
        self.displayHistory = True
        if self.GetAlign() == uiconst.TOALL:
            self.height = 0
        else:
            self.height = self.default_height
        self.isTypeField = attributes.isTypeField
        self.isCharacterField = attributes.isCharacterField
        self.isCharCorpOrAllianceField = attributes.isCharCorpOrAllianceField

    def Close(self):
        if self.capsWarning:
            self.capsWarning.Close()
        self.capsLockUpdateThread = None
        SinglelineEditCore.Close(self)
        return

    def SetPasswordChar(self, char):
        SinglelineEditCore.SetPasswordChar(self, char)
        if self.passwordchar:
            self.capsWarning = TooltipGeneric(parent=uicore.layer.hint, idx=0, opacity=0.0)
            self.capsWarning.defaultPointer = uiconst.POINT_LEFT_2
            self.capsLockUpdateThread = AutoTimer(300, self.UpdateCapsState)
        else:
            self.capsLockUpdateThread = None
        return

    def Prepare_(self):
        self.sr.text = Label(name='edittext', parent=self._textClipper, left=self.TEXTLEFTMARGIN, state=uiconst.UI_DISABLED, maxLines=1, align=uiconst.CENTERLEFT, fontsize=self.fontsize)
        self.sr.hinttext = Label(parent=self._textClipper, name='hinttext', align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, maxLines=1, left=self.TEXTLEFTMARGIN, fontsize=self.fontsize)
        self.sr.background = BumpedUnderlay(bgParent=self, showFill=True)

    def SetLabel(self, text):
        self.sr.label = EveLabelSmall(parent=self, name='__caption', text=text, state=uiconst.UI_DISABLED, align=uiconst.TOPLEFT, idx=0)
        self.sr.label.top = -self.sr.label.textheight
        if self.adjustWidth:
            self.width = max(self.width, self.sr.label.textwidth)

    def OnDropData(self, dragObj, nodes):
        SinglelineEditCore.OnDropData(self, dragObj, nodes)
        if self.isTypeField:
            self.OnDropType(dragObj, nodes)
        if self.isCharCorpOrAllianceField:
            self.OndDropCharCorpOrAlliance(dragObj, nodes)
        elif self.isCharacterField:
            self.OnDropCharacter(dragObj, nodes)

    def OnDropType(self, dragObj, nodes):
        node = nodes[0]
        guid = node.Get('__guid__', None)
        typeID = None
        if guid in ('xtriui.ShipUIModule', 'xtriui.InvItem', 'listentry.InvItem', 'listentry.InvAssetItem'):
            typeID = getattr(node.item, 'typeID', None)
        elif guid in ('listentry.GenericMarketItem', 'listentry.QuickbarItem'):
            typeID = getattr(node, 'typeID', None)
        if typeID:
            typeName = evetypes.GetName(typeID)
            self.SetValue(typeName)
        return

    def OnDropCharacter(self, dragObj, nodes):
        charName = GetDroppedCharName(nodes[0])
        if charName is not None:
            self.SetValue(charName)
        return

    def OndDropCharCorpOrAlliance(self, dragObj, nodes):
        itemName = GetDroppedCharCorpOrAllianceName(nodes[0])
        if itemName is not None:
            self.SetValue(itemName)
        return

    def UpdateCapsState(self):
        if not self.capsWarning or self.capsWarning.destroyed or self.destroyed:
            self.capsLockUpdateThread = None
            return
        else:
            if self.passwordchar is not None:
                if trinity.app.GetKeyState(uiconst.VK_CAPITAL) == True and self is uicore.registry.GetFocus():
                    if self.capsWarning:
                        if self.capsWarning.opacity == 0.0:
                            self.capsWarning.opacity = 1.0
                        self.capsWarning.display = True
                        self.capsWarning.SetTooltipString(localization.GetByLabel('/Carbon/UI/Common/CapsLockWarning'), self)
                else:
                    self.capsWarning.display = False
            return


from carbonui.control.singlelineedit import SinglelineEditCoreOverride
SinglelineEditCoreOverride.__bases__ = (SinglelineEdit,)

def GetDroppedCharCorpOrAllianceName(node):
    if not IsUserNode(node):
        return
    validTypeIDs = const.characterTypeByBloodline.values() + [const.typeCorporation, const.typeAlliance]
    itemID = GetItemIDFromTextLink(node, validTypeIDs)
    if itemID is None:
        itemID = node.itemID
    if util.IsCharacter(itemID) or util.IsCorporation(itemID) or util.IsAlliance(itemID):
        itemName = cfg.eveowners.Get(itemID).name
        return itemName
    else:
        return


def GetDroppedCharName(node):
    if not IsUserNode(node):
        return
    charID = GetCharIDFromTextLink(node)
    if charID is None:
        charID = node.charID
    if util.IsCharacter(charID):
        charName = cfg.eveowners.Get(charID).name
        return charName
    else:
        return


def IsUserNode(node):
    isUserNode = node.Get('__guid__', None) in uiutil.AllUserEntries() + ['TextLink']
    return isUserNode