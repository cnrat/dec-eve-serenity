# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\carbonui\control\scroll.py
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.control.label import LabelCore
from carbonui.control.scrollentries import SE_ListGroupCore
from carbonui.primitives.container import Container
from carbonui.control.menuLabel import MenuLabel
from carbonui.util.various_unsorted import GetAttrs, SmartCompare, GetWindowAbove, SortListOfTuples
from carbonui.util.stringManip import GetAsUnicode
from carbon.common.script.util.commonutils import StripTags
import blue
import telemetry
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.control.eveWindowUnderlay import RaisedUnderlay
from eve.client.script.ui.control.themeColored import LineThemeColored
import uiprimitives
import uthread
import sys
import _weakref
import log
import carbonui.const as uiconst
from carbonui.fontconst import DEFAULT_FONTSIZE, DEFAULT_LETTERSPACE, DEFAULT_UPPERCASE
import weakref
import localization
SCROLLMARGIN = 0
MINCOLUMNWIDTH = 24
VERSION = uiconst.SCROLLVERSION
TABMARGIN = 6

class ScrollCore(Container):
    __guid__ = 'uicontrols.ScrollCore'
    default_name = 'scroll'
    default_multiSelect = 1
    default_stickToBottom = 0
    default_smartSort = 0
    default_id = None
    default_state = uiconst.UI_NORMAL
    headerFontSize = 10
    scrollEnabled = True
    sortGroups = True
    dragHoverScrollSpeed = 1.0
    dragHoverScrollAreaSize = 30

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.sr.maincontainer = Container(parent=self, name='maincontainer', padding=(1, 1, 1, 1), clipChildren=True)
        self.sr.scrollHeaders = Container(name='scrollHeaders', parent=self.sr.maincontainer, height=18, state=uiconst.UI_HIDDEN, align=uiconst.TOTOP)
        self.sr.clipper = Container(name='__clipper', align=uiconst.TOALL, parent=self.sr.maincontainer, clipChildren=True)
        self.sr.clipper._OnSizeChange_NoBlock = self.OnClipperResize
        self.sr.content = Container(name='__content', align=uiconst.RELATIVE, parent=self.sr.clipper, state=uiconst.UI_NORMAL)
        self.Release()
        self.multiSelect = attributes.get('multiSelect', self.default_multiSelect)
        self.stickToBottom = attributes.get('stickToBottom', self.default_stickToBottom)
        self.smartSort = attributes.get('smartSort', self.default_smartSort)
        self.sr.id = attributes.get('id', self.default_id)
        self.loadingWheel = None
        self.sr.selfProxy = _weakref.proxy(self)
        self.Prepare_()
        self._mouseHoverCookie = uicore.uilib.RegisterForTriuiEvents(uiconst.UI_MOUSEHOVER, self.OnGlobalMouseHover)
        return

    def Close(self, *args):
        uicore.uilib.UnregisterForTriuiEvents(self._mouseHoverCookie)
        Container.Close(self, *args)

    def OnGlobalMouseHover(self, obj, *args):
        if uicore.IsDragging() and (obj == self or obj.IsUnder(self.sr.content)):
            l, t, w, h = self.GetAbsolute()
            if self.sr.scrollcontrols.display:
                y = uicore.uilib.y - t
                if y <= self.dragHoverScrollAreaSize:
                    self.Scroll(self.dragHoverScrollSpeed)
                    self.sr.scrollcontrols.AnimFade()
                elif y > h - self.dragHoverScrollAreaSize:
                    self.Scroll(-self.dragHoverScrollSpeed)
                    self.sr.scrollcontrols.AnimFade()
        return True

    def Prepare_(self):
        self.Prepare_Underlay_()
        self.Prepare_ScrollControls_()

    def Prepare_Underlay_(self):
        self.sr.underlay = Frame(name='__underlay', color=(0.0, 0.0, 0.0, 0.5), frameConst=uiconst.FRAME_FILLED_CORNER0, parent=self)

    def Prepare_ScrollControls_(self):
        self.sr.scrollcontrols = ScrollControlsCore(name='__scrollcontrols', parent=self.sr.maincontainer, align=uiconst.TORIGHT, width=12, state=uiconst.UI_HIDDEN, idx=0, clipChildren=True)
        self.sr.scrollcontrols.Startup(self)

    def RemoveActiveFrame(self, *args):
        pass

    def HideBackground(self, alwaysHidden=0):
        self.RemoveActiveFrame()
        if alwaysHidden:
            self.SetNoBackgroundFlag(alwaysHidden)

    HideUnderLay = HideBackground

    def SetNoBackgroundFlag(self, hide=0):
        self.hideBackground = hide

    def Release(self):
        self.isTabStop = 1
        self._loading = 0
        self._position = 0
        self._totalHeight = 0
        self._fixedEntryHeight = None
        self._customColumnWidths = None
        self.sr.scaleLine = None
        self.sr.headers = []
        self.sr.widthToHeaders = {}
        self.sr.tabs = []
        self.sr.nodes = []
        self.visibleNodes = []
        self.sr.overlays = []
        self.sr.underlays = []
        self.sr.fixedColumns = {}
        self.rightAlignHeaderLabels = []
        self.stretchLastHeader = False
        self.sr.maxDefaultColumns = {}
        self.sr.minColumnWidth = {}
        self.sr.defaultColumnWidth = {}
        self.sr.notSortableColumns = []
        self.sr.ignoreTabTrimming = 0
        self.showColumnLines = True
        self.sr.id = None
        self.sortBy = None
        self.sr.iconMargin = 0
        self.sr.hint = None
        self.scrollingRange = 0
        self.hiliteSorted = 1
        self.reversedSort = 0
        self.debug = 0
        self.scrolling = 0
        self.scalingcol = 0
        self.refreshingColumns = 0
        self.lastDrawnColumns = None
        self.allowFilterColumns = 0
        self.lastSelected = None
        self.lastHeaders = None
        self.bumpHeaders = 1
        self.slimHeaders = 0
        self.newColumns = 0
        self.trimFast = 0
        self.refs = []
        self.lastCharReceivedAt = 0
        self.currChars = ''
        self.hideBackground = False
        self._ignoreSort = 0
        return

    def GetVisibleNodes(self):
        if self.visibleNodes:
            return self.visibleNodes
        return self.sr.nodes

    def OnSetFocus(self, *args):
        if self and not self.destroyed and self.parent and self.parent.name == 'inlines':
            if self.parent.parent and self.parent.parent.sr.node:
                self.parent.parent.sr.node.scroll.ShowNodeIdx(self.parent.parent.sr.node.idx)
        self.sr.underlay.AnimEntry()

    def OnKillFocus(self, *args):
        self.sr.underlay.AnimExit()

    def DrawHeaders(self, headers, tabs=[]):
        self.sr.scrollHeaders.state = uiconst.UI_HIDDEN
        self.sr.scrollHeaders.Flush()
        for each in self.sr.clipper.children[:]:
            if each.name == '__columnLine':
                each.Close()

        self.lastDrawnColumns = None
        self.sr.widthToHeaders = {}
        if not (headers and tabs and len(headers) == len(tabs)):
            self.sr.headers = []
            self.sr.tabs = []
            return
        elif not self.sr.nodes:
            return
        else:
            self.sr.scrollHeaders.state = uiconst.UI_NORMAL
            self.sr.scrollHeaders.SetOrder(0)
            LineThemeColored(parent=self.sr.scrollHeaders, align=uiconst.TOBOTTOM, opacity=uiconst.OPACITY_FRAME)
            i = 0
            totalWidth = 0
            maxTextHeight = 0
            for header in headers:
                width = self.sr.fixedColumns.get(header, None)
                if width is None:
                    if len(headers) == 1:
                        width = 128
                    else:
                        width = tabs[i]
                        if i != 0:
                            width = width - tabs[i - 1]
                sortdir = self.GetSmartSortDirection(header)
                self.sr.widthToHeaders[header] = totalWidth
                from carbonui.control.scroll import ColumnHeaderCoreOverride as ScrollColumnHeader
                headerparent = ScrollColumnHeader(parent=self.sr.scrollHeaders, label=header)
                headerparent.SetAlign(uiconst.TOLEFT)
                headerparent.width = width
                headerparent.state = uiconst.UI_NORMAL
                headerparent.sr.column = header
                headerparent.sr.idx = i
                headerparent.sr.sortdir = sortdir
                headerparent.scroll = weakref.ref(self)
                headerparent.sr.header = header
                headerparent.name = header
                headerparent.haveBar = 0
                if headerparent.width - 12 <= headerparent.sr.label.textwidth:
                    headerparent.hint = header
                if self.stretchLastHeader and header == headers[-1]:
                    headerparent.SetAlign(uiconst.TOALL)
                    headerparent.width = 0
                elif header not in self.sr.fixedColumns and self.sr.id:
                    headerparent.width = width
                    headerparent.haveBar = 1
                    bar = uiprimitives.Container(parent=headerparent, align=uiconst.TORIGHT, pos=(-1, 0, 2, 0), state=uiconst.UI_NORMAL, idx=1)
                    bar.name = 'scaler'
                    bar.sr.column = header
                    bar.OnMouseDown = (self.StartScaleCol, bar)
                    bar.OnMouseUp = (self.EndScaleCol, bar)
                    bar.OnMouseMove = (self.ScalingCol, bar)
                    bar.OnDblClick = (self.DblClickCol, bar)
                    bar.cursor = 18
                    bar.columnWidth = width
                    headerparent.bar = bar
                if header in self.rightAlignHeaderLabels:
                    headerparent.sr.label.SetAlign(uiconst.CENTERRIGHT)
                totalWidth += width
                if self.smartSort:
                    if sortdir:
                        headerparent.ShowSortDirection(sortdir)
                if not (self.smartSort or self.allowFilterColumns):
                    headerparent.GetMenu = None
                maxTextHeight = max(maxTextHeight, headerparent.sr.label.textheight)
                if headerparent.align != uiconst.TOALL and not self.sr.ignoreTabTrimming and self.sr.nodes and self.showColumnLines:
                    line = LineThemeColored(parent=self.sr.clipper, align=uiconst.RELATIVE, name='__columnLine', opacity=uiconst.OPACITY_FRAME)
                    line.width = 1
                    line.height = uicore.desktop.height
                    line.top = 1
                    line.left = totalWidth - 1
                i += 1

            self.sr.scrollHeaders.height = maxTextHeight + 3
            self.lastDrawnColumns = headers
            return

    def ShowHint(self, hint=None):
        if self.sr.hint is None and hint:
            clipperWidth = self.GetContentWidth()
            self.sr.hint = LabelCore(parent=self.sr.clipper, align=uiconst.TOPLEFT, left=16, top=32, width=clipperWidth - 32, text=hint, fontsize=20, uppercase=True, letterspace=1)
        elif self.sr.hint is not None and hint:
            self.sr.hint.text = hint
            self.sr.hint.state = uiconst.UI_DISABLED
        elif self.sr.hint is not None and not hint:
            self.sr.hint.state = uiconst.UI_HIDDEN
        return

    def StartScaleCol(self, sender, *args):
        if uicore.uilib.rightbtn:
            return
        else:
            self.scalingcol = uicore.uilib.x
            if self.sr.scaleLine is not None:
                self.sr.scaleLine.Close()
            l, t, w, h = self.GetAbsolute()
            self.sr.scaleLine = LineThemeColored(parent=self, align=uiconst.TOPLEFT, width=2, pos=(uicore.uilib.x - l - 1,
             1,
             0,
             h), idx=0, opacity=uiconst.OPACITY_FRAME)
            return

    def ScalingCol(self, sender, *args):
        l, t, w, h = self.GetAbsolute()
        minColumnWidth = self.sr.minColumnWidth.get(sender.sr.column, MINCOLUMNWIDTH)
        if self.scalingcol and self.sr.scaleLine:
            self.sr.scaleLine.left = max(minColumnWidth, min(w - minColumnWidth, uicore.uilib.x - l - 2))

    def EndScaleCol(self, sender, *args):
        if self.sr.scaleLine is not None:
            if self.sr.id and self.scalingcol != uicore.uilib.x:
                currentSettings = settings.user.ui.Get('columnWidths_%s' % VERSION, {})
                currentSettings.setdefault(self.sr.id, {})
                currentWidth = sender.columnWidth
                minColumnWidth = self.sr.minColumnWidth.get(sender.sr.column, MINCOLUMNWIDTH)
                if self.sr.scaleLine:
                    l, t, w, h = self.GetAbsolute()
                    newLeft = self.sr.scaleLine.left + l
                else:
                    newLeft = uicore.uilib.x
                diff = newLeft - self.scalingcol
                newWidth = currentWidth + diff
                currentSettings[self.sr.id][sender.sr.column] = max(minColumnWidth, newWidth)
                settings.user.ui.Set('columnWidths_%s' % VERSION, currentSettings)
                uthread.pool('VirtualScroll::EndScaleCol-->UpdateTabStops', self.UpdateTabStops, 'EndScaleCol')
            scaleLine = self.sr.scaleLine
            self.sr.scaleLine = None
            scaleLine.Close()
        self.scalingcol = 0
        return

    def OnColumnChanged(self, *args):
        pass

    def OnNewHeaders(self, *args):
        pass

    def DblClickCol(self, sender, *args):
        self.ResetColumnWidth(sender.sr.column)

    def ShowNodeIdx(self, idx, toTop=1):
        if self.scrollingRange:
            node = self.GetNode(idx)
            fromTop = node.scroll_positionFromTop
            if fromTop is None:
                return
            if self._position > fromTop:
                portion = fromTop / float(self.scrollingRange)
                self.ScrollToProportion(portion)
            clipperWidth, clipperHeight = self.GetContentParentSize()
            nodeHeight = self.GetNodeHeight(node, clipperWidth)
            if self._position + clipperHeight < fromTop + nodeHeight:
                portion = (fromTop - clipperHeight + nodeHeight) / float(self.scrollingRange)
                self.ScrollToProportion(portion)
        return

    def GetNodes(self, allowNone=False):
        ret = []
        for each in self.sr.nodes:
            if each.internalNodes:
                if allowNone:
                    ret += each.internalNodes
                else:
                    for internal in each.internalNodes:
                        if internal:
                            ret.append(internal)

            else:
                ret.append(each)

        return ret

    def SetSelected(self, idx):
        node = self.GetNode(idx)
        if node:
            self.SelectNode(node)
        self.ReportSelectionChange()

    def ActivateIdx(self, idx):
        node = self.GetNode(min(idx, len(self.GetNodes()) - 1))
        if node:
            self.SelectNode(node)
            self.ShowNodeIdx(node.idx)
        else:
            self.ReportSelectionChange()

    def _SelectNode(self, node):
        if getattr(node, 'selectable', 1) == 0:
            return
        node.selected = 1
        self.UpdateSelection(node)

    def _DeselectNode(self, node):
        node.selected = 0
        self.UpdateSelection(node)

    def SelectNodes(self, nodeList):
        self.DeselectAll()
        for node in nodeList:
            self._SelectNode(node)

        self.ReportSelectionChange()

    def SelectNode(self, node, multi=0, subnode=None, checktoggle=1):
        control = uicore.uilib.Key(uiconst.VK_CONTROL)
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        selected = node.get('selected', 0)
        if not self.multiSelect:
            self.DeselectAll(0)
            if control:
                if not selected:
                    self._SelectNode(node)
            else:
                self._SelectNode(node)
        elif not control and not shift:
            self.DeselectAll(0)
            self._SelectNode(node)
        elif control and not shift:
            if not selected:
                self._SelectNode(node)
            else:
                self._DeselectNode(node)
        elif not control and shift:
            if self.lastSelected is not None and self.lastSelected != node.idx:
                self.DeselectAll(0)
                r = [self.lastSelected, node.idx]
                r.sort()
                for i in xrange(r[0], r[1] + 1):
                    _node = self.GetNode(i, checkInternalNodes=True)
                    if _node:
                        self._SelectNode(_node)

                self.ReportSelectionChange()
                return
            self.DeselectAll(0)
            self._SelectNode(node)
        elif control and shift:
            if self.lastSelected is not None and self.lastSelected != node.idx:
                r = [self.lastSelected, node.idx]
                r.sort()
                for i in xrange(r[0], r[1] + 1):
                    _node = self.GetNode(i, checkInternalNodes=True)
                    if _node:
                        self._SelectNode(_node)

        else:
            self.DeselectAll(0)
            self._SelectNode(node)
        self.lastSelected = node.idx
        self.ReportSelectionChange()
        return

    def ReportSelectionChange(self):
        self.OnSelectionChange(self.GetSelected())

    def OnSelectionChange(self, *args):
        pass

    def DeselectAll(self, report=1, *args):
        for node in self.GetNodes():
            node.selected = 0
            self.UpdateSelection(node)

        if report:
            self.ReportSelectionChange()

    def SelectAll(self, *args):
        if not self.multiSelect:
            return
        for node in self.GetNodes():
            if getattr(node, 'selectable', 1) == 0:
                continue
            node.selected = 1
            self.UpdateSelection(node)

        self.ReportSelectionChange()

    def ToggleSelected(self, *args):
        for node in self.GetNodes():
            node.selected = not node.get('selected', 0)
            self.UpdateSelection(node)

        self.ReportSelectionChange()

    def UpdateSelection(self, node):
        if node.panel:
            if node.panel.sr.selection:
                node.panel.sr.selection.state = [uiconst.UI_HIDDEN, uiconst.UI_DISABLED][node.selected]
            elif node.selected and hasattr(node.panel, 'Select'):
                node.panel.Select()
            elif not node.selected and hasattr(node.panel, 'Deselect'):
                node.panel.Deselect()

    def ClearSelection(self, *args):
        for node in self.GetNodes():
            node.selected = 0
            self.UpdateSelection(node)

        self.lastSelected = None
        self.ReportSelectionChange()
        return

    def GetSelectedNodes(self, node, toggle=0):
        if not node.get('selected', 0) or toggle:
            self.SelectNode(node)
        sel = []
        for each in self.GetNodes():
            if each.get('selected', 0):
                sel.append(each)

        return sel

    def GetSelected(self):
        sel = []
        for each in self.GetNodes():
            if each.get('selected', 0):
                sel.append(each)

        return sel

    def GetSortBy(self):
        if self.smartSort:
            return None
        else:
            if self.sr.id:
                pr = settings.user.ui.Get('scrollsortby_%s' % VERSION, {})
                if self.sr.id in pr:
                    return pr[self.sr.id][0]
            return self.sortBy

    def GetSortDirection(self):
        if self.sr.id:
            pr = settings.user.ui.Get('scrollsortby_%s' % VERSION, {})
            if self.sr.id in pr:
                return pr[self.sr.id][1]
        return self.reversedSort

    def GetSmartSortDirection(self, column):
        if self.sr.id and self.smartSort:
            if column not in self.sr.notSortableColumns:
                pr = settings.user.ui.Get('smartSortDirection_%s' % VERSION, {})
                if self.sr.id in pr:
                    return pr[self.sr.id].get(column, 1)
            else:
                return None
        return 1

    def ToggleSmartSortDirection(self, column):
        if self.sr.id and self.smartSort:
            current = self.GetSmartSortDirection(column)
            new = [1, -1][current == 1]
            pr = settings.user.ui.Get('smartSortDirection_%s' % VERSION, {})
            if self.sr.id not in pr:
                pr[self.sr.id] = {}
            pr[self.sr.id][column] = new
            settings.user.ui.Set('smartSortDirection_%s' % VERSION, pr)

    def GetSortValue(self, by, node, idx=None):
        if getattr(node, 'sortValues', None):
            return node.sortValues[idx]
        elif getattr(node, 'GetSortValue', None):
            return node.GetSortValue(node, by, self.GetSortDirection(), idx=idx)
        else:
            ret = self._GetSortValue(by, node, idx)
            ret = StripTags(ret, stripOnly=['localized'])
            Deco = node.get('DecoSortValue', lambda x: x)
            return Deco(ret)

    def _GetSortValue(self, by, node, idx):
        val = node.Get('sort_' + by, None)
        if val is None:
            val = node.Get('sort_' + by.replace('<br>', ' '), None)
        if val is not None:
            try:
                val = val.lower()
            except:
                sys.exc_clear()

            return val
        elif idx is not None:
            strings = self.GetStringFromNode(node).split('<t>')
            if len(strings) > idx:
                value = strings[idx].lower()
                try:
                    value = uicore.font.DeTag(value)
                    isAU = value.find('au') != -1
                    isKM = value.find('km') != -1
                    value = float(value.replace('m\xb3', '').replace('isk', '').replace('km', '').replace('au', '').replace(',', '').replace(' ', ''))
                    if isAU:
                        value *= const.AU
                    elif isKM:
                        value *= 1000
                    return value
                except:
                    sys.exc_clear()
                    rest = ''.join(strings[idx + 1:])
                    return value + rest

            return 'aaa'
        else:
            val = node.Get(by, '-')
            try:
                val = val.lower()
            except:
                sys.exc_clear()

            return val

    def GetContentContainer(self):
        return self.sr.content

    def GetColumns(self):
        if self.sr.id and (self.smartSort or self.allowFilterColumns):
            if not self.sr.headers:
                return []
            orderedColumns = settings.user.ui.Get('columnOrder_%s' % VERSION, {}).get(self.sr.id, self.sr.headers)
            notInOrdered = [ header for header in self.sr.headers if header not in orderedColumns ]
            headers = [ header for header in orderedColumns + notInOrdered if header in self.sr.headers ]
            hiddenColumns = settings.user.ui.Get('filteredColumns_%s' % VERSION, {}).get(self.sr.id, [])
            allHiddenColumns = hiddenColumns + settings.user.ui.Get('filteredColumnsByDefault_%s' % VERSION, {}).get((self.sr.id, session.languageID), [])
            filterColumns = filter(lambda x: x not in allHiddenColumns, headers)
            return filterColumns
        else:
            return self.sr.headers

    def GetHeaderMenu(self, label):
        m = []
        if self.smartSort:
            m += [(MenuLabel('/Carbon/UI/Commands/CmdMakePrimary'), self.MakePrimary, (label,))]
        if self.smartSort or self.allowFilterColumns:
            if len(self.GetColumns()) > 1:
                m += [(MenuLabel('/Carbon/UI/Common/Hide', {'label': label}), self.HideColumn, (label,))]
            m += self.GetShowColumnMenu()
        return m

    def GetShowColumnMenu(self):
        m = []
        for label in self.sr.headers:
            if label not in self.GetColumns():
                m.append((MenuLabel('/Carbon/UI/Common/Show', {'label': label}), self.ShowColumn, (label,)))

        if m:
            m.insert(0, None)
        return m

    def MakePrimary(self, label, update=1):
        all = settings.user.ui.Get('primaryColumn_%s' % VERSION, {})
        all[self.sr.id] = label
        settings.user.ui.Set('primaryColumn_%s' % VERSION, all)
        if update:
            self.ChangeColumnOrder(label, 0)

    def GetPrimaryColumn(self):
        return settings.user.ui.Get('primaryColumn_%s' % VERSION, {}).get(self.sr.id, None)

    def SetColumnsHiddenByDefault(self, columns, *args):
        if self.sr.id:
            filteredByDefault = settings.user.ui.Get('filteredColumnsByDefault_%s' % VERSION, {})
            idWithLanguage = (self.sr.id, session.languageID)
            if idWithLanguage not in filteredByDefault:
                filteredByDefault[idWithLanguage] = columns
                settings.user.ui.Set('filteredColumnsByDefault_%s' % VERSION, filteredByDefault)

    def HideColumn(self, label):
        if self.sr.id:
            filtered = settings.user.ui.Get('filteredColumns_%s' % VERSION, {})
            if self.sr.id not in filtered:
                filtered[self.sr.id] = []
            if label not in filtered[self.sr.id]:
                filtered[self.sr.id].append(label)
            settings.user.ui.Set('filteredColumns_%s' % VERSION, filtered)
            self.OnColumnChanged(None)
            self.OnNewHeaders()
        return

    def ShowColumn(self, label):
        if self.sr.id:
            filtered = settings.user.ui.Get('filteredColumns_%s' % VERSION, {})
            if self.sr.id in filtered and label in filtered[self.sr.id]:
                filtered[self.sr.id].remove(label)
            filteredByDefault = settings.user.ui.Get('filteredColumnsByDefault_%s' % VERSION, {})
            idWithLanguage = (self.sr.id, session.languageID)
            if idWithLanguage in filteredByDefault and label in filteredByDefault[idWithLanguage]:
                filteredByDefault[idWithLanguage].remove(label)
                settings.user.ui.Set('filteredColumnsByDefault_%s' % VERSION, filteredByDefault)
            settings.user.ui.Set('filteredColumns_%s' % VERSION, filtered)
            self.OnColumnChanged(None)
            self.OnNewHeaders()
        return

    def HideTriangle(self, column):
        for each in self.sr.scrollHeaders.children:
            if not isinstance(each, ColumnHeaderCore):
                continue
            if each.name == column and each.sr.triangle:
                each.sr.triangle.state = uiconst.UI_HIDDEN
                if each.sr.label.align == uiconst.CENTERRIGHT:
                    each.sr.label.left = 0

    def Sort(self, by=None, reversesort=0, forceHilite=0):
        if self.debug:
            log.LogInfo('vscroll', 'Sort' + strx(by) + ', ' + strx(reversesort))
        if self.smartSort:
            columns = self.GetColumns()
            primary = self.GetPrimaryColumn()
            sortcolumns = columns[:]
            if primary in columns:
                idx = columns.index(primary)
                sortcolumns = columns[idx:]
            if columns:
                sortData = []
                rm = []
                for node in self.sr.nodes:
                    nodeData = []
                    idx = 0
                    for header in columns:
                        if header not in sortcolumns:
                            self.HideTriangle(header)
                            continue
                        if idx in rm:
                            value = 0
                        else:
                            value = node.Get('sort_%s' % header, None)
                            if value is None:
                                log.LogWarn('Cannot find sortvalue for column ', header, ' in scroll ', self.sr.id)
                                rm.append(idx)
                                self.HideTriangle(header)
                                value = 0
                            else:
                                try:
                                    value = value.lower()
                                except:
                                    sys.exc_clear()

                        idx += 1
                        nodeData.append(value)

                    sortData.append([nodeData, node])

                sortOrder = [ (idx, self.GetSmartSortDirection(header)) for idx, header in enumerate(sortcolumns) if idx not in rm ]
                sortData.sort(lambda x, y, sortOrder=sortOrder: SmartCompare(x, y, sortOrder))
                self.SetNodes([ each[1] for each in sortData ])
                self.UpdatePositionThreaded(fromWhere='Sort(Smart)')
        else:
            idx = None
            headers = self.GetColumns()
            if by in headers:
                idx = headers.index(by)
            endOrder = []
            self.SortAsRoot(self.sr.nodes, endOrder, by, idx, reversesort)
            self.SetNodes(endOrder)
            self.UpdatePosition(fromWhere='Sort')
            if self.sortBy != by or forceHilite:
                self.HiliteSorted(by, reversesort)
                self.sortBy = by
        return

    def SortAsRoot(self, nodes, endOrder, columnName, columnIndex, reversedSorting=0, groupIndex=None):
        groups = []
        rootSortList_Groups = []
        rootSortList_NotGroups = []
        for node in nodes:
            if groupIndex is None and node.isSub:
                continue
            val = self.GetSortValue(columnName, node, columnIndex)
            val = (val, self.GetStringFromNode(node).lower())
            if issubclass(node.decoClass, SE_ListGroupCore):
                rootSortList_Groups.append((val, node))
            else:
                rootSortList_NotGroups.append((val, node))

        if self.sortGroups:
            rootSortList_Groups = SortListOfTuples(rootSortList_Groups)
        else:
            rootSortList_Groups = [ node for val, node in rootSortList_Groups ]
        rootSortList_NotGroups = SortListOfTuples(rootSortList_NotGroups)
        if reversedSorting:
            rootSortList_NotGroups.reverse()
        combinedGroupsAndOthers = rootSortList_Groups + rootSortList_NotGroups
        if groupIndex is not None:
            for subIndex, subNode in enumerate(combinedGroupsAndOthers):
                endOrder.insert(groupIndex + subIndex + 1, subNode)

        else:
            endOrder.extend(combinedGroupsAndOthers)
        if rootSortList_Groups:
            for groupNode in rootSortList_Groups:
                groupIdx = endOrder.index(groupNode)
                subNodes = groupNode.get('subNodes', [])
                self.SortAsRoot(subNodes, endOrder, columnName, columnIndex, reversedSorting, groupIndex=groupIdx)

        return nodes

    def GetStringFromNode(self, node):
        label_or_text = node.get('label', '') or node.get('text', '')
        return GetAsUnicode(label_or_text)

    def RefreshSort(self, forceHilite=0):
        if self.debug:
            log.LogInfo('vscroll', 'RefreshSort')
        if self.smartSort:
            self.Sort()
        else:
            sortby = self.GetSortBy()
            if sortby:
                self.Sort(sortby, self.GetSortDirection(), forceHilite=forceHilite)

    def ChangeSortBy(self, by, *args):
        if self.debug:
            log.LogInfo('vscroll', 'ChangeSortBy')
        if self.smartSort:
            self.MakePrimary(by, 0)
            self.ToggleSmartSortDirection(by)
            for header in self.sr.scrollHeaders.children:
                if not isinstance(header, ColumnHeaderCore):
                    continue
                sortdir = self.GetSmartSortDirection(header.sr.column)
                header.sr.sortdir = sortdir
                header.ShowSortDirection(sortdir)

            self.Sort()
        else:
            if self.sortBy == by:
                self.reversedSort = not self.reversedSort
            else:
                self.reversedSort = 0
            self.sortBy = by
            if self.sr.id:
                pr = settings.user.ui.Get('scrollsortby_%s' % VERSION, {})
                pr[self.sr.id] = (self.sortBy, self.reversedSort)
                settings.user.ui.Set('scrollsortby_%s' % VERSION, pr)
            self.RefreshSort(1)

    def ChangeColumnOrder(self, column, toIdx):
        if self.debug:
            log.LogInfo('vscroll', 'ChangeColumnOrder')
        if self.sr.id and self.smartSort:
            all = settings.user.ui.Get('columnOrder_%s' % VERSION, {})
            currentOrder = all.get(self.sr.id, self.sr.headers)[:]
            if column in currentOrder:
                currentOrder.remove(column)
            currentOrder.insert(toIdx, column)
            all[self.sr.id] = currentOrder
            settings.user.ui.Set('columnOrder_%s' % VERSION, all)
            self.OnColumnChanged(None)
            self.OnNewHeaders()
        return

    def HiliteSorted(self, by, rev, *args):
        if self.debug:
            log.LogInfo('vscroll', 'HiliteSorted')
        totalWidth = 0
        for header in self.sr.scrollHeaders.children:
            if not isinstance(header, ColumnHeaderCore):
                continue
            header.Deselect()
            if self.hiliteSorted and header.sr.column == by:
                header.Select(rev)
            totalWidth += header.width

    def Clear(self):
        if self.debug:
            log.LogInfo('vscroll', 'Clear')
        self.visibleNodes = []
        self.LoadContent()

    def ReloadNodes(self):
        for node in self.GetNodes():
            self.PrepareSubContent(node, threadedUpdate=False)
            if node.panel:
                node.panel.Load(node)

    def LoadContent(self, fixedEntryHeight=None, contentList=[], sortby=None, reversesort=0, headers=[], scrollTo=None, customColumnWidths=False, showScrollTop=False, noContentHint='', ignoreSort=False, scrolltotop=False, keepPosition=False):
        if self.destroyed:
            return
        else:
            if scrolltotop:
                scrollTo = 0.0
            elif scrollTo is None or keepPosition:
                scrollTo = self.GetScrollProportion()
            self._loading = 1
            self._fixedEntryHeight = fixedEntryHeight
            self._customColumnWidths = customColumnWidths
            self._ignoreSort = ignoreSort
            wnd = GetWindowAbove(self)
            if wnd and not wnd.destroyed and hasattr(wnd, 'ShowLoad'):
                wnd.ShowLoad()
            if self.debug:
                log.LogInfo('vscroll', 'Load %s %s %s %s' % (len(contentList),
                 sortby,
                 reversesort,
                 headers))
            self.sr.nodes = self.sr.entries = []
            self.sr.content.Flush()
            self._position = self.sr.content.top = 0
            if showScrollTop:
                self.sr.scrollcontrols.state = uiconst.UI_NORMAL
            self.sortBy = sortby
            self.reversedSort = reversesort
            self.AddNodes(0, contentList, initing=True)
            if sortby and not ignoreSort:
                self.Sort(sortby, reversesort)
            if self.destroyed:
                return
            if noContentHint and not contentList:
                self.ShowHint(noContentHint)
                self.__LoadHeaders([])
            else:
                self.ShowHint()
                self.__LoadHeaders(headers)
            if self.destroyed:
                return
            self.RefreshNodes(fromWhere='LoadContent')
            self.ScrollToProportion(scrollTo, threaded=False)
            self.UpdateTabStops('LoadContent')
            if wnd and not wnd.destroyed and hasattr(wnd, 'HideLoad'):
                wnd.HideLoad()
            self._loading = 0
            return

    Load = LoadContent

    def LoadHeaders(self, headers):
        wnd = GetWindowAbove(self)
        try:
            if self.__LoadHeaders(headers):
                self.OnColumnChanged(self.sr.tabs)
        finally:
            if wnd and not wnd.destroyed and hasattr(wnd, 'HideLoad'):
                wnd.HideLoad()

    def __LoadHeaders(self, headers):
        self.sr.headers = headers
        self.UpdateTabStops('__LoadHeaders')
        if self.destroyed:
            return
        if headers:
            if not self.smartSort:
                sortby = self.GetSortBy()
                reversesort = self.GetSortDirection()
                if not sortby or sortby not in headers:
                    sortby = headers[0]
                if not self._ignoreSort:
                    self.Sort(sortby, reversesort)
                else:
                    self.UpdatePositionThreaded(fromWhere='__LoadHeaders')
            else:
                self.Sort()
        if len(self.sr.nodes) or not headers:
            self.lastHeaders = headers

    def ResetColumnWidths(self):
        for header in self.GetColumns():
            self.ResetColumnWidth(header)

    def ResetColumnWidth(self, header, onlyReset=0):
        if self.debug:
            log.LogInfo('vscroll', 'ResetColumnWidth')
        if self.sr.id is None or self.refreshingColumns:
            return
        else:
            if not onlyReset:
                wnd = GetWindowAbove(self)
                if wnd and not wnd.destroyed and hasattr(wnd, 'ShowLoad'):
                    wnd.ShowLoad()
            self.refreshingColumns = 1
            if header not in self.sr.fixedColumns and self.sr.id:
                headertab = [(header,
                  self.headerFontSize,
                  2,
                  TABMARGIN + 8 + 20,
                  1)]
            else:
                headertab = [(header,
                  self.headerFontSize,
                  2,
                  0,
                  1)]
            if header in self.GetColumns():
                idx = self.GetColumns().index(header)
                width = None
                if self._customColumnWidths:
                    headerWidth = uicore.font.GetTextWidth(header, fontsize=self.headerFontSize, letterspace=0, uppercase=True)
                    headerWidth += TABMARGIN + 8 + 20
                    normHeader = header.replace('<br>', ' ')
                    width = max([headerWidth] + [ node.GetColumnWidthFunction(None, node, normHeader) for node in self.sr.nodes if node.get('GetColumnWidthFunction', None) is not None ])
                else:
                    tabstops = self.GetTabStops(headertab, idx)
                    if len(tabstops):
                        width = max(MINCOLUMNWIDTH, tabstops[0])
                if width is not None:
                    current = settings.user.ui.Get('columnWidths_%s' % VERSION, {})
                    current.setdefault(self.sr.id, {})[header] = width
                    settings.user.ui.Set('columnWidths_%s' % VERSION, current)
                    self.UpdateTabStops('ResetColumnWidth')
            if not onlyReset and wnd and not wnd.destroyed and hasattr(wnd, 'HideLoad'):
                wnd.HideLoad()
            self.refreshingColumns = 0
            return

    @telemetry.ZONE_METHOD
    def ApplyTabstopsToNode(self, node, fromWhere=''):
        if self.sr.ignoreTabTrimming or not self.GetColumns():
            return
        else:
            tabStops = self.sr.tabs
            node.tabs = tabStops
            if tabStops and GetAttrs(node, 'panel', 'OnColumnResize'):
                cols = []
                last = 0
                for tab in tabStops:
                    cols.append(tab - last)
                    last = tab

                cols[0] -= self.sr.maincontainer.left
                node.panel.OnColumnResize(cols)
            elif tabStops and node.panel and node.panel.sr.label:
                label = node.panel.sr.label
                subTract = label.left
                if isinstance(label, LabelCore):
                    newtext = self.GetStringFromNode(node)
                    if newtext and (getattr(label, 'tabs', None) != tabStops or getattr(label, 'xShift', 0) != -subTract) and newtext.find('<t>') != -1:
                        label.xShift = -subTract
                        label.tabs = tabStops
                        label.text = newtext
                        label.Update()
            return

    def GetTabStops(self, headertabs, idx=None):
        strengir = []
        fontsize = 12
        letterspace = 0
        shift = 0
        for node in self.sr.nodes:
            s = self.GetStrengir(node, fontsize, letterspace, shift, idx)
            if s is None:
                continue
            strengir.append(s)

        tabstops = uicore.font.MeasureTabstops(strengir + headertabs)
        return tabstops

    def GetStrengir(self, node, fontsize, letterspace, shift, idx=None):
        t = self.GetStringFromNode(node)
        if not t or t.find('<t>') == -1:
            return
        else:
            if idx is not None:
                t = t.split('<t>')
                if len(t) <= idx:
                    return
                t = t[idx]
            if node.panel and node.panel.sr.label:
                label = node.panel.sr.label
                fontsize = label.fontsize
                letterspace = label.letterspace
                shift = label.left
            return (t,
             fontsize,
             letterspace,
             shift,
             0)

    @telemetry.ZONE_METHOD
    def UpdateTabStops(self, fromWhere=None, updatePosition=True):
        headers = self.GetColumns()
        if self.debug:
            log.LogInfo('vscroll', 'UpdateTabStops %s %s' % (headers, fromWhere))
        headertabs = []
        if headers is not None and len(headers):
            headertabs = [('<t>'.join(headers),
              self.headerFontSize,
              2,
              TABMARGIN + 2,
              1)]
        tabstops = self.GetTabStops(headertabs)
        if self.sr.id and headers:
            userDefined = settings.user.ui.Get('columnWidths_%s' % VERSION, {}).get(self.sr.id, {})
            i = 0
            total = 0
            former = 0
            for header in headers:
                if header in self.sr.fixedColumns:
                    stopSize = self.sr.fixedColumns[header]
                else:
                    userSetWidth = userDefined.get(header, None) or self.sr.defaultColumnWidth.get(header, None)
                    minColumnWidth = self.sr.minColumnWidth.get(header, MINCOLUMNWIDTH)
                    if userSetWidth is not None:
                        stopSize = max(userSetWidth, minColumnWidth)
                    else:
                        stopSize = tabstops[i] - former
                        if header in self.sr.maxDefaultColumns:
                            stopSize = min(self.sr.maxDefaultColumns.get(header, minColumnWidth), stopSize)
                total += stopSize
                former = tabstops[i]
                tabstops[i] = total
                i += 1

        didChange = tabstops != self.sr.tabs
        self.sr.tabs = tabstops
        if headers != self.lastDrawnColumns or didChange:
            self.DrawHeaders(headers, tabstops)
            if didChange:
                if not self.smartSort:
                    self.HiliteSorted(self.GetSortBy(), self.GetSortDirection(), 'UpdateTabStops')
                if not self._loading:
                    self.OnColumnChanged(tabstops)
        if updatePosition:
            self.UpdatePositionThreaded('UpdateTabStops')
        return tabstops

    @telemetry.ZONE_METHOD
    def AddNode(self, idx, node, isSub=0, initing=False):
        if self.debug:
            log.LogInfo('vscroll', 'AddNode', idx)
        if idx == -1:
            idx = len(self.sr.nodes)
        node.panel = None
        node.open = 0
        node.idx = idx
        node.isSub = isSub
        node.scroll = self.sr.selfProxy
        node.selected = node.get('isSelected', 0)
        if node.get('PreLoadFunction', None):
            node.PreLoadFunction(node)
            if self.destroyed:
                return
        self.sr.nodes.insert(idx, node)
        self.PrepareSubContent(node, initing=initing)
        return node

    @telemetry.ZONE_METHOD
    def PrepareSubContent(self, node, initing=False, threadedUpdate=True):
        if node.id:
            if node.get('subNodes', []):
                rm = node.subNodes
                node.subNodes = []
                node.open = 0
                self.RemoveNodes(rm)
            if node.Get('GetSubContent', None) is not None:
                forceOpen = node.get('forceOpen', False) and initing
                if forceOpen or uicore.registry.GetListGroupOpenState(node.id, default=node.get('openByDefault', False)):
                    subcontent = node.GetSubContent(node)
                    if self.destroyed or node not in self.GetNodes():
                        return
                    if not node.Get('hideNoItem', False) and not len(subcontent):
                        noItemText = node.get('noItemText', localization.GetByLabel('/Carbon/UI/Controls/Common/NoItem'))
                        subcontent.append(self.GetNoItemNode(text=noItemText, sublevel=node.get('sublevel', 0) + 1))
                    if not self.destroyed:
                        self.AddNodes(node.idx + 1, subcontent, node, initing=initing, threadedUpdate=threadedUpdate)
                        if node not in self.GetNodes():
                            self.RemoveNodes(subcontent)
                        else:
                            node.subNodes = subcontent
                            node.open = 1
                            return subcontent
        return

    def SetNodes(self, nodes):
        self.sr.nodes = nodes
        self.RefreshNodes()

    @telemetry.ZONE_METHOD
    def RefreshNodes(self, fromWhere=None):
        if self.destroyed:
            return
        clipperWidth, clipperHeight = self.sr.clipper.GetCurrentAbsoluteSize()
        if not clipperWidth or not clipperHeight:
            clipperWidth, clipperHeight = self.sr.clipper.GetAbsoluteSize()
        fromTop = 0
        for nodeidx, node in enumerate(self.sr.nodes):
            node.idx = nodeidx
            nodeheight = self.GetNodeHeight(node, clipperWidth)
            node.scroll_positionFromTop = fromTop
            if node.panel:
                node.panel.align = uiconst.TOPLEFT
                node.panel.left = 0
                node.panel.top = fromTop
                node.panel.width = clipperWidth
                node.panel.height = nodeheight
                node.panel.name = node.name or 'entry_%s' % node.idx
            fromTop += nodeheight

        for overlay, attrs, x, y in self.sr.overlays + self.sr.underlays:
            fromTop = max(fromTop, attrs.top + attrs.height)

        atBottom = self._position and self._position == self.scrollingRange
        self._totalHeight = fromTop
        self.scrollingRange = max(0, self._totalHeight - clipperHeight)
        if self.scrollingRange and self.scrollEnabled:
            self.sr.scrollcontrols.state = uiconst.UI_NORMAL
        else:
            self.sr.scrollcontrols.state = uiconst.UI_HIDDEN
        if self.scrollEnabled:
            if not self.scrollingRange or atBottom or self.stickToBottom:
                self._position = self.scrollingRange
            self._position = min(self._position, self.scrollingRange)
        else:
            self._position = 0
        self.UpdateContentSize(clipperWidth, clipperHeight, self._totalHeight)
        if self.sr.overlays_content:
            self.sr.overlays_content.height = self.sr.content.height
            self.sr.overlays_content.width = clipperWidth
        if self.sr.underlays_content:
            self.sr.underlays_content.height = self.sr.content.height
            self.sr.underlays_content.width = clipperWidth

    @telemetry.ZONE_METHOD
    def UpdateContentSize(self, clipperWidth, clipperHeight, contentHeight):
        self.sr.content.height = max(clipperHeight, contentHeight)
        self.sr.content.width = clipperWidth

    @telemetry.ZONE_METHOD
    def AddNodes(self, fromIdx, nodesData, parentNode=None, ignoreSort=0, initing=False, threadedUpdate=True):
        if self.debug:
            log.LogInfo('vscroll', 'AddNodes start')
        wnd = GetWindowAbove(self)
        if wnd and not wnd.destroyed and hasattr(wnd, 'ShowLoad'):
            wnd.ShowLoad()
        if fromIdx == -1:
            fromIdx = len(self.sr.nodes)
        isSub = 0
        if parentNode:
            isSub = parentNode.get('sublevel', 0) + 1
        nodes = []
        idx = fromIdx
        for data in nodesData:
            newnode = self.AddNode(idx, data, isSub=isSub, initing=initing)
            if newnode is None:
                continue
            subs = self.CollectSubNodes(newnode, clear=0)
            idx = newnode.idx + 1 + len(subs)
            nodes.append(newnode)

        if parentNode:
            parentNode.subNodes = nodes
        if not initing:
            if self.GetSortBy() and not (self._ignoreSort or ignoreSort):
                self.RefreshSort()
            elif threadedUpdate:
                self.RefreshNodes()
                self.UpdatePositionThreaded(fromWhere='AddNodes')
            else:
                self.RefreshNodes()
                self.UpdatePosition(fromWhere='AddNodes')
            if nodes:
                self.UpdateTabStops('AddNodes', updatePosition=True)
        if wnd and not wnd.destroyed and hasattr(wnd, 'HideLoad'):
            wnd.HideLoad()
        if self.debug:
            log.LogInfo('vscroll', 'AddNodes done')
        return nodes

    AddEntries = AddNodes

    @telemetry.ZONE_METHOD
    def RemoveNodes(self, nodes):
        if self.debug:
            log.LogInfo('vscroll', 'RemoveNodes start')
        wnd = GetWindowAbove(self)
        if wnd and not wnd.destroyed and hasattr(wnd, 'ShowLoad'):
            wnd.ShowLoad()
        subs = []
        for node in nodes:
            subs.extend(self.CollectSubNodes(node))

        for nodeList in (nodes, subs):
            for node in nodeList:
                if node.panel:
                    node.panel.Close()
                if node in self.sr.nodes:
                    self.sr.nodes.remove(node)

        self.RefreshNodes()
        self.UpdatePosition()
        if wnd and not wnd.destroyed and hasattr(wnd, 'HideLoad'):
            wnd.HideLoad()
        if self.debug:
            log.LogInfo('vscroll', 'RemoveNodes done')

    RemoveEntries = RemoveNodes

    def CollectSubNodes(self, node, nodes=None, clear=1):
        if nodes is None:
            nodes = []
        inNodes = [ id(each) for each in nodes ]
        for subnode in node.get('subNodes', []):
            if subnode is None:
                continue
            self.CollectSubNodes(subnode, nodes, clear)
            if id(subnode) not in inNodes:
                nodes.append(subnode)

        if clear:
            node.subNodes = []
        return nodes

    @telemetry.ZONE_METHOD
    def GetNodeHeight(self, node, clipperWidth):
        func = node.GetHeightFunction
        newStyle = getattr(node.decoClass, 'GetDynamicHeight', None)
        if func:
            allowDynamicResize = node.get('allowDynamicResize', True)
            if not node.height or allowDynamicResize and node._lastClipperWidth != clipperWidth:
                node.height = apply(func, (None, node, clipperWidth))
                node._lastClipperWidth = clipperWidth
        elif newStyle:
            if not node.height or node._lastClipperWidth != clipperWidth:
                node.height = newStyle(node, clipperWidth)
                node._lastClipperWidth = clipperWidth
        elif self._fixedEntryHeight:
            node.height = self._fixedEntryHeight
        else:
            node.height = getattr(node.decoClass, 'ENTRYHEIGHT', 18)
        if not node.height:
            if func:
                apply(func, (None, node, clipperWidth))
            else:
                node.height = getattr(node.decoClass, 'ENTRYHEIGHT', 18)
        return node.height

    @telemetry.ZONE_METHOD
    def GetContentWidth(self):
        w, h = self.GetContentParentSize()
        return w

    @telemetry.ZONE_METHOD
    def GetContentHeight(self):
        return self._totalHeight

    GetTotalHeight = GetContentHeight

    def GetContentParentSize(self):
        w, h = self.sr.clipper.GetAbsoluteSize()
        return (w, h)

    def UpdatePositionThreaded(self, fromWhere=None):
        loopThread = getattr(self, 'loopThread', None)
        if loopThread is None:
            self.loopThread = uthread.new(self.UpdatePositionLoop)
        return

    @telemetry.ZONE_METHOD
    def UpdatePositionLoop(self, fromWhere=None):
        if self.destroyed:
            return
        else:
            while True:
                nodeCreatedOrRefreshed = self.UpdatePosition(fromWhere='UpdatePositionLoop', doYield=True)
                blue.pyos.BeNice()
                if self.destroyed:
                    return
                if not nodeCreatedOrRefreshed:
                    break

            self.loopThread = None
            return

    @telemetry.ZONE_METHOD
    def UpdatePosition(self, fromWhere=None, doYield=False):
        if self.destroyed:
            return
        else:
            clipperWidth, clipperHeight = self.sr.clipper.GetAbsoluteSize()
            self.sr.content.top = int(-self._position)
            if self.sr.overlays_content:
                self.sr.overlays_content.top = self.sr.content.top
            if self.sr.underlays_content:
                self.sr.underlays_content.top = self.sr.content.top
            self.UpdateScrollHandle(clipperHeight, fromWhere='UpdatePosition')
            tabStops = self.sr.tabs
            scrollPosition = self._position
            ignoreTabstops = self.sr.ignoreTabTrimming or not self.GetColumns()
            nodeLoaded = False
            self.visibleNodes = []
            for nodeCount, node in enumerate(self.sr.nodes):
                if nodeCount != node.idx or node.scroll_positionFromTop is None or node.height is None:
                    self.RefreshNodes(fromWhere='UpdatePosition')
                nodeheight = node.height
                posFromTop = node.scroll_positionFromTop
                displayScrollEntry = node.panel
                if scrollPosition > posFromTop + nodeheight or scrollPosition + clipperHeight < posFromTop:
                    if displayScrollEntry:
                        displayScrollEntry.state = uiconst.UI_HIDDEN
                    if doYield:
                        blue.pyos.BeNice()
                    continue
                forceTabstops = False
                if not displayScrollEntry:
                    decoClass = node.decoClass
                    displayScrollEntry = decoClass(parent=self.sr.content, align=uiconst.TOPLEFT, pos=(0,
                     posFromTop,
                     clipperWidth,
                     nodeheight), state=uiconst.UI_NORMAL, name=node.name or 'entry_%s' % node.idx, node=node)
                    displayScrollEntry.sr.node = node
                    node.panel = displayScrollEntry
                    node.scroll = self.sr.selfProxy
                    if hasattr(displayScrollEntry, 'Startup'):
                        displayScrollEntry.Startup(self.sr.selfProxy)
                    displayScrollEntry.Load(node)
                    forceTabstops = True
                    nodeLoaded = True
                elif not displayScrollEntry.display:
                    displayScrollEntry.state = uiconst.UI_NORMAL
                    if not node.isStatic:
                        displayScrollEntry.Load(node)
                    forceTabstops = True
                    nodeLoaded = True
                self.visibleNodes.append(node)
                if not ignoreTabstops:
                    updateTabs = node.tabs != tabStops
                    if forceTabstops or updateTabs:
                        self.ApplyTabstopsToNode(node, 'UpdatePosition')

            self.OnUpdatePosition(self)
            return nodeLoaded

    def UpdateScrollHandle(self, clipperHeight, fromWhere=''):
        if self.destroyed or not self.sr.scrollcontrols:
            return
        self.sr.scrollcontrols.SetScrollHandleSize(clipperHeight, self._totalHeight)
        if self._position and self.scrollingRange:
            self.sr.scrollcontrols.SetScrollHandlePos(self._position / float(self.scrollingRange))
        else:
            self.sr.scrollcontrols.SetScrollHandlePos(0.0)

    def OnChar(self, enteredChar, *args):
        if enteredChar < 32:
            return False
        elif not self.sr.nodes:
            return False
        else:
            haveCharIndex = False
            for node in self.sr.nodes:
                if node.charIndex is not None:
                    haveCharIndex = True
                    break

            if not haveCharIndex:
                return False
            if blue.os.TimeAsDouble(blue.os.GetWallclockTime()) - self.lastCharReceivedAt < 1.0 and self.currChars is not None:
                self.currChars += unichr(enteredChar).lower()
            else:
                self.currChars = unichr(enteredChar).lower()
            if enteredChar == uiconst.VK_SPACE:
                selected = self.GetSelected()
                if len(selected) == 1 and self.currChars == ' ' and GetAttrs(selected[0], 'panel', 'OnCharSpace') is not None:
                    selected[0].panel.OnCharSpace(enteredChar)
                    return True
            uthread.new(self._OnCharThread, enteredChar)
            self.lastCharReceivedAt = blue.os.TimeAsDouble(blue.os.GetWallclockTime())
            return True

    def ScrollToSelectedNode(self):
        selected = self.GetSelected()
        if selected:
            self.ScrollToNode(selected[0])

    def ScrollToNode(self, node):
        numEntries = len(self.sr.nodes)
        if numEntries <= 1:
            return
        entryPos = self.sr.nodes.index(node)
        self.ScrollToProportion(float(entryPos) / (numEntries - 1))

    def _OnCharThread(self, enteredChar):
        if self.destroyed:
            return
        charsBefore = self.currChars
        blue.pyos.synchro.SleepWallclock(100)
        if self.destroyed:
            return
        if self.currChars != charsBefore:
            return
        selected = self.GetSelected()
        if not selected:
            selected = self.sr.nodes
        selected = selected[0]
        numEntries = len(self.sr.nodes)
        if selected not in self.sr.nodes:
            return
        startIndex = self.sr.nodes.index(selected)
        if len(self.currChars) == 1:
            startIndex += 1
        entryRange = range(numEntries)[startIndex:] + range(numEntries)[:startIndex]
        for i in entryRange:
            entry = self.sr.nodes[i]
            if entry.charIndex and entry.charIndex.lower().startswith(self.currChars):
                self.SelectNode(entry)
                self.ScrollToNode(entry)
                break

    def OnDelete(self):
        pass

    def OnUpdatePosition(self, *args):
        pass

    def ShowLoading(self):
        if not self.loadingWheel:
            self.loadingWheel = LoadingWheel(name='myLoadingWheel', parent=self, align=uiconst.CENTER, width=80, height=80)
        self.ShowHint(None)
        return

    def HideLoading(self):
        if self.loadingWheel:
            self.loadingWheel.Close()
            self.loadingWheel = None
        return

    def CheckOverlaysAndUnderlays(self):
        for overlay, attrs, x, y in self.sr.overlays + self.sr.underlays:
            if overlay is None or overlay.destroyed:
                continue
            if attrs.Get('align', None) == 'right':
                overlay.left = self.GetContentWidth() - overlay.width - attrs.left
            if not overlay.loaded:
                overlay.top = attrs.top
                overlay.SetAlign(uiconst.RELATIVE)
                overlay.state = uiconst.UI_NORMAL
                overlay.Load()

        return

    def GetNode(self, idx, checkInternalNodes=False):
        if checkInternalNodes:
            allNodes = self.GetNodes(allowNone=True)
        else:
            allNodes = self.sr.nodes
        if idx == -1:
            if allNodes:
                return allNodes[-1]
            else:
                return None
        if len(allNodes) > idx:
            return allNodes[idx]
        else:
            return None

    def OnKeyDown(self, key, flag):
        if uiconst.VK_DELETE == key:
            self.OnDelete()
        elif key == uiconst.VK_PRIOR:
            self.ScrollByPage(up=True)
        elif key == uiconst.VK_NEXT:
            self.ScrollByPage(up=False)

    def ScrollByPage(self, up=True):
        visibleNodes = self.GetVisibleNodes()
        numVisibleNodes = len(visibleNodes)
        allNodesNum = len(self.sr.nodes)
        if numVisibleNodes < 1:
            return
        if up:
            lastVisibleNode = visibleNodes[0]
            step = -1
        else:
            lastVisibleNode = visibleNodes[-1]
            step = 1
        newNodesHeight = lastVisibleNode.height
        currentNodeIdx = lastVisibleNode.idx
        clipperWidth, clipperHeight = self.GetContentParentSize()
        while 1:
            nextNodeIdx = currentNodeIdx + step
            if not 0 < nextNodeIdx < allNodesNum - 1:
                break
            nextNode = self.GetNode(idx=nextNodeIdx, checkInternalNodes=False)
            newNodesHeight += nextNode.height
            if newNodesHeight > clipperHeight:
                break
            currentNodeIdx = nextNodeIdx

        self.ShowNodeIdx(currentNodeIdx)
        self.sr.scrollcontrols.AnimFade()

    def Resizing(self):
        pass

    def OnClipperResize(self, clipperWidth, clipperHeight, *args, **kw):
        self.OnContentResize(clipperWidth, clipperHeight, *args, **kw)

    def OnContentResize(self, clipperWidth, clipperHeight, *args, **kw):
        if self.sr.hint:
            w, h = clipperWidth, clipperHeight
            newWidth = w - self.sr.hint.left * 2
            if abs(newWidth - self.sr.hint.width) > 12:
                self.sr.hint.width = newWidth
        if self.sr.content:
            self.RefreshNodes(fromWhere='OnContentResize')
            self.UpdatePositionThreaded(fromWhere='OnContentResize')
        if not self.destroyed:
            self.Resizing()

    def BrowseNodes(self, up):
        sel = self.GetSelected()
        control = uicore.uilib.Key(uiconst.VK_CONTROL)
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        if sel:
            shiftIdx = None
            if not control and shift:
                r = [ node.idx for node in sel ]
                if up:
                    if r[0] < self.lastSelected:
                        shiftIdx = r[0] - 1
                    else:
                        shiftIdx = r[-1] - 1
                elif r[0] < self.lastSelected:
                    shiftIdx = r[0] + 1
                else:
                    shiftIdx = r[-1] + 1
            if shiftIdx is None:
                if len(sel) > 1:
                    idx = sel[[-1, 0][up]].idx
                else:
                    idx = sel[-1].idx
                idx += [1, -1][up]
            else:
                idx = shiftIdx
            total = len(self.GetNodes())
            if 0 <= idx < total:
                self.ActivateIdx(idx)
                return 1
        return 0

    BrowseEntries = BrowseNodes

    def OnUp(self):
        if not self.GetSelected():
            self.ActivateIdx(len(self.sr.nodes) - 1)
            return
        if not self.BrowseNodes(1):
            self.Scroll(1 + 10 * uicore.uilib.Key(uiconst.VK_SHIFT))

    def OnDown(self):
        if not self.GetSelected():
            self.ActivateIdx(0)
            return
        if not self.BrowseNodes(0):
            self.Scroll(-1 - 10 * uicore.uilib.Key(uiconst.VK_SHIFT))

    def OnHome(self):
        self.ScrollToProportion(0.0)

    def OnEnd(self):
        self.ScrollToProportion(1.0)

    def OnMouseWheel(self, *etc):
        if getattr(self, 'wheeling', 0):
            return 1
        self.wheeling = 1
        self.Scroll(uicore.uilib.dz / 240.0)
        self.wheeling = 0

    def Scroll(self, dz):
        if not self.scrollEnabled:
            return
        if self.debug:
            log.LogInfo('vscroll', 'Scroll %s' % (dz,))
        step = 37
        pos = max(0, min(self.scrollingRange, self._position - step * dz))
        if pos != self._position:
            self._position = int(pos)
            self.stickToBottom = False
            self.UpdatePositionThreaded(fromWhere='Scroll')

    def GetScrollProportion(self):
        if self.scrollingRange:
            return self._position / float(self.scrollingRange)

    @telemetry.ZONE_METHOD
    def ScrollToProportion(self, proportion, threaded=True):
        if not self.scrollEnabled:
            return
        proportion = min(1.0, max(0.0, proportion))
        pos = int(max(0, self.scrollingRange * proportion))
        self._position = int(pos)
        if threaded:
            self.UpdatePositionThreaded(fromWhere='ScrollToPorportion')
        else:
            self.UpdatePosition(fromWhere='ScrollToPorportion')

    def GetMinSize(self):
        pass

    def GetMaxTextWidth(self, defaultTextWidth=0):
        nodes = self.GetNodes()
        if not nodes:
            return defaultTextWidth
        textWidths = []
        for node in nodes:
            fontsize = node.Get('fontsize', DEFAULT_FONTSIZE)
            hspace = node.Get('letterspace', DEFAULT_LETTERSPACE)
            uppercase = node.Get('uppercase', DEFAULT_UPPERCASE)
            textWidth = uicore.font.GetTextWidth(node.label, fontsize, hspace, uppercase)
            padLeft = node.Get('padLeft', TABMARGIN)
            padRight = node.Get('padRight', TABMARGIN)
            padIndentation = uiconst.ENTRY_DEFAULT_ICONSIZE * (1 + node.get('sublevel', 0))
            textWidth += padIndentation + padLeft + padRight
            textWidths.append(textWidth)

        return max(textWidths)

    def GetNoItemNode(self, text, sublevel=0, *args):
        from carbonui.control.scrollentries import ScrollEntryNode
        return ScrollEntryNode(label=text, sublevel=sublevel)

    def Copy(self, *args):
        myNodes = self.GetSelected() or self.GetNodes()
        allLabelsList = []
        for node in myNodes:
            if node.decoClass and getattr(node.decoClass, 'GetCopyData', None):
                label = node.decoClass.GetCopyData(node)
                if label:
                    allLabelsList.append(label)

        allLabels = '\n'.join(allLabelsList)
        allLabels = allLabels.replace('<t>', '\t')
        strippedText = StripTags(allLabels)
        if strippedText:
            blue.pyos.SetClipboardData(strippedText)
        return


