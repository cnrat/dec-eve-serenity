# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\carbonui\control\browser\browserSourceWindow.py
import carbonui.const as uiconst
import uthread
import blue
import browser
import localization
from carbonui.primitives.fill import Fill
from carbonui.control.window import WindowCoreOverride as Window

class BrowserSourceWindowCore(Window):
    __guid__ = 'uicls.BrowserSourceWindowCore'
    default_windowID = 'BrowserSourceWindowCore'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.MakeUnstackable()
        mainArea = self.GetMainArea()
        bp = browser.BrowserPane(parent=mainArea, padding=6, align=uiconst.TOALL, state=uiconst.UI_NORMAL)
        bp.Startup()
        self.browserPane = bp
        Fill(parent=mainArea, padding=const.defaultPadding, color=(0.0, 0.0, 0.0, 1.0))
        self.browserSession = browser.BrowserSession()
        self.browserSession.Startup('viewSource', browserEventHandler=self)
        self.browserSession.SetBrowserSurface(bp.GetSurface(), self.browserPane._OnSurfaceReady)
        self.browserSession.SetViewSourceMode(True)
        self.browserPane.browserSession = self.browserSession
        self.sizeChanged = False
        self.browserPane.ResizeBrowser()
        url = attributes.browseTo
        if url is not None:
            self.BrowseTo(url)
        return

    def BrowseTo(self, url=None, *args, **kwargs):
        try:
            self.SetCaption(localization.GetByLabel('UI/Browser/HTMLSourceOf', url=url))
        except:
            self.SetCaption(url)

        self.browserSession.BrowseTo(url=url, *args)

    def OnResizeUpdate(self, *args):
        if not self.sizeChanged:
            uthread.new(self.DoResizeBrowser)
            self.sizeChanged = True

    def DoResizeBrowser(self):
        blue.pyos.synchro.SleepWallclock(250)
        if getattr(self, 'browserPane', None):
            self.browserPane.ResizeBrowser()
        self.sizeChanged = False
        return

    def _OnClose(self, *args):
        self.browserPane.browserSession = None
        self.browserSession.Cleanup()
        self.browserSession = None
        return


class BrowserSourceWindowCoreOverride(BrowserSourceWindowCore):
    pass