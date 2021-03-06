# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\cef\componentViews\proximityComponentView.py
from carbon.common.script.cef.baseComponentView import BaseComponentView

class ProximityComponentView(BaseComponentView):
    __guid__ = 'cef.ProximityComponentView'
    __COMPONENT_ID__ = const.cef.PROXIMITY_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Proximity'
    __COMPONENT_CODE_NAME__ = 'proximity'
    __SHOULD_SPAWN__ = {'client': False,
     'server': True}

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)


ProximityComponentView.SetupInputs()