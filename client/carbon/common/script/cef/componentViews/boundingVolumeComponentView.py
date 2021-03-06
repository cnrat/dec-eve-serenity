# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\cef\componentViews\boundingVolumeComponentView.py
from carbon.common.script.cef.baseComponentView import BaseComponentView

class BoundingVolumeComponentView(BaseComponentView):
    __guid__ = 'cef.BoundingVolumeComponentView'
    __COMPONENT_ID__ = const.cef.BOUNDING_VOLUME_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'BoundingVolume'
    __COMPONENT_CODE_NAME__ = 'boundingVolume'
    MIN = 'min'
    MAX = 'max'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.MIN, None, cls.RUNTIME, const.cef.COMPONENTDATA_NON_PRIMITIVE_TYPE, displayName='Min')
        cls._AddInput(cls.MAX, None, cls.RUNTIME, const.cef.COMPONENTDATA_NON_PRIMITIVE_TYPE, displayName='Max')
        return


BoundingVolumeComponentView.SetupInputs()