class ScrollControlsCore(Container):
    __guid__ = 'uicontrols.ScrollControlsCore'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.Prepare_()

    def Prepare_(self):
        LineThemeColored(parent=self, align=uiconst.TOLEFT, opacity=uiconst.OPACITY_FRAME)
        self.sr.underlay = Frame(name='__underlay', frameConst=uiconst.FRAME_FILLED_CORNER0, parent=self)
        self.Prepare_ScrollHandle_()

    def Prepare_ScrollHandle_(self):
        subparent = Container(name='subparent', parent=self, align=uiconst.TOALL, padding=(-1, 0, 0, 0))
        self.sr.scrollhandle = ScrollHandleCore(name='__scrollhandle', parent=subparent, align=uiconst.TOPLEFT, pos=(0, 0, 2, 2), state=uiconst.UI_NORMAL, idx=0)

    def Startup(self, dad):
        self.dad = weakref.ref(dad)
        self.sr.scrollhandle.Startup(dad)

    def AccessScroll(self):
        if self.dad:
            return self.dad()

    def OnMouseDown(self, *args):
        scrollTop = self.sr.scrollhandle
        l, t, w, h = self.GetAbsolute()
        absTop = t + scrollTop.width + scrollTop.height / 2
        absBottom = t + h - scrollTop.width - scrollTop.height / 2
        proportion = (uicore.uilib.y - absTop) / float(absBottom - absTop)
        proportion = min(1.0, max(0.0, proportion))
        scrollControl = self.AccessScroll()
        if scrollControl:
            scrollControl.stickToBottom = 0
            scrollControl.ScrollToProportion(proportion, threaded=False)

    def SetScrollHandleSize(self, displayHeight, contentHeight):
        if self.sr.scrollhandle:
            self.sr.scrollhandle.UpdateSize(displayHeight, contentHeight)

    def SetScrollHandlePos(self, posFraction):
        if self.sr.scrollhandle:
            self.sr.scrollhandle.ScrollToProportion(posFraction)


