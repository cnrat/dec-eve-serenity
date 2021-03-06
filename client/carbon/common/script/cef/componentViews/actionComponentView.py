# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\cef\componentViews\actionComponentView.py
from carbon.common.script.cef.baseComponentView import BaseComponentView
import zaction

class ActionComponentView(BaseComponentView):
    __guid__ = 'cef.ActionComponentView'
    __COMPONENT_ID__ = const.cef.ACTION_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'ActionTree'
    __COMPONENT_CODE_NAME__ = 'action'
    DEFAULT_ACTION_ID = const.zactionConst.ACTIONTREE_RECIPE_DEFAULT_ACTION_NAME

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.DEFAULT_ACTION_ID, None, cls.RECIPE, const.cef.COMPONENTDATA_ARBITRARY_DROPDOWN_TYPE, callback=cls._GetActionList, displayName='Default Action')
        return

    @staticmethod
    def _GetActionList(*args):
        actionList = zaction.Tree.GetActionNameIDMappingList()
        validList = [ (action[0], action[1], '') for action in actionList ]
        return validList


ActionComponentView.SetupInputs()