# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\extras\cider.py
import blue
import ctypes
import log
import service

class CiderService(service.Service):
    __guid__ = 'svc.cider'
    __servicename__ = 'ciderSvc'
    __displayname__ = 'Transgaming specific methods'
    __exportedcalls__ = {'GetFullscreen': [],
     'SetFullscreen': [],
     'GetMultiThreadedOpenGL': [],
     'SetMultiThreadedOpenGL': []}
    __startupdependencies__ = ['settings']

    def Run(self, *args):
        service.Service.Run(self, args)
        self.SetFullscreen(self.GetFullscreen())
        self.SetMultiThreadedOpenGL(self.GetMultiThreadedOpenGL())
        self.state = service.SERVICE_RUNNING

    def SetFullscreen(self, fullscreenEnabled, setAPI=True):
        if not blue.sysinfo.isTransgaming:
            return
        try:
            if setAPI:
                ctypes.windll.user32.TGSetFullscreen(fullscreenEnabled)
            settings.public.ui.Set('MacFullscreen', fullscreenEnabled)
        except:
            log.LogException()

    def GetFullscreen(self, apiCheck=False):
        if apiCheck:
            return ctypes.windll.user32.TGIsFullscreen()
        return settings.public.ui.Get('MacFullscreen', True)

    def SetMultiThreadedOpenGL(self, doMultiThread):
        if not blue.sysinfo.isTransgaming:
            return
        try:
            ctypes.windll.user32.TGSetMTGL(doMultiThread)
            settings.public.ui.Set('MacMTOpenGL', doMultiThread)
        except:
            log.LogException()

    def GetMultiThreadedOpenGL(self):
        return settings.public.ui.Get('MacMTOpenGL', False)

    def HasFullscreenModeChanged(self):
        if not blue.sysinfo.isTransgaming:
            return False
        return ctypes.windll.user32.TGIsFullscreen() != settings.public.ui.Get('MacFullscreen', True)