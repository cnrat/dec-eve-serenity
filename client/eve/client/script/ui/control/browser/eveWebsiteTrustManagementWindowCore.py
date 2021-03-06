# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\control\browser\eveWebsiteTrustManagementWindowCore.py
import localization
from carbonui.control.browser.websiteTrustManagementWindow import WebsiteTrustManagementWindowCore, WebsiteTrustManagementWindowCoreOverride
from eve.client.script.ui.control.eveLabel import WndCaptionLabel

class WebsiteTrustManagementWindow(WebsiteTrustManagementWindowCore):
    __guid__ = 'uicls.WebsiteTrustManagementWindow'
    default_iconNum = 'res:/ui/Texture/WindowIcons/browser.png'

    def ApplyAttributes(self, attributes):
        WebsiteTrustManagementWindowCore.ApplyAttributes(self, attributes)
        self.SetWndIcon(self.iconNum)
        WndCaptionLabel(text=localization.GetByLabel('UI/Browser/TrustedManagementHeader'), parent=self.sr.topParent)


WebsiteTrustManagementWindowCoreOverride.__bases__ = (WebsiteTrustManagementWindow,)