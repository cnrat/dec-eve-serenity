# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\cef\componentViews\occluderComponentView.py
from carbon.common.script.cef.baseComponentView import BaseComponentView

class OccluderComponentView(BaseComponentView):
    __guid__ = 'cef.OccluderComponentView'
    __COMPONENT_ID__ = const.cef.OCCLUDER_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Occluder'
    __COMPONENT_CODE_NAME__ = 'occluder'
    __SHOULD_SPAWN__ = {'client': True}
    __DESCRIPTION__ = 'A box that visually occludes objects behind it'
    SCALE_X = 'scaleX'
    SCALE_Y = 'scaleY'
    SCALE_Z = 'scaleZ'
    CELL_NAME = 'cellName'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.SCALE_X, 0.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='X Scale')
        cls._AddInput(cls.SCALE_Y, 0.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Y Scale')
        cls._AddInput(cls.SCALE_Z, 0.0, cls.RECIPE, const.cef.COMPONENTDATA_FLOAT_TYPE, displayName='Z Scale')
        cls._AddInput(cls.CELL_NAME, None, cls.SPAWN_ONLY, const.cef.COMPONENTDATA_CELL_TYPE, displayName='Cell Name')
        return


OccluderComponentView.SetupInputs()