class ScrollHandle(Container):
    __guid__ = 'uicontrols.ScrollHandle'
    OPACITY_INACTIVE = 0.6
    OPACITY_ACTIVE = 1.0

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.sr.hilite = None
        self._dragging = False
        self.Prepare_()
        return

    def Prepare_(self):
        self.sr.hilite = RaisedUnderlay(name='hilite', parent=self, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW, opacity=self.OPACITY_INACTIVE, hideFrame=True)

    def Startup(self, dad):
        self.dad = weakref.ref(dad)

    def AccessScroll(self):
        if self.dad:
            return self.dad()

    def UpdateSize(self, displayHeight, contentHeight):
        if displayHeight and contentHeight:
            sizePortion = max(0.0, min(1.0, float(displayHeight) / contentHeight))
        else:
            sizePortion = 0.0
        scrollAreaHeight = displayHeight - self.parent.padTop - self.parent.padBottom
        self.height = max(6, int(scrollAreaHeight * sizePortion))
        self.width = self.parent.parent.width - self.left * 2

    def ScrollToProportion(self, proportion):
        proportion = min(1.0, max(0.0, proportion))
        w, h = self.parent.GetCurrentAbsoluteSize()
        self.top = int((h - self.height) * proportion)

    def OnMouseDown(self, btn, *args):
        if btn != uiconst.MOUSELEFT:
            return
        self.startdragdata = (uicore.uilib.y, self.top)
        self._dragging = 1
        scrollControl = self.AccessScroll()
        if scrollControl:
            scrollControl.sr.content.state = uiconst.UI_DISABLED
            scrollControl.stickToBottom = 0
        self.sr.hilite.OnMouseDown()

    def OnMouseMove(self, *etc):
        self.MouseMove()

    def MouseMove(self, *args):
        if not self._dragging:
            return
        if not uicore.uilib.leftbtn:
            self._dragging = 0
            return
        y0, top0 = self.startdragdata
        w, h = self.parent.GetCurrentAbsoluteSize()
        range_ = h - self.height
        self.top = max(0, min(range_, top0 - y0 + uicore.uilib.y))
        scrollTo = 0.0
        if range_ and self.top:
            scrollTo = self.top / float(range_)
        scrollControl = self.AccessScroll()
        if scrollControl:
            scrollControl.ScrollToProportion(scrollTo)

    def OnMouseUp(self, btn, *args):
        if btn == uiconst.MOUSELEFT:
            self._dragging = 0
        scrollControl = self.AccessScroll()
        if scrollControl:
            scrollControl.sr.content.state = uiconst.UI_NORMAL
            scrollControl.UpdatePositionThreaded(fromWhere='OnMouseUp')
        self.sr.hilite.OnMouseUp()

    def OnMouseEnter(self, *args):
        self.sr.hilite.OnMouseEnter()
        uicore.animations.FadeTo(self.sr.hilite, self.sr.hilite.opacity, self.OPACITY_ACTIVE, duration=0.15)

    def OnMouseExit(self, *args):
        self.sr.hilite.OnMouseExit()
        uicore.animations.FadeTo(self.sr.hilite, self.sr.hilite.opacity, self.OPACITY_INACTIVE, duration=0.5)


