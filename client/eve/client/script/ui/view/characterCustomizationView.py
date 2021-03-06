# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\view\characterCustomizationView.py
from eve.client.script.ui.services.viewStateSvc import View
from eveaudio import EVE_INCARNA_BANKS
import uicls
from sceneManager import SCENE_TYPE_CHARACTER_CREATION
import localization

class CharacterCustomizationView(View):
    __guid__ = 'viewstate.CharacterCustomizationView'
    __notifyevents__ = ['OnShowUI']
    __dependencies__ = []
    __layerClass__ = uicls.CharacterCreationLayer
    __suppressedOverlays__ = {'sidePanels'}
    __dependencies__ = View.__dependencies__[:]
    __dependencies__.extend(['entityClient', 'cameraClient', 'gameui'])

    def __init__(self):
        View.__init__(self)

    def LoadView(self, charID=None, gender=None, dollState=None, bloodlineID=None, **kwargs):
        sm.GetService('audio').SwapBanks(EVE_INCARNA_BANKS)
        View.LoadView(self)
        self.LogInfo('Opening character creator with arguments', kwargs)
        if charID is not None:
            if session.worldspaceid == session.stationid2:
                player = self.entityClient.GetPlayerEntity()
                if player is not None:
                    pos = player.GetComponent('position')
                    if pos is not None:
                        self.cachedPlayerPos = pos.position
                        self.cachedPlayerRot = pos.rotation
                camera = self.cameraClient.GetActiveCamera()
                if camera is not None:
                    self.cachedCameraYaw = camera.yaw
                    self.cachedCameraPitch = camera.pitch
                    self.cachedCameraZoom = camera.zoom
            change = {'worldspaceid': [session.worldspaceid, None]}
            self.entityClient.ProcessSessionChange(False, session, change)
            self.gameui.OnSessionChanged(False, session, change)
        factory = sm.GetService('character').factory
        factory.compressTextures = False
        factory.allowTextureCache = False
        clothSimulation = sm.GetService('device').GetAppFeatureState('CharacterCreation.clothSimulation', True)
        factory.clothSimulationActive = clothSimulation
        sm.GetService('sceneManager').SetSceneType(SCENE_TYPE_CHARACTER_CREATION)
        self.layer.SetCharDetails(charID, gender, bloodlineID, dollState=dollState)
        uicore.layer.main.display = False
        return

    def UnloadView(self):
        View.UnloadView(self)
        uicore.layer.main.display = True

    def GetProgressText(self, **kwargs):
        if kwargs.get('charID', None) is not None:
            text = localization.GetByLabel('UI/CharacterCustomization/EnteringCharacterCustomization')
        else:
            text = localization.GetByLabel('UI/CharacterCreation/EnteringCharacterCreation')
        return text

    def OnShowUI(self):
        uicore.layer.main.display = False