# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\carbonui\control\basicDynamicScroll.py
import telemetry
import uthread
import _weakref
import log
import carbonui.const as uiconst
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.primitives.container import Container
from carbonui.control.scroll import ScrollCoreOverride as Scroll

class BasicDynamicScroll(Scroll):
    __guid__ = 'uicontrols.BasicDynamicScroll'
    isTabStop = 1
    scrollEnabled = True
    default_name = 'scroll'
    default_multiSelect = 1
    default_stickToBottom = 0
    default_state = uiconst.UI_NORMAL
    default_autoPurgeHiddenEntries = True

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.sr.maincontainer = Container(parent=self, name='maincontainer', padding=(1, 1, 1, 1), clipChildren=True)
        self.sr.clipper = Container(name='__clipper', align=uiconst.TOALL, parent=self.sr.maincontainer, clipChildren=True)
        self.sr.clipper._OnSizeChange_NoBlock = self.OnClipperResize
        self.sr.content = Container(name='__content', align=uiconst.RELATIVE, parent=self.sr.clipper, state=uiconst.UI_NORMAL)
        self.loadingWheel = None
        self.Release()
        self.multiSelect = attributes.get('multiSelect', self.default_multiSelect)
        self.stickToBottom = attributes.get('stickToBottom', self.default_stickToBottom)
        self.autoPurgeHiddenEntries = attributes.get('autoPurgeHiddenEntries', self.default_autoPurgeHiddenEntries)
        self.sr.selfProxy = _weakref.proxy(self)
        self.Prepare_()
        self._mouseHoverCookie = uicore.uilib.RegisterForTriuiEvents(uiconst.UI_MOUSEHOVER, self.OnGlobalMouseHover)
        return

    def Close(self, *args, **kwds):
        self.cleanupTimer = None
        return Scroll.Close(self, *args, **kwds)

    def Release(self):
        self._loading = 0
        self._position = 0
        self._totalHeight = 0
        self.scrollingRange = 0
        self.sr.nodes = []
        self.visibleNodes = []
        self.sr.hint = None
        self.updatePositionThread = None
        self.debug = 0
        self.scrolling = 0
        self.scalingcol = 0
        self.lastSelected = None
        self.lastCharReceivedAt = 0
        self.currChars = ''
        self.hideBackground = False
        self.destroyInvisibleEntries = False
        self.lazyLoadNodes = False
        return

    @telemetry.ZONE_METHOD
    def ShowNodeIdx(self, idx, *args, **kwds):
        if self.scrollingRange:
            node = self.GetNode(idx)
            if not node:
                return
            fromTop = node.positionFromTop
            if fromTop is None:
                self.UpdateNodesWidthAndPosition()
                fromTop = node.positionFromTop
            if self._position > fromTop:
                portion = fromTop / float(self.scrollingRange)
                self.ScrollToProportion(portion)
            else:
                clipperWidth, clipperHeight = self.sr.clipper.GetAbsoluteSize()
                if fromTop + node.height > self._position + clipperHeight:
                    portion = (fromTop - clipperHeight + node.height) / float(self.scrollingRange)
                    self.ScrollToProportion(portion)
        return

    @telemetry.ZONE_METHOD
    def ChangeNodeIndex(self, newIndex, node):
        oldIndex = None
        if node in self.sr.nodes:
            oldIndex = self.sr.nodes.index(node)
            self.sr.nodes.remove(node)
        if newIndex == -1:
            newIndex = len(self.sr.nodes)
        self.sr.nodes.insert(newIndex, node)
        clipperWidth, clipperHeight = self.sr.clipper.GetAbsoluteSize()
        self.UpdateNodesWidthAndPosition(clipperWidth)
        self.UpdatePosition()
        return

    @telemetry.ZONE_METHOD
    def UpdateNodesWidthAndPosition(self, clipperWidth=None):
        if self.destroyed:
            return
        else:
            updateWidth = clipperWidth is not None
            fromTopPosition = 0
            for nodeIndex, node in enumerate(self.sr.nodes):
                if updateWidth and not node.fixedHeight and node._lastClipperWidth != clipperWidth:
                    node.height = node.dynamicHeightFunction(node, clipperWidth)
                    node._lastClipperWidth = clipperWidth
                if node.panel and node.panel.state != uiconst.UI_HIDDEN:
                    node.panel.top = fromTopPosition
                    if updateWidth:
                        node.panel.width = clipperWidth
                    node.panel.height = node.height
                node.positionFromTop = fromTopPosition
                node.idx = nodeIndex
                fromTopPosition += node.height

            if updateWidth:
                self.sr.content.width = clipperWidth
            self.SetTotalHeight(fromTopPosition)
            return

    def SetOrderedNodes(self, nodes, loadNodes=True):
        self.sr.nodes = nodes
        self.UpdateNodesWidthAndPosition()
        return self.UpdatePosition(loadNodes=loadNodes)

    def SetFilteredNodes(self, nodes, loadNodes=True):
        for visNode in self.visibleNodes:
            if visNode in nodes:
                continue
            displayScrollEntry = visNode.panel
            if displayScrollEntry and not displayScrollEntry.destroyed:
                displayScrollEntry.Close()
            visNode.panel = None

        self.sr.nodes = nodes
        self.UpdateNodesWidthAndPosition()
        return self.UpdatePosition(loadNodes=loadNodes)

    def ReloadNodes(self, nodes, updateHeight=False):
        if updateHeight:
            for node in nodes:
                node._lastClipperWidth = None

        clipperWidth, clipperHeight = self.sr.clipper.GetAbsoluteSize()
        self.UpdateNodesWidthAndPosition(clipperWidth)
        for node in nodes:
            if node.panel:
                node.panel.Load(node)

        self.UpdatePosition(fromWhere='ReloadNodes')
        return

    @telemetry.ZONE_METHOD
    def AddNodes(self, fromIdx, nodesData, updateScroll=True, *args, **kwds):
        if fromIdx == -1:
            fromIdx = len(self.sr.nodes)
        clipperWidth = None
        idx = fromIdx
        for node in nodesData:
            if node in self.sr.nodes:
                continue
            node.panel = None
            node.scroll = self.sr.selfProxy
            node.selected = node.get('isSelected', 0)
            fixedHeight = getattr(node.decoClass, 'ENTRYHEIGHT', None)
            if fixedHeight:
                node.fixedHeight = fixedHeight
                node.height = fixedHeight
            else:
                dynamicHeightFunction = getattr(node.decoClass, 'GetDynamicHeight', None)
                if dynamicHeightFunction:
                    if clipperWidth is None:
                        clipperWidth, clipperHeight = self.sr.clipper.GetAbsoluteSize()
                    node.dynamicHeightFunction = dynamicHeightFunction
                    node.height = dynamicHeightFunction(node, clipperWidth)
                    node._lastClipperWidth = clipperWidth
                else:
                    raise RuntimeError('Fatal error in baseScroll, nodeclass has to have either ENTRYHEIGHT or GetDynamicHeight function')
            preLoadFunction = getattr(node.decoClass, 'PreLoad', None)
            if preLoadFunction:
                preLoadFunction(node)
                if self.destroyed:
                    return
            self.sr.nodes.insert(idx, node)
            idx += 1

        if updateScroll:
            if clipperWidth is None:
                clipperWidth, clipperHeight = self.sr.clipper.GetAbsoluteSize()
            self.UpdateNodesWidthAndPosition(clipperWidth)
            self.UpdatePosition(fromWhere='AddNodes')
        return

    @telemetry.ZONE_METHOD
    def RemoveNodes(self, nodes, updateScroll=True):
        for node in nodes:
            if node.panel:
                node.panel.Close()
            if node in self.sr.nodes:
                self.sr.nodes.remove(node)

        if updateScroll:
            clipperWidth, clipperHeight = self.sr.clipper.GetAbsoluteSize()
            self.UpdateNodesWidthAndPosition(clipperWidth)
            self.UpdatePosition(fromWhere='RemoveNodes')

    @telemetry.ZONE_METHOD
    def Clear(self):
        self.sr.nodes = []
        self.visibleNodes = []
        self.sr.content.Flush()
        self.SetTotalHeight(0)
        self.UpdatePosition(fromWhere='RemoveNodes')

    @telemetry.ZONE_METHOD
    def PurgeInvisibleEntries(self, *args):
        self.cleanupTimer = None
        purgeCount = 0
        if self.sr.nodes:
            for node in self.sr.nodes:
                if not node.panel:
                    continue
                if node.panel.state != uiconst.UI_HIDDEN:
                    continue
                panel = node.panel
                node.panel = None
                panel.Close()
                purgeCount += 1

        return

    @telemetry.ZONE_METHOD
    def SetTotalHeight(self, newTotalHeight):
        self._totalHeight = max(0, newTotalHeight)
        atBottom = self._position and self._position == self.scrollingRange
        clipperWidth, clipperHeight = self.sr.clipper.GetCurrentAbsoluteSize()
        if not clipperWidth or not clipperHeight:
            clipperWidth, clipperHeight = self.sr.clipper.GetAbsoluteSize()
        self.scrollingRange = max(0, self._totalHeight - clipperHeight)
        if self.scrollingRange and self.scrollEnabled:
            self.sr.scrollcontrols.state = uiconst.UI_NORMAL
        else:
            self.sr.scrollcontrols.state = uiconst.UI_HIDDEN
        if not self.scrollingRange or atBottom or self.stickToBottom:
            self._position = self.scrollingRange
        self._position = min(self._position, self.scrollingRange)
        self.sr.content.height = max(clipperHeight, self._totalHeight)
        self.sr.content.width = clipperWidth

    @telemetry.ZONE_METHOD
    def UpdatePositionThreaded(self, *args, **kwds):
        killThread = self.updatePositionThread
        self.updatePositionThread = uthread.new(self.UpdatePosition)
        if killThread:
            killThread.kill()

    @telemetry.ZONE_METHOD
    def UpdatePosition(self, fromWhere=None, loadNodes=True):
        if self.destroyed:
            return
        else:
            clipperWidth, clipperHeight = self.sr.clipper.GetAbsoluteSize()
            self.sr.content.top = int(-self._position)
            self.UpdateScrollHandle(clipperHeight, fromWhere='UpdatePosition')
            scrollPosition = self._position
            UI_HIDDEN = uiconst.UI_HIDDEN
            while self.visibleNodes:
                node = self.visibleNodes.pop()
                displayScrollEntry = node.panel
                if not displayScrollEntry:
                    continue
                if displayScrollEntry.state != UI_HIDDEN:
                    aboveVisible = node.positionFromTop + displayScrollEntry.height < scrollPosition
                    belowVisible = scrollPosition + clipperHeight < node.positionFromTop
                    if aboveVisible or belowVisible:
                        if getattr(displayScrollEntry, '__notifyevents__', None) is not None:
                            sm.UnregisterNotify(displayScrollEntry)
                        displayScrollEntry.state = UI_HIDDEN

            positionFromTop = 0
            for node in self.sr.nodes:
                nodeheight = node.height
                positionFromTop = node.positionFromTop
                displayScrollEntry = node.panel
                if scrollPosition > positionFromTop + nodeheight:
                    continue
                belowVisible = scrollPosition + clipperHeight < positionFromTop
                if belowVisible:
                    break
                if not displayScrollEntry:
                    decoClass = node.decoClass
                    displayScrollEntry = decoClass(parent=self.sr.content, align=uiconst.TOPLEFT, pos=(0,
                     positionFromTop,
                     clipperWidth,
                     nodeheight), state=uiconst.UI_NORMAL, node=node)
                    displayScrollEntry.sr.node = node
                    node.panel = displayScrollEntry
                    node.scroll = self.sr.selfProxy
                    if hasattr(displayScrollEntry, 'Startup'):
                        displayScrollEntry.Startup(self.sr.selfProxy)
                elif displayScrollEntry.display:
                    self.visibleNodes.append(node)
                    displayScrollEntry.top = positionFromTop
                    displayScrollEntry.height = nodeheight
                    continue
                self.visibleNodes.append(node)
                displayScrollEntry.state = uiconst.UI_NORMAL
                displayScrollEntry.top = positionFromTop
                displayScrollEntry.width = clipperWidth
                displayScrollEntry.height = nodeheight
                if loadNodes:
                    displayScrollEntry.Load(node)
                if getattr(displayScrollEntry, '__notifyevents__', None) is not None:
                    sm.RegisterNotify(displayScrollEntry)

            self.updatePositionThread = None
            if self.autoPurgeHiddenEntries:
                self.cleanupTimer = AutoTimer(1500, self.PurgeInvisibleEntries)
            return

    @telemetry.ZONE_METHOD
    def GetNode(self, idx, *args, **kwds):
        allNodes = self.sr.nodes
        if allNodes:
            if idx == -1:
                return allNodes[-1]
            if len(allNodes) > idx:
                return allNodes[idx]
        return None

    @telemetry.ZONE_METHOD
    def OnContentResize(self, clipperWidth, clipperHeight, *args, **kw):
        if self.sr.hint:
            newWidth = clipperWidth - self.sr.hint.left * 2
            if abs(newWidth - self.sr.hint.width) > 12:
                self.sr.hint.width = newWidth
        if self.sr.content:
            self.UpdateNodesWidthAndPosition(clipperWidth)
            self.UpdatePositionThreaded(fromWhere='OnContentResize')
        if not self.destroyed:
            self.Resizing()

    def GetScrollRange(self):
        return self.scrollingRange

    def GetScrollControlsParent(self):
        return self.sr.scrollcontrols

    def Prepare_(self, *args, **kwds):
        return Scroll.Prepare_(self, *args, **kwds)

    def Prepare_Underlay_(self, *args, **kwds):
        return Scroll.Prepare_Underlay_(self, *args, **kwds)

    def Prepare_ScrollControls_(self, *args, **kwds):
        return Scroll.Prepare_ScrollControls_(self, *args, **kwds)

    def RemoveActiveFrame(self, *args, **kwds):
        return Scroll.RemoveActiveFrame(self, *args, **kwds)

    def HideBackground(self, *args, **kwds):
        return Scroll.HideBackground(self, *args, **kwds)

    HideUnderLay = HideBackground

    def SetNoBackgroundFlag(self, *args, **kwds):
        return Scroll.SetNoBackgroundFlag(self, *args, **kwds)

    def OnSetFocus(self, *args, **kwds):
        return Scroll.OnSetFocus(self, *args, **kwds)

    def OnKillFocus(self, *args, **kwds):
        return Scroll.OnKillFocus(self, *args, **kwds)

    def GetNodes(self, *args, **kwds):
        return self.sr.nodes

    def SetSelected(self, *args, **kwds):
        return Scroll.SetSelected(self, *args, **kwds)

    def ActivateIdx(self, *args, **kwds):
        return Scroll.ActivateIdx(self, *args, **kwds)

    def _SelectNode(self, *args, **kwds):
        return Scroll._SelectNode(self, *args, **kwds)

    def _DeselectNode(self, *args, **kwds):
        return Scroll._DeselectNode(self, *args, **kwds)

    def SelectNodes(self, *args, **kwds):
        return Scroll.SelectNodes(self, *args, **kwds)

    def SelectNode(self, *args, **kwds):
        return Scroll.SelectNode(self, *args, **kwds)

    def ReportSelectionChange(self, *args, **kwds):
        return Scroll.ReportSelectionChange(self, *args, **kwds)

    def DeselectAll(self, *args, **kwds):
        return Scroll.DeselectAll(self, *args, **kwds)

    def SelectAll(self, *args, **kwds):
        return Scroll.SelectAll(self, *args, **kwds)

    def ToggleSelected(self, *args, **kwds):
        return Scroll.ToggleSelected(self, *args, **kwds)

    def UpdateSelection(self, *args, **kwds):
        return Scroll.UpdateSelection(self, *args, **kwds)

    def ClearSelection(self, *args, **kwds):
        return Scroll.ClearSelection(self, *args, **kwds)

    def GetSelectedNodes(self, *args, **kwds):
        return Scroll.GetSelectedNodes(self, *args, **kwds)

    def GetSelected(self, *args, **kwds):
        return Scroll.GetSelected(self, *args, **kwds)

    def GetContentContainer(self, *args, **kwds):
        return Scroll.GetContentContainer(self, *args, **kwds)

    def OnKeyDown(self, *args, **kwds):
        return Scroll.OnKeyDown(self, *args, **kwds)

    def OnClipperResize(self, *args, **kwds):
        return Scroll.OnClipperResize(self, *args, **kwds)

    def GetContentWidth(self, *args, **kwds):
        return Scroll.GetContentWidth(self, *args, **kwds)

    def GetContentHeight(self, *args, **kwds):
        return Scroll.GetContentHeight(self, *args, **kwds)

    GetTotalHeight = GetContentHeight

    def GetContentParentSize(self, *args, **kwds):
        return Scroll.GetContentParentSize(self, *args, **kwds)

    def UpdatePositionLoop(self, *args, **kwds):
        Scroll.UpdatePositionLoop(self, *args, **kwds)

    def UpdateScrollHandle(self, *args, **kwds):
        return Scroll.UpdateScrollHandle(self, *args, **kwds)

    def OnChar(self, *args, **kwds):
        return Scroll.OnChar(self, *args, **kwds)

    def _OnCharThread(self, *args, **kwds):
        return Scroll._OnCharThread(self, *args, **kwds)

    def BrowseNodes(self, *args, **kwds):
        return Scroll.BrowseNodes(self, *args, **kwds)

    BrowseEntries = BrowseNodes

    def OnUp(self, *args, **kwds):
        return Scroll.OnUp(self, *args, **kwds)

    def OnDown(self, *args, **kwds):
        return Scroll.OnDown(self, *args, **kwds)

    def OnHome(self, *args, **kwds):
        return Scroll.OnHome(self, *args, **kwds)

    def OnEnd(self, *args, **kwds):
        return Scroll.OnEnd(self, *args, **kwds)

    def OnMouseWheel(self, *args, **kwds):
        return Scroll.OnMouseWheel(self, *args, **kwds)

    def Scroll(self, *args, **kwds):
        return Scroll.Scroll(self, *args, **kwds)

    def GetScrollProportion(self, *args, **kwds):
        return Scroll.GetScrollProportion(self, *args, **kwds)

    def ScrollToProportion(self, *args, **kwds):
        return Scroll.ScrollToProportion(self, *args, **kwds)

    def GetMinSize(self, *args, **kwds):
        return Scroll.GetMinSize(self, *args, **kwds)

    def GetNoItemNode(self, *args, **kwds):
        return Scroll.GetNoItemNode(self, *args, **kwds)

    def ShowHint(self, *args, **kwds):
        return Scroll.ShowHint(self, *args, **kwds)

    def GetNodeHeight(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll GetNodeHeight NOTACTIVE')

    def CheckOverlaysAndUnderlays(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll CheckOverlaysAndUnderlays NOTACTIVE')

    def RemoveEntries(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll RemoveEntries NOTACTIVE')

    def AddEntries(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll AddEntries NOTACTIVE')

    def CollectSubNodes(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll CollectSubNodes NOTACTIVE')

    def DrawHeaders(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll DrawHeaders NOT ACTIVE')

    def StartScaleCol(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll StartScaleCol NOT ACTIVE')

    def ScalingCol(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll ScalingCol NOT ACTIVE')

    def EndScaleCol(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll EndScaleCol NOT ACTIVE')

    def OnColumnChanged(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll OnColumnChanged NOT ACTIVE')

    def OnNewHeaders(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll OnNewHeaders NOT ACTIVE')

    def DblClickCol(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll DblClickCol NOT ACTIVE')

    def GetSortBy(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll GetSortBy NOTACTIVE')

    def GetSortDirection(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll GetSortDirection NOTACTIVE')

    def GetSmartSortDirection(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll GetSmartSortDirection NOTACTIVE')

    def ToggleSmartSortDirection(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll ToggleSmartSortDirection NOTACTIVE')

    def GetSortValue(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll GetSortValue NOTACTIVE')

    def _GetSortValue(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll _GetSortValue NOTACTIVE')

    def GetColumns(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll GetColumns NOTACTIVE')

    def GetHeaderMenu(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll GetHeaderMenu NOTACTIVE')

    def GetShowColumnMenu(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll GetShowColumnMenu NOTACTIVE')

    def MakePrimary(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll MakePrimary NOTACTIVE')

    def GetPrimaryColumn(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll GetPrimaryColumn NOTACTIVE')

    def SetColumnsHiddenByDefault(self, columns, *args):
        log.LogWarn('BasicDynamicScroll SetColumnsHiddenByDefault NOTACTIVE')

    def HideColumn(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll HideColumn NOTACTIVE')

    def ShowColumn(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll ShowColumn NOTACTIVE')

    def HideTriangle(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll HideTriangle NOTACTIVE')

    def Sort(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll Sort NOTACTIVE')

    def SortAsRoot(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll SortAsRoot NOTACTIVE')

    def GetStringFromNode(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll GetStringFromNode NOTACTIVE')

    def RefreshSort(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll RefreshSort NOTACTIVE')

    def ChangeSortBy(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll ChangeSortBy NOTACTIVE')

    def ChangeColumnOrder(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll ChangeColumnOrder NOTACTIVE')

    def HiliteSorted(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll HiliteSorted NOTACTIVE')

    def LoadHeaders(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll LoadHeaders NOTACTIVE')

    def __LoadHeaders(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll __LoadHeaders NOTACTIVE')

    def ResetColumnWidths(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll ResetColumnWidths NOTACTIVE')

    def ResetColumnWidth(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll ResetColumnWidth NOTACTIVE')

    def ApplyTabstopsToNode(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll ApplyTabstopsToNode NOTACTIVE')

    def UpdateTabStops(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll UpdateTabStops NOTACTIVE')

    def AddNode(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll AddNode NOTACTIVE')

    def PrepareSubContent(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll PrepareSubContent NOTACTIVE')

    def SetNodes(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll SetNodes NOTACTIVE')

    def RefreshNodes(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll RefreshNodes NOTACTIVE')

    def LoadContent(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll LoadContent NOTACTIVE')

    def Load(self, *args, **kwds):
        log.LogWarn('BasicDynamicScroll Load NOTACTIVE')


class BasicDynamicScrollOverride(BasicDynamicScroll):
    pass