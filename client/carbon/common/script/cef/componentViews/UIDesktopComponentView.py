# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\cef\componentViews\UIDesktopComponentView.py
from carbon.common.script.cef.baseComponentView import BaseComponentView

class UIDesktopComponentView(BaseComponentView):
    __guid__ = 'cef.UIDesktopComponentView'
    __COMPONENT_ID__ = const.cef.UIDESKTOP_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'UIDesktop'
    __COMPONENT_CODE_NAME__ = 'UIDesktopComponent'
    __SHOULD_SPAWN__ = {'client': True}
    UI_DESKTOP_NAME = 'uiDesktopName'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.UI_DESKTOP_NAME, '', cls.RECIPE, const.cef.COMPONENTDATA_STRING_TYPE, displayName='UI Desktop Name')


UIDesktopComponentView.SetupInputs()