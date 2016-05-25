# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\container.py
from carbonui.control.scrollentries import SE_BaseClassCore
from eve.client.script.ui.control.themeColored import FillThemeColored, FrameThemeColored
import evetypes
from inventorycommon.util import GetItemVolume
import uicontrols
import uix
import uiutil
import blue
import carbon.client.script.util.lg as lg
import uthread
import base
import service
import carbonui.const as uiconst
import log
import trinity
import invCtrl
import util
import localization
import telemetry
import uiprimitives
from math import pi, fabs
colMargin = rowMargin = 12

class InvContViewBtns(uicontrols.ContainerAutoSize):
    __guid__ = 'uicls.InvContViewBtns'
    default_name = 'InvContViewBtns'
    default_align = uiconst.TOPLEFT
    default_height = 16

    def ApplyAttributes(self, attributes):
        uicontrols.ContainerAutoSize.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        self.viewMode = None
        self.btnViewModeIcons = uicontrols.ButtonIcon(texturePath='res:/UI/Texture/Icons/38_16_188.png', parent=self, width=self.height, align=uiconst.TOLEFT, func=self.SetViewModeIcons, hint=localization.GetByLabel('UI/Inventory/Icons'))
        self.btnViewModeIconList = uicontrols.ButtonIcon(texturePath='res:/UI/Texture/Icons/38_16_189.png', parent=self, align=uiconst.TOLEFT, width=self.height, func=self.SetViewModeIconList, hint=localization.GetByLabel('UI/Inventory/Details'))
        self.btnViewModeList = uicontrols.ButtonIcon(texturePath='res:/UI/Texture/Icons/38_16_190.png', parent=self, align=uiconst.TOLEFT, width=self.height, func=self.SetViewModeList, hint=localization.GetByLabel('UI/Inventory/List'))
        return

    def SetViewModeIcons(self):
        self._SetViewMode(0)

    def SetViewModeIconList(self):
        self._SetViewMode(1)

    def SetViewModeList(self):
        self._SetViewMode(2)

    def _SetViewMode(self, viewMode):
        self.viewMode = viewMode
        self.UpdateButtons(viewMode)
        self.controller.SetInvContViewMode(viewMode)

    def UpdateButtons(self, viewMode):
        self.btnViewModeIcons.SetActive(viewMode == 0)
        self.btnViewModeIconList.SetActive(viewMode == 1)
        self.btnViewModeList.SetActive(viewMode == 2)


class InvContQuickFilter(uiprimitives.Container):
    __guid__ = 'uicls.InvContQuickFilter'
    default_align = uiconst.TOPLEFT
    default_height = 20
    default_width = 100

    def ApplyAttributes(self, attributes):
        uiprimitives.Container.ApplyAttributes(self, attributes)
        self.invCont = attributes.invCont
        self.inputThread = None
        self.quickFilterInputBox = uicontrols.SinglelineEdit(name='quickFilterInputBox', parent=self, align=uiconst.CENTER, width=self.width, top=0, OnChange=self.SetQuickFilterInput, hinttext=localization.GetByLabel('UI/Inventory/Filter'))
        self.quickFilterInputBox.ShowClearButton(hint=localization.GetByLabel('UI/Inventory/Clear'))
        self.quickFilterInputBox.SetHistoryVisibility(0)
        if self.invCont:
            self.SetInvCont(self.invCont)
        return

    def SetInvCont(self, invCont):
        self.invCont = invCont
        if not settings.user.ui.Get('keepInvQuickFilterInput', False):
            self.quickFilterInputBox.SetText(u'')
            self.quickFilterInputBox.SetHintText(localization.GetByLabel('UI/Inventory/Filter'))

    def GetQuickFilterInput(self):
        return self.quickFilterInputBox.GetText()

    def SetQuickFilterInput(self, txt):
        if self.inputThread:
            return
        self.inputThread = uthread.new(self._SetQuickFilterInput, txt)

    def ClearFilter(self):
        self.quickFilterInputBox.SetValue('')

    def _SetQuickFilterInput(self, txt):
        if txt:
            blue.synchro.SleepWallclock(300)
        if self.invCont:
            self.invCont.SetQuickFilterInput(self.quickFilterInputBox.GetValue())
        self.inputThread = None
        return


