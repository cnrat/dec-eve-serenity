# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\carbonui\control\baselink.py
import blue
from carbonui.util.bunch import Bunch
from carbon.common.script.util import commonutils
from carbonui.util import various_unsorted
from carbonui.util import stringManip
from carbonui.control.menuLabel import MenuLabel
import log
import types
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill

class BaseLinkCore(Container):
    __guid__ = 'uicontrols.BaseLinkCore'
    isDragObject = True

    def GetDragData(self, *args):
        if getattr(self, 'url', None) and getattr(self, 'linkText', None):
            entry = Bunch()
            entry.__guid__ = 'TextLink'
            entry.url = self.url
            entry.displayText = self.linkText
            return [entry]
        else:
            return

    @classmethod
    def PrepareDrag(cls, dragContainer, dragSource, *args):
        dragData = dragContainer.dragData[0]
        displayText = stringManip.TruncateStringTo(dragData.displayText, 24, '...')
        from carbonui.control.label import LabelOverride as Label
        label = Label(parent=dragContainer, text=commonutils.StripTags(displayText), align=uiconst.TOPLEFT, bold=True)
        Fill(parent=dragContainer, color=(0, 0, 0, 0.3), padding=(-10, -2, -10, -2))
        dragContainer.width = label.textwidth
        dragContainer.height = label.textheight
        return (2, label.textheight)

    def OnClick(self, *args):
        if self.url:
            self.ClickLink(self, self.url.replace('&amp;', '&'))

    def ClickLink(self, parent, URL):
        if URL.startswith('shellexec:http://') or URL.startswith('shellexec:https://'):
            blue.os.ShellExecute(URL[10:])
            return
        if URL.startswith('localsvc:'):
            self.LocalSvcCall(URL[9:])
            return
        linkUsed = self.ClickGameLinks(parent, URL)
        if linkUsed:
            return
        if self.CanOpenBrowser():
            if uicore.commandHandler:
                browser = uicore.commandHandler.OpenBrowser(URL)
        else:
            browser = various_unsorted.GetBrowser(parent)
            if browser:
                if hasattr(browser.sr, 'window') and hasattr(browser.sr.window, 'ShowHint'):
                    browser.sr.window.ShowHint('')
                browser.GoTo(URL)
            else:
                self.UrlHandlerDelegate(parent, 'GoTo', URL)

    def GetStandardLinkHint(self, *args, **kwds):
        return None

    def LoadTooltipPanel(self, tooltipPanel, *args):
        pass

    def GetLinkFormat(self, url, linkState=None, linkStyle=None):
        linkState = linkState or uiconst.LINK_IDLE
        fmt = Bunch()
        if linkState in (uiconst.LINK_IDLE, uiconst.LINK_DISABLED):
            fmt.color = -23040
        elif linkState in (uiconst.LINK_ACTIVE, uiconst.LINK_HOVER):
            fmt.color = -256
        fmt.bold = True
        return fmt

    def FormatLinkParams(self, params, linkState=None, linkStyle=None):
        if 'priorUrlColor' not in params:
            params.priorUrlColor = params.color
        if 'priorUrlBold' not in params:
            params.priorUrlBold = params.bold
        if 'priorUrlItalic' not in params:
            params.priorUrlItalic = params.italic
        if 'priorUrlUnderline' not in params:
            params.priorUrlUnderline = params.underline
        linkFmt = self.GetLinkFormat(params.url, linkState, linkStyle)
        if linkFmt.color is not None:
            params.color = linkFmt.color
        if linkFmt.underline is not None:
            params.underline = linkFmt.underline
        if linkFmt.bold is not None:
            params.bold = linkFmt.bold
        if linkFmt.italic is not None:
            params.italic = linkFmt.italic
        return

    def ClickGameLinks(self, parent, URL):
        return False

    def CanOpenBrowser(self, *args):
        return False

    def GetMenu(self):
        if getattr(self, 'url', None) is None:
            return []
        else:
            return self.GetLinkMenu(self, self.url)

    def GetLinkMenu(self, parent, url):
        m = []
        if self.ValidateURL(url):
            url = url.replace('&amp;', '&')
            m += [(MenuLabel('/Carbon/UI/Commands/OpenInNewView'), self.UrlHandlerDelegate, (parent, 'NewView', url))]
            m += [(MenuLabel('/Carbon/UI/Commands/Open'), self.UrlHandlerDelegate, (parent, 'GoTo', url))]
        if url.lower().startswith('http'):
            m += [(MenuLabel('/Carbon/UI/Commands/CopyURL'), self.CopyUrl, (url,))]
        return m

    def ValidateURL(self, URL):
        badURLs = self.GetBadUrls()
        for badURL in badURLs:
            if URL.startswith(badURL):
                return False

        return True

    def GetBadUrls(self, *args):
        return ['shellexec:', 'localsvc:/', 'cmd:/']

    def CopyUrl(self, url):
        blue.pyos.SetClipboardData(url)

    def UrlHandlerDelegate(self, parent, funcName, args):
        handler = getattr(self, 'URLHandler', None)
        if not handler and getattr(parent, 'sr', None) and getattr(parent.sr, 'node', None):
            handler = getattr(parent.sr.node, 'URLHandler', None)
        if handler:
            func = getattr(handler, funcName, None)
            if func:
                apply(func, (args,))
                return
        if uicore.commandHandler:
            uicore.commandHandler.OpenBrowser(args)
        return

    def LocalSvcCall(self, args):
        import htmlwriter
        import service
        kw = htmlwriter.PythonizeArgs(args)
        if 'service' not in kw:
            log.LogError('Invalid LocalSvc args:', args, ' (missing service)')
            return
        sv = kw['service']
        del kw['service']
        if 'method' not in kw:
            log.LogError('Invalid LocalSvc args:', args, ' (missing method)')
            return
        method = kw['method']
        del kw['method']
        svc = sm.GetService(sv)
        access = svc.__exportedcalls__.get(method, [])
        if access and type(access) in (types.ListType, types.TupleType):
            access = access[0]
        elif type(access) == types.DictType:
            access = access.get('role', 0)
        else:
            access = 0
        if access & service.ROLE_IGB:
            apply(getattr(svc, method), (), kw)
        else:
            log.LogError('Invalid LocalSvc args:', args, ' (method not allowed)')


class BaseLinkCoreOverride(BaseLinkCore):
    pass