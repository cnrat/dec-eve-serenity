# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\cef\componentViews\lightsComponentView.py
from carbon.common.script.cef.baseComponentView import BaseComponentView

class LoadedLightComponentView(BaseComponentView):
    __guid__ = 'cef.LoadedLightComponentView'
    __COMPONENT_ID__ = const.cef.LOADED_LIGHT_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Loaded Light'
    __COMPONENT_CODE_NAME__ = 'loadedLight'
    __SHOULD_SPAWN__ = {'client': True}
    RED_FILE = 'resPath'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.RED_FILE, '', cls.RECIPE, const.cef.COMPONENTDATA_STRING_TYPE, displayName='Red File')
        cls._AddInput('useBoundingBox', 0, cls.RECIPE, const.cef.COMPONENTDATA_BOOL_TYPE, displayName='Use Bounding Box')
        cls._AddInput('bbPos', '(0.0,0.0,0.0)', cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_VECTOR_AS_STRING_TYPE, displayName='BB Position')
        cls._AddInput('bbRot', '(0.0,0.0,0.0)', cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_VECTOR_AS_STRING_TYPE, displayName='BB Rotation')
        cls._AddInput('bbScale', '(1.0,1.0,1.0)', cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_VECTOR_AS_STRING_TYPE, displayName='BB Scale')


LoadedLightComponentView.SetupInputs()