class InvContCapacityGauge(uiprimitives.Container):
    __guid__ = 'uicls.InvContCapacityGauge'
    __notifyevents__ = ['OnItemChange']
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    default_clipChildren = True
    COLOR_SECONDARY = (0.0, 0.52, 0.67)
    COLOR_PRIMARY = (0.0, 0.31, 0.4)
    BG_OPACITY_NORMAL = 0.8
    BG_OPACITY_PINNED = 0.2

    def ApplyAttributes(self, attributes):
        uiprimitives.Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        invCont = attributes.invCont
        self.secondaryVolume = 0.0
        self.additionalVolume = 0.0
        self.refreshGaugesThread = None
        self.resetPending = False
        self.capacityText = uicontrols.EveLabelSmall(name='capacityText', parent=self, align=uiconst.CENTER, top=1)
        self.bg = FillThemeColored(bgParent=self, colorType=uiconst.COLORTYPE_UIBASECONTRAST, opacity=0.5)
        uicontrols.Frame(parent=self, color=(0.5, 0.5, 0.5, 0.05))
        self.capacityGaugeParentSec = uiprimitives.Container(name='capacityGaugeParent', parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        self.capacityGaugeSec = uicontrols.GradientSprite(parent=self.capacityGaugeParentSec, align=uiconst.TOLEFT_PROP, rotation=-pi / 2, rgbData=[(0, self.COLOR_SECONDARY)], alphaData=[(0, 0.7), (0.5, 1.0), (1.0, 0.7)])
        self.capacityGaugeParent = uiprimitives.Container(name='capacityGaugeParent', parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        self.capacityGauge = uicontrols.GradientSprite(parent=self.capacityGaugeParent, align=uiconst.TOLEFT_PROP, rotation=-pi / 2, rgbData=[(0, self.COLOR_PRIMARY)], alphaData=[(0, 0.7), (0.5, 1.0), (1.0, 0.7)])
        self.capacityGaugeParentAdd = uiprimitives.Container(name='capacityGaugeParentAdd', parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED)
        self.capacityGaugeAdd = uicontrols.GradientSprite(parent=self.capacityGaugeParent, align=uiconst.TOLEFT_PROP, rotation=-pi / 2, rgbData=[(0, self.COLOR_SECONDARY)], alphaData=[(0, 0.7), (0.5, 1.0), (1.0, 0.7)])
        if invCont:
            self.SetInvCont(invCont)
        else:
            self.invCont = None
        return

    def SetInvCont(self, invCont):
        self.invCont = invCont
        self.SetSecondaryVolume()
        self.SetAdditionalVolume()
        self.RefreshCapacity()
        self.bg.display = self.invCont.invController.hasCapacity

    @telemetry.ZONE_METHOD
    def RefreshCapacity(self):
        if not self.invCont:
            return
        self.UpdateLabel()
        proportion = 0.0
        if self.invCont.invController.hasCapacity:
            cap = self.invCont.invController.GetCapacity()
            if cap.capacity:
                proportion = min(1.0, max(0.0, cap.used / float(cap.capacity)))
        currWidth = self.capacityGauge.width
        duration = 0.5 * fabs(currWidth - proportion) ** 0.3
        uicore.animations.MorphScalar(self.capacityGauge, 'width', currWidth, proportion, duration=duration)

    def UpdateLabel(self):
        if self.invCont.invController.hasCapacity:
            cap = self.invCont.invController.GetCapacity()
            volume = cap.used + self.additionalVolume
            text = localization.GetByLabel('UI/Inventory/ContainerQuantityAndCapacity', quantity=volume, capacity=cap.capacity)
        else:
            volume = 0.0
            for item in self.invCont.invController.GetItems():
                volume += GetItemVolume(item)

            text = localization.GetByLabel('UI/Inventory/ContainerCapacity', capacity=volume)
        if self.secondaryVolume:
            if text:
                text = '(%s) ' % localization.formatters.FormatNumeric(self.secondaryVolume, useGrouping=True, decimalPlaces=1) + text
        self.capacityText.text = text

    def HideLabel(self):
        self.capacityText.Hide()

    def ShowLabel(self):
        self.capacityText.Show()

    def GetHint(self):
        return self.capacityText.text

    @telemetry.ZONE_METHOD
    def SetAdditionalVolume(self, items=[]):
        if not self.invCont:
            return
        volume = 0
        for item in items:
            volume += GetItemVolume(item)

        self.additionalVolume = volume
        value = self.GetVolumeProportion(volume)
        animValue = min(value, 1.0 - self.capacityGauge.width)
        currWidth = self.capacityGaugeAdd.width
        duration = 0.5 * fabs(currWidth - animValue) ** 0.3
        uicore.animations.MorphScalar(self.capacityGaugeAdd, 'width', currWidth, animValue, duration=duration)
        color = self.COLOR_SECONDARY
        if self.invCont.invController.hasCapacity:
            cap = self.invCont.invController.GetCapacity()
            if cap.capacity and volume + cap.used > cap.capacity:
                color = (0.6, 0, 0)
        self.capacityGaugeAdd.SetGradient(colorData=[(0.0, color)])
        self.UpdateLabel()

    @telemetry.ZONE_METHOD
    def SetSecondaryVolume(self, items=[]):
        volume = 0
        for item in items:
            volume += GetItemVolume(item)

        self.secondaryVolume = volume
        value = self.GetVolumeProportion(volume)
        currWidth = self.capacityGaugeSec.width
        duration = 0.5 * fabs(currWidth - value) ** 0.3
        uicore.animations.MorphScalar(self.capacityGaugeSec, 'width', currWidth, value, duration=duration)
        self.UpdateLabel()

    def GetVolumeProportion(self, volume):
        if self.invCont and self.invCont.invController.hasCapacity:
            cap = self.invCont.invController.GetCapacity()
            if cap.capacity:
                return min(1.0, volume / cap.capacity)

    def OnItemChange(self, item=None, change=None):
        if not self.invCont:
            return
        if item.itemID == util.GetActiveShip():
            return
        if item.locationID == self.invCont.invController.itemID:
            self.ResetGauges()
        if const.ixLocationID in change:
            if change[const.ixLocationID] == self.invCont.invController.itemID:
                self.ResetGauges()

    def ResetGauges(self):
        self.resetPending = True
        if self.refreshGaugesThread:
            return
        self.refreshGaugesThread = uthread.new(self._ResetGauges)

    def _ResetGauges(self):
        try:
            while self.resetPending:
                self.RefreshCapacity()
                nodes = self.invCont.scroll.GetSelected()
                self.SetSecondaryVolume([ node.item for node in nodes ])
                self.SetAdditionalVolume()
                self.resetPending = False
                blue.synchro.Sleep(500)

        finally:
            self.refreshGaugesThread = None

        return


class _InvContBase(uiprimitives.Container):
    __guid__ = 'invCont._InvContBase'
    default_name = 'InventoryContainer'
    default_showControls = False
    __notifyevents__ = ['OnPostCfgDataChanged', 'OnInvTempFilterChanged']
    __invControllerClass__ = None

    def ApplyAttributes(self, attributes):
        uiprimitives.Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.itemID = attributes.itemID
        self.displayName = attributes.displayName
        self.activeFilters = attributes.get('activeFilters', [])
        showControls = attributes.get('showControls', self.default_showControls)
        self.quickFilterInput = attributes.Get('quickFilterInput', None)
        self.invController = self._GetInvController(attributes)
        self.items = []
        self.cols = None
        self.droppedIconData = (None, None)
        self.iconWidth = 64
        import xtriui
        self.iconHeight = xtriui.InvItem.GetInvItemHeight()
        self.sr.resizeTimer = None
        self.scrollTimer = None
        self.tmpDropIdx = {}
        self.refreshingView = False
        self.reRefreshView = False
        self.changeViewModeThread = None
        self.hintText = None
        self.dragStart = None
        self.previouslyHighlighted = None
        self.dragContainer = None
        self.itemChangeThread = None
        self.initialized = False
        self.numFilteredItems = 0
        if showControls:
            import uicls
            self.topCont = uiprimitives.Container(parent=self, align=uiconst.TOTOP, height=22)
            uicls.InvContViewBtns(parent=self.topCont, align=uiconst.CENTERLEFT, controller=self)
            uicls.InvContQuickFilter(parent=self.topCont, align=uiconst.CENTERRIGHT, invCont=self)
        self.ConstructUI()
        return

    def ConstructUI(self):
        self.scroll = uicontrols.Scroll(parent=self, state=uiconst.UI_PICKCHILDREN)
        self.scroll.sr.id = 'containerWnd_%s' % self.invController.GetName()
        self.scroll.OnNewHeaders = self.OnNewHeadersSet
        self.scroll.allowFilterColumns = 1
        self.scroll.SetColumnsHiddenByDefault(uix.GetInvItemDefaultHiddenHeaders())
        self.scroll.dad = self
        self.scroll.Copy = self.Copy
        self.scroll.Cut = self.Cut
        self.scroll.Paste = self.Paste
        content = self.content = self.scroll.GetContentContainer()
        content.OnDragEnter = self.OnDragEnter
        content.OnDragExit = self.OnDragExit
        content.OnDropData = self.OnScrollContentDropData
        content.GetMenu = lambda : GetContainerMenu(self)
        content.OnMouseUp = self.scroll.OnMouseUp = self.OnScrollMouseUp
        content.OnMouseDown = self.scroll.OnMouseDown = self.OnScrollMouseDown
        self.invSvcCookie = sm.GetService('inv').Register(self)
        self.sortIconsBy, self.sortIconsDir = settings.user.ui.Get('containerSortIconsBy_%s' % self.name, ('type', 0))
        self.viewMode = settings.user.ui.Get('containerViewMode_%s' % self.name, 'icons')
        uthread.new(self.ChangeViewMode, ['icons', 'details', 'list'].index(self.viewMode))

    def _GetInvController(self, attributes):
        return self.__invControllerClass__(itemID=attributes.itemID)

    def SetInvContViewMode(self, value):
        self.ChangeViewMode(value)

    def SetQuickFilterInput(self, filterTxt=''):
        if len(filterTxt) > 0:
            self.quickFilterInput = filterTxt.lower()
            self.Refresh()
        else:
            prefilter = self.quickFilterInput
            self.quickFilterInput = None
            if prefilter != None:
                self.Refresh()
            self.hintText = None
        return

    def QuickFilter(self, item):
        name = uix.GetItemName(item).lower()
        typename = evetypes.GetName(item.typeID).lower()
        input = self.quickFilterInput.lower()
        return name.find(input) + 1 or typename.find(input) + 1

    def OnInvTempFilterChanged(self):
        self.Refresh()

    def SetFilters(self, filters):
        self.activeFilters = filters
        self.Refresh()

    def FilterOptionsChange(self, combo, label, value, *args):
        if combo and combo.name == 'filterCateg':
            if value is None:
                ops = [(localization.GetByLabel('UI/Inventory/Filters/All'), None)]
            else:
                ops = sm.GetService('marketutils').GetFilterops(value)
            self.sr.filterGroup.LoadOptions(ops)
            settings.user.ui.Set('containerCategoryFilter%s' % self.name.title(), value)
        elif combo and combo.name == 'filterGroup':
            settings.user.ui.Set('containerGroupFilter%s' % self.name.title(), value)
        self.Refresh()
        return

    def OnPostCfgDataChanged(self, what, data):
        if what == 'evelocations':
            itemID = data[0]
            for each in self.scroll.GetNodes():
                if each and getattr(each, 'item', None) and each.item.itemID == itemID:
                    each.name = None
                    uix.GetItemLabel(each.item, each, 1)
                    if each.panel:
                        each.panel.UpdateLabel()
                    return

        return

    def _OnClose(self, *args):
        if self.itemChangeThread:
            self.itemChangeThread.kill()

    def ChangeViewMode(self, viewMode=0):
        if self.changeViewModeThread:
            self.changeViewModeThread.kill()
        self.changeViewModeThread = uthread.new(self._ChangeViewMode, viewMode)

    def _ChangeViewMode(self, viewMode=0):
        if self.destroyed:
            return
        else:
            self.viewMode = ['icons', 'details', 'list'][viewMode]
            settings.user.ui.Set('containerViewMode_%s' % self.name, self.viewMode)
            self.items = self.invController.GetItems()
            self.invController.OnItemsViewed()
            self.PrimeItems([ item for item in self.items if item is not None ])
            if self.items:
                self.items = self.FilterItems(self.items)
            self.UpdateHint()
            try:
                if self.viewMode == 'icons':
                    self.SortIconsBy(self.sortIconsBy, self.sortIconsDir)
                else:
                    self.RefreshView()
            except UserError:
                self.Close()
                if self.sr.Get('cookie', None):
                    sm.GetService('inv').Unregister(self.invSvcCookie)
                raise

            return

    def FilterItems(self, items):
        oldNum = len(items)
        if self.quickFilterInput:
            items = uiutil.NiceFilter(self.QuickFilter, items)
        for filter in self.activeFilters:
            items = sm.GetService('itemFilter').FilterItems(items, filter)

        if self.invController.filtersEnabled:
            items = sm.GetService('itemFilter').ApplyTempFilter(items)
        self.numFilteredItems = oldNum - len(items)
        return items

    def UpdateHint(self):
        if len(self.items) == 0:
            if self.numFilteredItems:
                self.hintText = localization.GetByLabel('UI/Inventory/NothingFoundFiltered', numFilters=self.numFilteredItems)
            elif not self.invController.CheckCanQuery():
                self.hintText = localization.GetByLabel('UI/Inventory/NoAccessHint')
            else:
                self.hintText = localization.GetByLabel('UI/Common/NothingFound')
        else:
            self.hintText = ''
        self.scroll.ShowHint(self.hintText)

    def Refresh(self):
        self.ChangeViewMode(['icons', 'details', 'list'].index(self.viewMode))

    def SortIconsBy(self, sortby, direction):
        self.sortIconsBy = sortby
        self.sortIconsDir = direction
        settings.user.ui.Set('containerSortIconsBy_%s' % self.name, (sortby, direction))
        sortData = []
        for rec in self.items:
            if rec is None:
                continue
            name = uiutil.StripTags(uix.GetItemName(rec).lower())
            type = uiutil.StripTags(uix.GetCategoryGroupTypeStringForItem(rec).lower())
            id = rec.itemID
            qty = 0
            if not (rec.singleton or rec.typeID in (const.typeBookmark,)):
                qty = rec.stacksize
            if sortby == 'name':
                sortKey = (name,
                 type,
                 qty,
                 id,
                 rec)
            elif sortby == 'qty':
                sortKey = (qty,
                 type,
                 name,
                 id,
                 rec)
            elif sortby == 'type':
                sortKey = (type,
                 name,
                 qty,
                 id,
                 rec)
            else:
                log.LogError('Unknown sortkey used in container sorting', sortby, direction)
                continue
            sortData.append((sortKey, rec))

        locCmpFunc = localization.util.GetSortFunc(localization.util.GetLanguageID())

        def _sort(left, right):
            if len(left) == 0:
                return 0
            if isinstance(left[0], basestring):
                res = locCmpFunc(left[0], right[0])
            else:
                res = cmp(left[0], right[0])
            if res == 0:
                return _sort(left[1:], right[1:])
            return res

        sortedList = sorted(sortData, cmp=_sort, key=lambda x: x[0])
        sortedList = [ x[1] for x in sortedList ]
        if direction:
            sortedList.reverse()
        self.items = sortedList
        self.RefreshView()
        return

    def _OnSizeChange_NoBlock(self, *args):
        self.sr.resizeTimer = base.AutoTimer(250, self.OnEndScale_)

    def OnEndScale_(self, *etc):
        if self.destroyed:
            self.sr.resizeTimer = None
            return
        elif not self.initialized:
            return
        else:
            self.sr.resizeTimer = None
            oldcols = self.cols
            self.RefreshCols()
            if self.viewMode == 'icons':
                if self.refreshingView:
                    self.reRefreshView = True
                    return
                if oldcols != self.cols:
                    uthread.new(self.RefreshView)
            return

    @telemetry.ZONE_METHOD
    def AddItem(self, rec, index=None, fromWhere=None):
        if self.quickFilterInput:
            if not self.QuickFilter(rec):
                return
        if not self.FilterItems([rec]):
            return
        else:
            lg.Info('vcont', 'AddItem', fromWhere, rec.stacksize, evetypes.GetName(rec.typeID))
            for node in self.scroll.sr.nodes:
                if self.viewMode in ('details', 'list'):
                    if node is not None and node.Get('item', None) and node.item.itemID == rec.itemID:
                        lg.Warn('vcont', 'Tried to add an item that is already there??')
                        self.UpdateItem(node.item)
                        return
                else:
                    for internalNode in node.internalNodes:
                        if internalNode is not None and internalNode.item.itemID == rec.itemID:
                            lg.Warn('vcont', 'Tried to add an item that is already there??')
                            self.UpdateItem(internalNode.item)
                            return

            import listentry
            if self.viewMode in ('details', 'list'):
                self.items.append(rec)
                self.scroll.AddEntries(-1, [listentry.Get('InvItem', data=uix.GetItemData(rec, self.viewMode, self.invController.viewOnly, container=self, scrollID=self.scroll.sr.id))])
                self.UpdateHint()
            else:
                if index is not None:
                    while index < len(self.items):
                        if self.items[index] is None:
                            return self.SetItem(index, rec)
                        index += 1

                    while index >= len(self.scroll.sr.nodes) * self.cols:
                        self.AddRow()

                    return self.SetItem(index, rec)
                if len(self.items) and None in self.items:
                    idx = self.tmpDropIdx.get(rec.itemID, None)
                    if idx is None:
                        idx = self.items.index(None)
                    return self.SetItem(idx, rec)
                if not self.cols:
                    self.RefreshCols()
                if index >= len(self.scroll.sr.nodes) * self.cols:
                    self.AddRow()
                return self.SetItem(0, rec)
            return

    @telemetry.ZONE_METHOD
    def UpdateItem(self, rec, *etc):
        lg.Info('vcont', 'UpdateItem', rec and '[%s %s]' % (rec.stacksize, evetypes.GetName(rec.typeID)))
        if self.viewMode in ('details', 'list'):
            idx = 0
            for each in self.items:
                if each.itemID == rec.itemID:
                    self.items[idx] = rec
                    break
                idx += 1

            for entry in self.scroll.sr.nodes:
                if entry.item.itemID == rec.itemID:
                    newentry = uix.GetItemData(rec, self.viewMode, self.invController.viewOnly, container=self, scrollID=self.scroll.sr.id)
                    for key, value in newentry.iteritems():
                        entry[key] = value

                    if entry.panel:
                        entry.panel.Load(entry)
                    self.UpdateHint()
                    return

        else:
            i = 0
            for rowNode in self.scroll.sr.nodes:
                for entry in rowNode.internalNodes:
                    if entry is not None and entry.item and entry.item.itemID == rec.itemID:
                        self.SetItem(i, rec)
                        return
                    i += 1

        lg.Warn('vcont', 'Tried to update an item that is not there??')
        return

    @telemetry.ZONE_METHOD
    def RemoveItem(self, rec):
        lg.Info('vcont', 'RemoveItem', rec and '[%s %s]' % (rec.stacksize, evetypes.GetName(rec.typeID)))
        if self.viewMode in ('details', 'list'):
            for entry in self.scroll.sr.nodes:
                if entry.item.itemID == rec.itemID:
                    self.scroll.RemoveEntries([entry])
                    break

            for item in self.items:
                if item.itemID == rec.itemID:
                    self.items.remove(item)

        else:
            i = 0
            for rowNode in self.scroll.sr.nodes:
                si = 0
                for entry in rowNode.internalNodes:
                    if entry and entry.item and entry.item.itemID == rec.itemID:
                        self.SetItem(i, None)
                        rowNode.internalNodes[si] = None
                        break
                    si += 1
                    i += 1

            i = 0
            for item in self.items:
                if item and item.itemID == rec.itemID:
                    self.items[i] = None
                i += 1

            self.CleanupRows()
        return

    @telemetry.ZONE_METHOD
    def CleanupRows(self):
        rm = []
        for rowNode in self.scroll.sr.nodes:
            internalNodes = rowNode.Get('internalNodes', [])
            if internalNodes == [None] * len(internalNodes):
                rm.append(rowNode)
            else:
                rm = []

        if rm:
            self.scroll.RemoveEntries(rm)
        return

    @telemetry.ZONE_METHOD
    def AddRow(self):
        self.items += [None] * self.cols
        import listentry
        self.scroll.AddEntries(-1, [listentry.Get('VirtualContainerRow', {'lenitems': len(self.scroll.sr.nodes) * self.cols,
          'rec': [None] * self.cols,
          'internalNodes': [None] * self.cols,
          'parentWindow': self,
          'hilightable': False,
          'container': self})])
        self.scroll.UpdatePosition()
        return

    @telemetry.ZONE_METHOD
    def StackAll(self):
        self.invController.StackAll()
        uthread.new(self.Refresh)

    def OnScrollContentDropData(self, dragObj, nodes):
        idx = None
        if self.viewMode == 'icons' and self.cols:
            l, t = self.scroll.GetAbsolutePosition()
            idx = self.cols * len(self.scroll.sr.nodes) + (uicore.uilib.x - l) // (64 + colMargin)
        sm.ScatterEvent('OnInvContDragExit', self.invController.GetInvID(), [])
        self.OnDropDataWithIdx(nodes, idx)
        return

    def OnDragEnter(self, dragObj, nodes):
        sm.ScatterEvent('OnInvContDragEnter', self.invController.GetInvID(), nodes)

    def OnDragExit(self, dragObj, nodes):
        sm.ScatterEvent('OnInvContDragExit', self.invController.GetInvID(), nodes)

    def OnDropData(self, dragObj, nodes):
        return self.OnDropDataWithIdx(nodes)

    def Cut(self):
        items = self.scroll.GetSelected()
        sm.GetService('inv').SetItemClipboard(items)

    def Copy(self):
        if bool(session.role & service.ROLE_PROGRAMMER):
            items = self.scroll.GetSelected()
            sm.GetService('inv').SetItemClipboard(items, copy=True)
        return uicontrols.Scroll.Copy(self.scroll)

    def Paste(self, value):
        items, copy = sm.GetService('inv').PopItemClipboard()
        if copy and bool(session.role & service.ROLE_PROGRAMMER):
            import param
            for item in items:
                itemID = sm.GetService('slash').cmd_createitem(param.ParamObject('%s %s' % (item.rec.typeID, item.rec.stacksize)))
                if itemID:
                    invController = invCtrl.StationItems() if session.stationid else invCtrl.ShipCargo()
                    blue.synchro.SleepWallclock(100)
                    newItem = invController.GetItem(itemID)
                    if newItem:
                        self.invController.AddItems([newItem])

        else:
            self.invController.OnDropData(items)

    @telemetry.ZONE_METHOD
    def OnDropDataWithIdx(self, nodes, idx=None):
        self.scroll.ClearSelection()
        if len(nodes) and getattr(nodes[0], 'scroll', None) and not nodes[0].scroll.destroyed:
            nodes[0].scroll.ClearSelection()
        if nodes and getattr(nodes[0], 'item', None) in self.invController.GetItems() and not uicore.uilib.Key(uiconst.VK_SHIFT):
            if getattr(nodes[0], 'scroll', None) != self.scroll:
                return
            if idx is not None:
                for i, node in enumerate(nodes):
                    self.tmpDropIdx[node.itemID] = idx + i

            for node in nodes:
                idx = self.tmpDropIdx.get(node.itemID, None)
                if idx is None:
                    if None in self.items:
                        idx = self.items.index(None)
                    else:
                        idx = len(self.items)
                self.OnItemDrop(idx, node)

            return
        else:
            return self.invController.OnDropData(nodes)

    @telemetry.ZONE_METHOD
    def OnItemDrop(self, index, node):
        if self.viewMode not in ('details', 'list'):
            self.RemoveItem(node.item)
            self.AddItem(node.item, index)

    @telemetry.ZONE_METHOD
    def SetItem(self, index, rec):
        lg.Info('vcont', 'SetItem', index, rec and '[%s %s]' % (rec.stacksize, evetypes.GetName(rec.typeID)))
        if not self or self.destroyed:
            return
        else:
            if index < len(self.items) and rec and self.items[index] is not None and self.items[index].itemID != rec.itemID:
                while index < len(self.items) and self.items[index] is not None:
                    index += 1

            if self.cols:
                rowIndex = index // self.cols
            else:
                rowIndex = 0
            while rowIndex >= len(self.scroll.sr.nodes):
                self.AddRow()

            while index >= len(self.items):
                self.items += [None]

            self.items[index] = rec
            try:
                self.scroll.sr.nodes[rowIndex].rec[index % self.cols] = rec
                self.UpdateHint()
                node = None
                if rec:
                    node = uix.GetItemData(rec, self.viewMode, self.invController.viewOnly, container=self, scrollID=self.scroll.sr.id)
                    if not self or self.destroyed:
                        return
                    node.scroll = self.scroll
                    node.panel = None
                    node.idx = index
                    node.__guid__ = 'xtriui.InvItem'
                self.scroll.sr.nodes[index // self.cols].internalNodes[index % self.cols] = node
            except IndexError:
                return

            icon = self.GetIcon(index)
            if icon:
                if rec is None:
                    icon.state = uiconst.UI_HIDDEN
                    icon.sr.node = None
                else:
                    icon.state = uiconst.UI_NORMAL
                    node.panel = icon
                    node.viewOnly = self.invController.viewOnly
                    icon.Load(node)
            return

    @telemetry.ZONE_METHOD
    def RefreshCols(self):
        w = self.scroll.GetContentWidth()
        self.cols = max(1, w // (64 + colMargin))

    def PrimeItems(self, itemlist):
        locations = []
        vouchers = []
        for rec in itemlist:
            if rec.categoryID == const.categoryStation and rec.groupID == const.groupStation:
                locations.append(rec.itemID)
                locations.append(rec.locationID)
            if rec.singleton and (rec.categoryID == const.categoryShip or rec.groupID in (const.groupWreck,
             const.groupCargoContainer,
             const.groupSecureCargoContainer,
             const.groupAuditLogSecureContainer,
             const.groupFreightContainer,
             const.groupBiomass)):
                locations.append(rec.itemID)
            if rec.typeID == const.typeBookmark:
                vouchers.append(rec.itemID)

        if vouchers:
            sm.GetService('voucherCache').PrimeVoucherNames(vouchers)
        if locations:
            cfg.evelocations.Prime(locations)

    def OnNewHeadersSet(self, *args):
        self.RefreshView()

    @telemetry.ZONE_METHOD
    def RefreshView(self, *args):
        if self.refreshingView:
            return
        else:
            self.refreshingView = 1
            try:
                if self.viewMode in ('details', 'list'):
                    self.scroll.sr.id = 'containerWnd_%s' % self.invController.GetName()
                    self.scroll.hiliteSorted = 1
                    scrolllist = []
                    import listentry
                    for rec in self.items:
                        if rec:
                            id = self.scroll.sr.id
                            theData = uix.GetItemData(rec, self.viewMode, self.invController.viewOnly, container=self, scrollID=id)
                            list = listentry.Get('InvItem', data=theData)
                            scrolllist.append(list)

                    hdr = uix.GetInvItemDefaultHeaders()
                    scrll = self.scroll.GetScrollProportion()
                    theSc = self.scroll
                    theSc.Load(contentList=scrolllist, headers=hdr, scrollTo=scrll)
                else:
                    if not self.cols:
                        self.RefreshCols()
                    while self.items and self.items[-1] is None:
                        self.items = self.items[:-1]

                    content = []
                    selectedItems = [ node.item for node in self.scroll.GetSelected() ]
                    import listentry
                    for i in xrange(len(self.items)):
                        blue.pyos.BeNice()
                        if not i % self.cols:
                            entry = [None] * self.cols
                            nodes = [None] * self.cols
                            content.append(listentry.Get('VirtualContainerRow', {'lenitems': i,
                             'rec': entry,
                             'internalNodes': nodes,
                             'parentWindow': self,
                             'hilightable': False,
                             'container': self}))
                        if self.items[i]:
                            node = uix.GetItemData(self.items[i], self.viewMode, self.invController.viewOnly, container=self)
                            node.scroll = self.scroll
                            node.panel = None
                            node.__guid__ = 'xtriui.InvItem'
                            node.idx = i
                            node.selected = node.item in selectedItems
                            nodes[i % self.cols] = node
                            entry[i % self.cols] = self.items[i]

                    self.scroll.sr.sortBy = None
                    self.scroll.sr.id = None
                    self.scroll.Load(fixedEntryHeight=self.iconHeight + rowMargin, contentList=content, scrollTo=self.scroll.GetScrollProportion())
                    self.CleanupRows()
                self.UpdateHint()
                self.initialized = True
                sm.ScatterEvent('OnInvContRefreshed', self)
            finally:
                if not self.destroyed:
                    if self.viewMode == 'details':
                        self.scroll.sr.minColumnWidth = {localization.GetByLabel('UI/Common/Name'): 44}
                        self.scroll.UpdateTabStops()
                    else:
                        self.scroll.sr.minColumnWidth = {}
                    self.refreshingView = 0
                    if self.reRefreshView:
                        self.reRefreshView = False
                        self.RefreshCols()
                        uthread.new(self.RefreshView)

            return

    def SelectAll(self):
        if not self.destroyed:
            self.scroll.SelectAll()

    def InvertSelection(self):
        if not self.destroyed:
            self.scroll.ToggleSelected()

    def GetIcons(self):
        return [ icon for row in self.scroll.GetContentContainer().children for icon in row.sr.icons if icon.state == uiconst.UI_NORMAL ]

    def OnScrollMouseDown(self, *args):
        if args[0] == uiconst.MOUSELEFT:
            self.dragStart = (uicore.uilib.x - self.scroll.GetContentContainer().absoluteLeft, uicore.uilib.y - self.scroll.GetContentContainer().absoluteTop)
            if uicore.uilib.Key(uiconst.VK_CONTROL) or uicore.uilib.Key(uiconst.VK_SHIFT):
                self.previouslyHighlighted = [ x.panel for x in self.scroll.GetSelected() ]
            else:
                self.previouslyHighlighted = []
            dragContainer = getattr(self, 'dragContainer', None)
            if dragContainer is None or dragContainer.destroyed:
                self.dragContainer = uiprimitives.Container(parent=self.scroll.GetContentContainer(), align=uiconst.TOPLEFT, idx=0)
                FrameThemeColored(parent=self.dragContainer, frameConst=uiconst.FRAME_BORDER1_CORNER3, colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=0.5)
                FillThemeColored(parent=self.dragContainer, frameConst=uiconst.FRAME_FILLED_CORNER3, opacity=0.3)
            self.dragContainer.Hide()
            uthread.new(self.RubberbandSelection_thread)
        return

    def RubberbandSelection_thread(self, *args):
        while self.dragStart and uicore.uilib.leftbtn and trinity.app.IsActive():
            startX, startY = self.dragStart
            currentX, currentY = uicore.uilib.x - self.scroll.GetContentContainer().absoluteLeft, uicore.uilib.y - self.scroll.GetContentContainer().absoluteTop
            if startX > currentX:
                temp = currentX
                currentX = startX
                startX = temp
            if startY > currentY:
                temp = currentY
                currentY = startY
                startY = temp
            left = max(startX, 0)
            width = min(currentX, self.scroll.GetContentContainer().width) - max(startX, 0)
            top = max(startY, 0)
            height = min(currentY, self.scroll.GetContentContainer().height) - max(startY, 0)
            self.dragContainer.left = left
            self.dragContainer.top = top
            self.dragContainer.width = width
            self.dragContainer.height = height
            self.dragContainer.Show()
            if not self.scrollTimer:
                self.scrollTimer = base.AutoTimer(250, self.ScrollTimer)
            import listentry
            for each in self.scroll.GetContentContainer().children:
                if isinstance(each, listentry.VirtualContainerRow):
                    if each.top >= startY and each.top + each.height <= currentY or each.top + each.height >= startY and each.top <= currentY:
                        for icon in each.sr.icons:
                            if icon.left >= startX and icon.left + icon.width <= currentX or icon.left + icon.width >= startX and icon.left <= currentX:
                                if icon in self.previouslyHighlighted:
                                    if uicore.uilib.Key(uiconst.VK_SHIFT):
                                        icon.Select()
                                    elif uicore.uilib.Key(uiconst.VK_CONTROL):
                                        icon.Deselect()
                                else:
                                    icon.Select()
                            elif icon not in self.previouslyHighlighted:
                                icon.Deselect()
                            else:
                                icon.Select()

                    else:
                        for icon in each.sr.icons:
                            if icon not in self.previouslyHighlighted:
                                icon.Deselect()
                            else:
                                icon.Select()

                elif isinstance(each, listentry.InvItem):
                    if each.top >= startY and each.top + each.height <= currentY or each.top + each.height >= startY and each.top <= currentY:
                        each.Select()
                        if each in self.previouslyHighlighted:
                            if uicore.uilib.Key(uiconst.VK_SHIFT):
                                each.Select()
                            elif uicore.uilib.Key(uiconst.VK_CONTROL):
                                each.Deselect()
                        else:
                            each.Select()
                    elif each not in self.previouslyHighlighted:
                        each.Deselect()
                    else:
                        each.Select()

            blue.pyos.synchro.SleepSim(10)

        self.scrollTimer = None
        self.dragStart = None
        self.previouslyHighlighted = None
        self.scrollTimer = None
        self.dragContainer.Hide()
        return

    def OnScrollMouseUp(self, *args):
        if self.dragStart and args[0] == uiconst.MOUSELEFT:
            startX, startY = self.dragStart
            endX, endY = uicore.uilib.x - self.scroll.GetContentContainer().absoluteLeft, uicore.uilib.y - self.scroll.GetContentContainer().absoluteTop
            if startX > endX:
                temp = endX
                endX = startX
                startX = temp
            if startY > endY:
                temp = endY
                endY = startY
                startY = temp
            preSelectedNodes = self.scroll.GetSelected() if uicore.uilib.Key(uiconst.VK_CONTROL) or uicore.uilib.Key(uiconst.VK_SHIFT) else []
            selectedNodes = []
            import listentry
            for each in self.scroll.GetContentContainer().children:
                if isinstance(each, listentry.VirtualContainerRow):
                    if each.top >= startY and each.top + each.height <= endY or each.top + each.height >= startY and each.top <= endY:
                        for icon in each.sr.icons:
                            if icon.left >= startX and icon.left + icon.width <= endX or icon.left + icon.width >= startX and icon.left <= endX:
                                if icon.sr.node:
                                    selectedNodes.append(icon.sr.node)

                elif isinstance(each, listentry.InvItem):
                    if each.top >= startY and each.top + each.height <= endY or each.top + each.height >= startY and each.top <= endY:
                        selectedNodes.append(each.sr.node)

            if uicore.uilib.Key(uiconst.VK_SHIFT):
                selectedNodes.extend(preSelectedNodes)
            elif uicore.uilib.Key(uiconst.VK_CONTROL):
                newSelectedNodes = [ item for item in selectedNodes if item not in preSelectedNodes ]
                newSelectedNodes.extend([ item for item in preSelectedNodes if item not in selectedNodes ])
                selectedNodes = newSelectedNodes
            uthread.new(self.scroll.SelectNodes, selectedNodes)
            self.dragStart = None
            self.previouslyHighlighted = None
            self.scrollTimer = None
            self.dragContainer.Hide()
        return

    def ScrollTimer(self):
        if not self.dragStart:
            self.scrollTimer = None
            return
        else:
            aL, aT, aW, aH = self.scroll.GetAbsolute()
            if uicore.uilib.y < aT + 10:
                self.scroll.Scroll(1)
            elif uicore.uilib.y > aT + aH - 10:
                self.scroll.Scroll(-1)
            return

    def GetIcon(self, index):
        for each in self.scroll.GetContentContainer().children:
            if getattr(each, 'index', -1) == index // self.cols * self.cols:
                lg.Info('vcont', 'GetIcon(', index, ') returns', each.sr.icons[index % self.cols].name)
                return each.sr.icons[index % self.cols]

        lg.Info('vcont', 'GetIcon(', index, ') found nothing')
        return None

    def RegisterSpecialActionButton(self, button):
        pass


class Row(SE_BaseClassCore):
    __guid__ = 'listentry.VirtualContainerRow'
    default_showHilite = False

    def Startup(self, dad):
        self.dad = dad.dad
        self.initialized = False
        self.sr.icons = []

    @telemetry.ZONE_METHOD
    def Load(self, node):
        if self.initialized:
            return
        else:
            self.initialized = True
            self.sr.node = node
            self.index = node.lenitems
            import xtriui
            for i in range(len(self.sr.icons), len(node.internalNodes)):
                icon = xtriui.InvItem(parent=self)
                icon.top = rowMargin
                icon.left = colMargin + (icon.width + colMargin) * i
                icon.height = xtriui.InvItem.GetInvItemHeight()
                self.sr.icons.append(icon)

            for icon in self.sr.icons[self.dad.cols:]:
                icon.sr.node = None
                icon.subnodeIdx = None

            i = 0
            for subnode in node.internalNodes:
                icon = self.sr.icons[i]
                if subnode is None:
                    icon.state = uiconst.UI_HIDDEN
                    icon.sr.node = None
                    icon.subnodeIdx = None
                else:
                    subnode.panel = icon
                    icon.Load(subnode)
                    icon.state = uiconst.UI_NORMAL
                    icon.subnodeIdx = subnode.idx = self.index + i
                i += 1

            return

    def GetMenu(self):
        return GetContainerMenu(self.dad)

    def OnDropData(self, dragObj, nodes):
        l, t, w, h = self.GetAbsolute()
        index = self.index + (uicore.uilib.x - l) // (64 + colMargin)
        self.dad.OnDropDataWithIdx(nodes, index)

    def OnDragEnter(self, dragObj, nodes):
        self.sr.node.container.OnDragEnter(dragObj, nodes)

    def OnDragExit(self, dragObj, nodes):
        self.sr.node.container.OnDragExit(dragObj, nodes)

    def OnMouseDown(self, *etc):
        if self.dad.scroll:
            self.dad.scroll.OnMouseDown(*etc)

    def OnMouseUp(self, *etc):
        if self.dad.scroll:
            self.dad.scroll.OnMouseUp(*etc)

    def OnMouseMove(self, *etc):
        if self.dad.scroll:
            self.dad.scroll.OnMouseMove(*etc)

    def ShowSelected(self, *args):
        pass


def GetContainerMenu(containerWindow):
    m = []
    if eve.rookieState:
        return m
    else:
        m += [(uiutil.MenuLabel('UI/Common/SelectAll'), containerWindow.SelectAll), (uiutil.MenuLabel('UI/Inventory/InvertSelection'), containerWindow.InvertSelection)]
        if eve.session.role & (service.ROLE_GML | service.ROLE_WORLDMOD):
            m += [(uiutil.MenuLabel('UI/Commands/Refresh'), containerWindow.Refresh)]
        if containerWindow.viewMode == 'icons':
            m += [(uiutil.MenuLabel('UI/Common/SortBy'), [(uiutil.MenuLabel('UI/Common/Name'), containerWindow.SortIconsBy, ('name', 0)),
               (uiutil.MenuLabel('UI/Inventory/NameReversed'), containerWindow.SortIconsBy, ('name', 1)),
               None,
               (uiutil.MenuLabel('UI/Inventory/ItemQuantity'), containerWindow.SortIconsBy, ('qty', 0)),
               (uiutil.MenuLabel('UI/Inventory/QuantityReversed'), containerWindow.SortIconsBy, ('qty', 1)),
               None,
               (uiutil.MenuLabel('UI/Common/Type'), containerWindow.SortIconsBy, ('type', 0)),
               (uiutil.MenuLabel('UI/Inventory/TypeReversed'), containerWindow.SortIconsBy, ('type', 1))])]
        if containerWindow.invController.viewOnly:
            return m
        containerItem = containerWindow.invController.GetInventoryItem()
        containerOwnerID = containerItem.ownerID
        myOwnerIDs = (session.charid, session.corpid, session.allianceid)
        containerSlim = sm.GetService('michelle').GetItem(containerItem.itemID)
        stackAll = containerItem.groupID in (const.groupStation, const.groupPlanetaryCustomsOffices) or containerItem.categoryID in (const.categoryStructure,) or containerOwnerID in myOwnerIDs or session.corpid == getattr(containerSlim, 'corpID', None) or session.allianceid and session.allianceid == getattr(containerSlim, 'allianceID', None)
        if stackAll:
            m += [(uiutil.MenuLabel('UI/Inventory/StackAll'), containerWindow.StackAll)]
        return m


class MiniButton(uicontrols.Icon):
    __guid__ = 'uicontrols.MiniButton'

    def ApplyAttributes(self, attributes):
        self.idleIcon = attributes.icon
        uicontrols.Icon.ApplyAttributes(self, attributes)
        self.selectedIcon = attributes.selectedIcon
        self.mouseOverIcon = attributes.mouseOverIcon
        self.groupID = attributes.groupID
        self.func = attributes.func
        self.selected = False
        self.keepselection = True

    def OnMouseEnter(self, *args):
        self.LoadIcon(self.mouseOverIcon, ignoreSize=True)

    def OnMouseExit(self, *args):
        if self.selected:
            self.LoadIcon(self.selectedIcon, ignoreSize=True)
        else:
            self.LoadIcon(self.idleIcon, ignoreSize=True)

    def OnMouseDown(self, *args):
        self.LoadIcon(self.selectedIcon, ignoreSize=True)

    def OnMouseUp(self, *args):
        if uicore.uilib.mouseOver is self:
            self.LoadIcon(self.mouseOverIcon, ignoreSize=True)

    def OnClick(self, *args):
        if self.keepselection:
            self.Select()
        else:
            self.Deselect()
        self.Click()

    def Click(self, *args):
        self.func()

    def Deselect(self):
        self.selected = 0
        self.LoadIcon(self.idleIcon, ignoreSize=True)

    def Select(self):
        if self.groupID:
            for child in self.parent.children:
                if child == self:
                    continue
                if isinstance(child, MiniButton) and child.groupID == self.groupID:
                    child.Deselect()

            self.selected = True
        elif self.selected:
            self.Deselect()
        else:
            self.selected = True
        if self.selected:
            self.LoadIcon(self.selectedIcon, ignoreSize=True)