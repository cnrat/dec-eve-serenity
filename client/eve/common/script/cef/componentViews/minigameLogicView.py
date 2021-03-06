# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\script\cef\componentViews\minigameLogicView.py
from carbon.common.script.cef.baseComponentView import BaseComponentView

class MinigameLogicView(BaseComponentView):
    __guid__ = 'cef.MinigameLogicView'
    __COMPONENT_ID__ = const.cef.MINIGAME_LOGIC_COMPONENT_ID
    __COMPONENT_DISPLAY_NAME__ = 'Minigame Logic'
    __COMPONENT_CODE_NAME__ = 'minigameLogic'
    __COMPONENT_DEPENDENCIES__ = [const.cef.MINIGAME_AI_COMPONENT_ID, const.cef.MINIGAME_CONFIG_COMPONENT_ID]
    GAME_TYPE = 'gameType'

    @classmethod
    def SetupInputs(cls):
        cls.RegisterComponent(cls)
        cls._AddInput(cls.GAME_TYPE, -1, cls.RECIPE, const.cef.COMPONENTDATA_ID_TYPE, displayName='Game Type')


MinigameLogicView.SetupInputs()