class ColumnHeaderCore(Container):
    __guid__ = 'uicontrols.ScrollColumnHeaderCore'
    headerFontSize = 10
    letterspace = 1

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.Prepare_Divider_()
        self.Prepare_Label_()
        self.sr.label.text = attributes.label
        self.draggingAllowed = 0
        self.sr.triangle = None
        self.sr.selection = None
        return

    def Prepare_Divider_(self):
        LineThemeColored(parent=self, align=uiconst.TORIGHT, opacity=uiconst.OPACITY_FRAME)

    def Prepare_Label_(self):
        textclipper = Container(name='textclipper', parent=self, align=uiconst.TOALL, padding=(6, 2, 6, 0), state=uiconst.UI_PICKCHILDREN, clipChildren=1)
        self.sr.label = LabelCore(text='', parent=textclipper, letterspace=self.letterspace, fontsize=self.headerFontSize, hilightable=1, state=uiconst.UI_DISABLED, uppercase=1)

    def _OnClose(self):
        if self.sr.selection:
            s = self.sr.selection
            self.sr.selection = None
            s.Close()
        Container._OnClose(self)
        return

    def _OnEndDrag(self, *args):
        if self.sr.frame:
            f = self.sr.frame
            self.sr.frame = None
            f.Close()
        for each in self.children:
            if each.name == 'scaler':
                each.state = uiconst.UI_NORMAL

        if hasattr(uicore.uilib.mouseOver, 'OnDropColumn'):
            uicore.uilib.mouseOver.OnDropColumn(self)
        return

    def _OnStartDrag(self, *args):
        for each in self.children:
            if each.name == 'scaler':
                each.state = uiconst.UI_HIDDEN

        self.sr.frame = Frame(parent=self, idx=0)

    def OnDropColumn(self, droppings):
        if droppings == self:
            return
        l, t, w, h = self.GetAbsolute()
        if uicore.uilib.x < l + w / 2:
            newIdx = self.sr.idx
        else:
            newIdx = self.sr.idx + 1
        if self.scroll and self.scroll():
            self.scroll().ChangeColumnOrder(droppings.sr.column, newIdx)

    def OnDblClick(self, *args):
        if self.scroll and self.scroll():
            self.scroll().ResetColumnWidth(self.sr.column)

    def OnClick(self, *args):
        if self.sr.sortdir is not None:
            if self.scroll and self.scroll():
                self.scroll().ChangeSortBy(self.sr.header)
        return

    def GetMenu(self, *args):
        if self.scroll and self.scroll():
            return self.scroll().GetHeaderMenu(self.sr.column)

    def Deselect(self):
        if self.sr.triangle:
            self.sr.triangle.state = uiconst.UI_HIDDEN
            if self.sr.label.align == uiconst.CENTERRIGHT:
                self.sr.label.left = 0
        if self.sr.selection:
            self.sr.selection.state = uiconst.UI_HIDDEN

    def Select(self, rev, *args):
        self.ShowSortDirection([1, -1][rev])

    def ShowSortDirection(self, direction):
        if direction is None:
            return
        else:
            if not self.sr.triangle:
                self.sr.triangle = Sprite(align=uiconst.CENTERRIGHT, pos=(3, 0, 16, 16), parent=self, idx=0, name='directionIcon')
            self.sr.triangle.state = uiconst.UI_DISABLED
            if self.sr.label.align == uiconst.CENTERRIGHT:
                self.sr.label.left = 8
            if direction == 1:
                self.sr.triangle.texturePath = 'res:/UI/Texture/Icons/1_16_16.png'
            else:
                self.sr.triangle.texturePath = 'res:/UI/Texture/Icons/1_16_15.png'
            return


class ScrollCoreOverride(ScrollCore):
    pass


class ColumnHeaderCoreOverride(ColumnHeaderCore):
    pass