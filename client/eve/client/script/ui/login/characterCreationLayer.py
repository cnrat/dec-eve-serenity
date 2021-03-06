# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\login\characterCreationLayer.py
from charactercreator.client.logging.stepLogger import StepLogger, StepInfoEventServiceLogger, FinalStepLogger, FinalStepInfoEventServiceLogger
from eve.client.script.ui.login.charcreation.bloodlineDollLoader import BloodlineDollLoader
from eve.client.script.ui.login.charcreation.portraitMaker import PortraitMaker, PortraitCameraConfigurator
import uicontrols
import uicls
import uiprimitives
import uiutil
import carbonui.const as uiconst
import everesourceprefetch
import trinity
import GameWorld
import uthread
import blue
import cameras
import paperDoll
import util
import copy
import ccUtil
import charactercreator.const as ccConst
import random
import log
import types
import telemetry
import math
import mathUtil
import geo2
import service
import paperDollUtil
import localization
import evegraphics.settings as gfxsettings
import gatekeeper
import eve.common.lib.appConst as const
from eve.client.script.ui.util.disconnectNotice import DisconnectNotice
from charactercreator.client.characterCreationSteps import ModeStorage
from eve.client.script.ui.login.charcreation.steps.raceStep import RaceStep
from eve.client.script.ui.login.charcreation.steps.characterBloodlineSelection import CharacterBloodlineSelection
from eve.client.script.ui.login.charcreation.steps.characterCustomization import CharacterCustomization
from eve.client.script.ui.login.charcreation.steps.characterNaming import CharacterNaming
from eve.client.script.ui.login.charcreation.steps.characterPortrait import CharacterPortrait
from evegraphics.fsd.graphicIDs import GetGraphicFile
MINSIDESIZE = 200
LEFTSIZE = 200
RIGHTSIZE = 350
DOLLSTATES_TO_RETURN_TO_CC = [const.paperdollStateNoExistingCustomization, const.paperdollStateForceRecustomize]
CLOTHING_ITEMS = (ccConst.topouter,
 ccConst.topmiddle,
 ccConst.bottomouter,
 ccConst.outer,
 ccConst.feet,
 ccConst.glasses,
 ccConst.bottommiddle)

class CharacterCreationLayer(uicls.LayerCore):
    __guid__ = 'uicls.CharacterCreationLayer'
    __notifyevents__ = ['OnSetDevice',
     'OnGraphicSettingsChanged',
     'OnHideUI',
     'OnShowUI',
     'OnDollUpdated',
     'OnMapShortcut',
     'OnUIRefresh',
     'OnDisconnect']
    __update_on_reload__ = 1

    def setFirstLastNameCallback(self, firstName, lastName):
        self.charFirstName = firstName
        self.charLastName = lastName

    @telemetry.ZONE_METHOD
    def OnSetDevice(self, *args):
        self.UpdateLayout()
        self.UpdateBackdrop()
        if self.stepID == ccConst.BLOODLINESTEP:
            self.CorrectBloodlinePlacement()

    def OnDisconnect(self, reason=0, msg=''):
        disconnectNotice = DisconnectNotice(logProvider=self)
        disconnectNotice.OnDisconnect(reason, msg)

    @telemetry.ZONE_METHOD
    def UpdateLayout(self):
        for each in self.sr.mainCont.children:
            if hasattr(each, 'UpdateLayout'):
                each.UpdateLayout()

    @telemetry.ZONE_METHOD
    def OnOpenView(self):
        self.startTime = blue.os.GetWallclockTime()
        uicore.cmd.commandMap.UnloadAllAccelerators()
        uicore.cmd.commandMap.LoadAcceleratorsByCategory('general')
        uicore.cmd.commandMap.LoadAcceleratorsByCategory('charactercreator')
        self.freezingAnimation = False
        from eve.client.script.ui.shared.preview import PreviewCharacterWnd
        previewWnd = PreviewCharacterWnd.GetIfOpen()
        if previewWnd:
            self.previewWindowWasOpenOn = (previewWnd.charID, previewWnd.dna)
            previewWnd.CloseByUser()
        else:
            self.previewWindowWasOpenOn = None
        sm.GetService('tutorial').ChangeTutorialWndState(visible=False)
        if hasattr(trinity, 'InitializeApex'):
            trinity.InitializeApex(GameWorld.GWPhysXWrapper())
        self._setColorsByCategory = {}
        self._setSpecularityByCategory = {}
        self._setIntensityByCategory = {}
        self.characterSvc = sm.GetService('character')
        self.alreadyLoadedOldPortraitData = False
        self.backdropPath = None
        self.colorCodedBackDrop = None
        self.posePath = None
        self.lightingID = ccConst.LIGHT_SETTINGS_ID[0]
        self.lightColorID = ccConst.LIGHT_COLOR_SETTINGS_ID[0]
        self.lightIntensity = 0.5
        self.camera = None
        self.cameraUpdateJob = None
        self.fastCharacterCreation = gfxsettings.Get(gfxsettings.GFX_CHAR_FAST_CHARACTER_CREATION)
        self.bloodlineSelector = None
        self.raceMusicStarted = False
        self.jukeboxWasPlaying = False
        self.mode = ccConst.MODE_FULLINITIAL_CUSTOMIZATION
        self.modeStorage = ModeStorage()
        self.modeObject = self.modeStorage.GetModeFor(self.mode)
        self.charID = None
        self.raceID = None
        self.bloodlineID = None
        self.genderID = None
        self.ancestryID = None
        self.schoolID = None
        self.charFirstName = ''
        self.charLastName = ''
        self.clothesOff = 0
        self.clothesStorage = {}
        self.dnaList = None
        self.dna = None
        self.lastLitHistoryBit = None
        sm.GetService('cc').ClearMyAvailabelTypeIDs()
        self.stepID = None
        self.floor = None
        self.showingHelp = 0
        self.CreateUI()
        self.avatarScene = None
        self.animatingToPortraitID = None
        self.animateToStoredPortraitThread = None
        audioService = sm.GetService('audio')
        self.worldLevel = audioService.GetWorldVolume()
        audioService.SetWorldVolume(0.0)
        sm.GetService('dynamicMusic').UpdateDynamicMusic()
        self.stepLogger = StepLogger(blue.os.GetWallclockTime)
        self.finalStepLogger = None
        return

    def LogFinalResultsIfNeededAndDestroy(self):
        if self.finalStepLogger is not None:
            finalStepLogger = FinalStepInfoEventServiceLogger(sm.GetService('infoGatheringSvc').LogInfoEvent, sessionID=session.sid, userID=session.userid)
            finalStepLogger.LogFinalStepObjects(self.finalStepLogger.GetFinalStepResult())
            self.finalStepLogger = None
        return

    def CreateANewFinalStepLogger(self):
        self.LogFinalResultsIfNeededAndDestroy()
        self.finalStepLogger = FinalStepLogger()
        self.finalStepLogger.Start()

    def CreateUI(self):
        self.sr.loadingWheel = uicls.LoadingWheel(parent=self, align=uiconst.CENTER, state=uiconst.UI_NORMAL)
        self.sr.loadingWheel.forcedOn = 0
        self.sr.uiContainer = uiprimitives.Container(name='uiContainer', parent=self, align=uiconst.TOALL)
        self.sr.leftSide = uiprimitives.Container(name='leftSide', parent=self.sr.uiContainer, align=uiconst.TOPLEFT, pos=(0,
         0,
         LEFTSIZE,
         400))
        self.sr.rightSide = uiprimitives.Container(name='rightSide', parent=self.sr.uiContainer, align=uiconst.BOTTOMRIGHT, pos=(0,
         0,
         RIGHTSIZE,
         64))
        self.sr.buttonNav = uiprimitives.Container(name='buttonPar', parent=self.sr.rightSide, align=uiconst.TOTOP, height=25, padRight=2)
        self.sr.finalizeBtn = uicls.CharCreationButton(parent=self.sr.buttonNav, align=uiconst.TORIGHT, label=localization.GetByLabel('UI/CharacterCreation/Finalize'), func=self.SaveWithStartLocation, left=10, args=(0,), state=uiconst.UI_HIDDEN, fixedwidth=70)
        self.sr.saveBtn = uicls.CharCreationButton(parent=self.sr.buttonNav, align=uiconst.TORIGHT, label=localization.GetByLabel('UI/CharacterCreation/Finalize'), func=self.Save, left=10, args=(), state=uiconst.UI_HIDDEN, fixedwidth=70)
        self.sr.approveBtn = uicls.CharCreationButton(parent=self.sr.buttonNav, align=uiconst.TORIGHT, label=localization.GetByLabel('UI/Generic/Next'), func=self.Approve, left=10, args=(), fixedwidth=70)
        self.sr.backBtn = uicls.CharCreationButton(parent=self.sr.buttonNav, align=uiconst.TORIGHT, label=localization.GetByLabel('UI/Commands/Back'), func=self.Back, args=(), left=10, fixedwidth=70)
        self.sr.blackOut = uiprimitives.Fill(parent=self, color=(0.0, 0.0, 0.0, 0.0))
        self.sr.mainCont = uiprimitives.Container(name='mainCont', parent=self, align=uiconst.TOALL)
        self.sr.helpButton = uiprimitives.Container(parent=self.sr.uiContainer, pos=(13, 66, 26, 26), state=uiconst.UI_HIDDEN, align=uiconst.BOTTOMLEFT, hint=localization.GetByLabel('UI/CharacterCreation/GetHelp'), idx=0)
        helpIcon = uicontrols.Icon(parent=self.sr.helpButton, icon=ccConst.ICON_HELP, state=uiconst.UI_DISABLED, align=uiconst.CENTER, color=ccConst.COLOR50)
        self.sr.helpButton.OnClick = self.SetStepHelpText
        self.sr.helpButton.OnMouseEnter = (self.OnHelpMouseEnter, self.sr.helpButton)
        self.sr.helpButton.OnMouseExit = (self.OnHelpMouseExit, self.sr.helpButton)
        self.sr.helpButton.sr.icon = helpIcon
        self.sr.helpBox = uiprimitives.Container(name='helpBox', parent=self.sr.uiContainer, pos=(0, 200, 350, 200), state=uiconst.UI_HIDDEN, align=uiconst.CENTER)
        self.sr.helpText = uicontrols.EveLabelMedium(text='', parent=self.sr.helpBox, align=uiconst.TOPLEFT, width=self.sr.helpBox.width)
        self.sr.helpFill = uiprimitives.Fill(name='fill', parent=self.sr.helpBox, color=(0.0, 0.0, 0.0, 0.5), padding=(-8, -8, -8, -8), state=uiconst.UI_NORMAL)
        self.sr.helpFill.OnClick = self.SetStepHelpText
        self.UpdateLayout()

    def OnAvailabilityCheck(self, name):
        self.finalStepLogger.AddTriedName(name)

    def OnUIRefresh(self):
        while getattr(self, 'doll', None) and self.doll.IsBusyUpdating():
            blue.synchro.Yield()

        self.Flush()
        self.CreateUI()
        self.SwitchStep(self.stepID)
        return

    def OnHelpMouseEnter(self, btn, *args):
        btn.sr.icon.SetAlpha(1.0)

    def OnHelpMouseExit(self, btn, *args):
        if not self.showingHelp:
            btn.sr.icon.SetAlpha(0.5)

    def ShowHelpText(self):
        self.showingHelp = 1
        self.sr.helpBox.state = uiconst.UI_NORMAL
        self.sr.helpBox.height = self.sr.helpText.textheight + 16
        self.sr.helpButton.sr.icon.SetAlpha(1.0)

    def HideHelpText(self):
        self.showingHelp = 0
        self.sr.helpText.text = ''
        self.sr.helpBox.state = uiconst.UI_HIDDEN
        self.sr.helpButton.sr.icon.SetAlpha(0.5)

    def SetStepHelpText(self, *args):
        limited = self.modeObject.IsLimited()
        if not self.showingHelp and self.stepID in (ccConst.CUSTOMIZATIONSTEP,
         ccConst.PORTRAITSTEP,
         ccConst.NAMINGSTEP,
         ccConst.MINIMALNAMINGSTEP):
            helpTextDict = {(1, 0): 'UI/CharacterCreation/HelpTexts/Step1',
             (2, 0): 'UI/CharacterCreation/HelpTexts/Step2',
             (3, 0): 'UI/CharacterCreation/HelpTexts/Step3',
             (3, 1): 'UI/CharacterCreation/HelpTexts/Step3Limited',
             (4, 0): 'UI/CharacterCreation/HelpTexts/Step4',
             (4, 1): 'UI/CharacterCreation/HelpTexts/Step4Limited',
             (5, 0): 'UI/CharacterCreation/HelpTexts/Step5',
             (ccConst.MINIMALNAMINGSTEP, 0): 'UI/CharacterCreation/HelpTexts/Step5'}
            labelPath = helpTextDict.get((self.stepID, limited), 'UI/Common/Unknown')
            self.sr.helpText.text = localization.GetByLabel(labelPath)
            self.ShowHelpText()
        else:
            self.HideHelpText()

    def SetHintText(self, modifier, hintText=''):
        if self.stepID in (ccConst.CUSTOMIZATIONSTEP, ccConst.PORTRAITSTEP):
            self.sr.step.SetHintText(modifier, hintText)

    def SetMode(self, modeID):
        self.mode = modeID
        self.modeObject = self.modeStorage.GetModeFor(modeID)

    def GetModeIDForDollState(self, dollState):
        mode = ccConst.MODE_LIMITED_RECUSTOMIZATION
        if dollState == const.paperdollStateFullRecustomizing:
            mode = ccConst.MODE_FULL_BLOODLINECHANGE
        elif dollState in (const.paperdollStateResculpting, const.paperdollStateNoExistingCustomization, const.paperdollStateForceRecustomize):
            mode = ccConst.MODE_FULL_RECUSTOMIZATION
        return mode

    @telemetry.ZONE_METHOD
    def SetCharDetails(self, charID=None, gender=None, bloodlineID=None, dollState=None):
        self.ClearFacePortrait()
        self.dollState = dollState
        self.dna = None
        self.charID = 0
        mode = None
        if charID:
            self.bloodlineID = bloodlineID
            self.genderID = int(gender)
            self.charID = charID
            if dollState not in (const.paperdollStateForceRecustomize, const.paperdollStateNoExistingCustomization):
                self.dna = sm.GetService('paperdoll').GetMyPaperDollData(self.charID)
            bloodlineInfo = sm.GetService('cc').GetBloodlineDataByID().get(self.bloodlineID, None)
            if bloodlineInfo is None:
                raise UserError('CCNoBloodlineInfo')
            self.raceID = bloodlineInfo.raceID
            mode = self.GetModeIDForDollState(dollState)
        else:
            mode = ccConst.MODE_FULLINITIAL_CUSTOMIZATION
        self.SetMode(mode)
        self.availableSteps = self.modeObject.GetSteps()
        stepID = self.availableSteps[0]
        self.stepsUsed = set([stepID])
        self.sr.mainCont.Flush()
        self.stepLogger.Start()
        self.SwitchStep(stepID)
        return

    @telemetry.ZONE_METHOD
    def GetInfo(self):
        return uiutil.Bunch(charID=self.charID, raceID=self.raceID, bloodlineID=self.bloodlineID, genderID=self.genderID, dna=self.dna, ancestryID=self.ancestryID, schoolID=self.schoolID, stepID=self.stepID, charFirstName=self.charFirstName, charLastName=self.charLastName)

    def CanChangeBaseAppearance(self, *args):
        return self.modeObject.CanChangeBaseAppearance()

    def GetMode(self, *args):
        return self.mode

    def CanChangeBloodline(self, *args):
        return self.modeObject.CanChangeBloodLine()

    def CanChangeGender(self, *args):
        return self.modeObject.CanChangeGender()

    def CanChangeName(self, *args):
        return self.modeObject.CanChangeName()

    def ConstructNavigationIfNeeded(self, toStep):
        if not self.sr.mainNav or self.sr.mainNav.destroyed:
            self.sr.mainNav = uicls.CharCreationNavigation(name='navigation', align=uiconst.CENTERTOP, parent=self.sr.leftSide, pos=(0, 16, 0, 60), stepID=toStep, func=self.SwitchStep, stepsUsed=self.stepsUsed, availableSteps=self.availableSteps)

    @telemetry.ZONE_METHOD
    def SwitchStep(self, toStep, *args):
        self.UnfreezeAnimationIfNeeded()
        self.HideHelpText()
        self.ConstructNavigationIfNeeded(toStep)
        info = self.GetInfo()
        characters = self.characterSvc.characters
        if info.charID in characters and self.characterSvc.GetSingleCharactersDoll(info.charID).busyUpdating:
            raise UserError('uiwarning01')
        if toStep > self.stepID:
            if not self.PassedStepCheck(toStep):
                return
        if self.stepID in [ccConst.CUSTOMIZATIONSTEP]:
            sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_sculpting_mouse_over_loop_stop'))
            self.sr.step.StoreHistorySliderPosition()
        elif self.stepID == ccConst.PORTRAITSTEP:
            sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_sculpting_mouse_over_loop_stop'))
            self.StorePortraitCameraSettings()
        self.LockEverything()
        self.sr.step = None
        uthread.new(self.sr.mainNav.PerformStepChange, toStep, self.stepsUsed)
        self.FadeToBlack(why=localization.GetByLabel('UI/Generic/Loading'))
        if toStep == self.availableSteps[-1]:
            self.sr.approveBtn.state = uiconst.UI_HIDDEN
            if not self.charID:
                self.sr.finalizeBtn.state = uiconst.UI_NORMAL
                self.sr.saveBtn.state = uiconst.UI_HIDDEN
            else:
                self.sr.finalizeBtn.state = uiconst.UI_HIDDEN
                self.sr.saveBtn.state = uiconst.UI_NORMAL
        else:
            self.sr.approveBtn.state = uiconst.UI_NORMAL
            self.sr.finalizeBtn.state = uiconst.UI_HIDDEN
            self.sr.saveBtn.state = uiconst.UI_HIDDEN
        self.sr.backBtn.state = uiconst.UI_NORMAL
        self.sr.mainCont.Flush()
        self.Cleanup()
        self.StartStep(toStep)
        if toStep in (ccConst.CUSTOMIZATIONSTEP, ccConst.PORTRAITSTEP, ccConst.NAMINGSTEP):
            self.sr.helpButton.state = uiconst.UI_NORMAL
        else:
            self.sr.helpButton.state = uiconst.UI_HIDDEN
        self.stepID = toStep
        self.stepsUsed.add(toStep)
        self.UpdateBackdrop()
        self.UnlockEverything()
        self.setupDone = 1
        self.FadeFromBlack()
        self.UnfreezeAnimationIfNeeded()
        sm.GetService('dynamicMusic').UpdateDynamicMusic()
        return

    def StartStep(self, toStep):
        self.stepLogger.SetStep(toStep)
        if toStep == ccConst.RACESTEP:
            self.StartRaceStep()
        elif toStep == ccConst.BLOODLINESTEP:
            self.StartBloodlineStep()
        elif toStep == ccConst.CUSTOMIZATIONSTEP:
            self.StartCustomizationStep()
        elif toStep == ccConst.PORTRAITSTEP:
            self.StartPortraitStep()
        elif toStep == ccConst.NAMINGSTEP:
            self.CreateANewFinalStepLogger()
            self.StartNamingStep()
        elif toStep == ccConst.MINIMALNAMINGSTEP:
            self.CreateANewFinalStepLogger()
            self.StartMinimalNamingStep()
        else:
            raise NotImplementedError

    def IsNamingStep(self, step):
        return step in [ccConst.NAMINGSTEP, ccConst.MINIMALNAMINGSTEP]

    @telemetry.ZONE_METHOD
    def StorePortraitCameraSettings(self):
        if self.camera is not None:
            self.storedPortraitCameraSettings = {'poi': self.camera.poi,
             'pitch': self.camera.pitch,
             'yaw': self.camera.yaw,
             'distance': self.camera.distance,
             'xFactor': self.camera.xFactor,
             'yFactor': self.camera.yFactor,
             'fieldOfView': self.camera.fieldOfView}
        return

    @telemetry.ZONE_METHOD
    def FadeToBlack(self, why=''):
        self.ShowLoading(why=why, forceOn=True)
        uicore.effect.CombineEffects(self.sr.blackOut, alpha=1.0, time=500.0)

    @telemetry.ZONE_METHOD
    def FadeFromBlack(self):
        uthread.new(uicore.effect.CombineEffects, self.sr.blackOut, alpha=0.0, time=500.0)
        self.HideLoading(forceOff=1)

    def IsInMinimalMode(self):
        return self.mode is ccConst.MODE_INITIAL_MINI_CUSTOMIZATION

    @telemetry.ZONE_METHOD
    def PassedStepCheck(self, toStep, *args):
        if toStep not in self.availableSteps:
            raise UserError('CCStepUnavailable')
        if toStep == ccConst.BLOODLINESTEP and self.raceID is None:
            raise UserError('CCMustSelectRace')
        if self.IsInMinimalMode():
            return True
        else:
            if not (max(self.stepsUsed) >= toStep or max(self.stepsUsed) + 1 == toStep):
                raise UserError('CCStepUnavailable')
            if toStep == ccConst.CUSTOMIZATIONSTEP and (self.raceID is None or self.bloodlineID is None or self.genderID is None):
                raise UserError('CCMustSelectRaceAndBloodline')
            isNamingStep = self.IsNamingStep(toStep)
            if (toStep == ccConst.PORTRAITSTEP or isNamingStep) and not prefs.GetValue('ignoreCCValidation', False):
                info = self.GetInfo()
                self.ToggleClothes(forcedValue=0)
                self.characterSvc.ValidateDollCustomizationComplete(info.charID)
            currentStepID = None
            if self.sr.step:
                currentStepID = self.sr.step.stepID
            if self.IsNamingStep(toStep) and currentStepID != ccConst.PORTRAITSTEP and self.GetActivePortrait() is None:
                raise UserError('CCStepUnavailable')
            if self.sr.step:
                self.sr.step.ValidateStepComplete()
            return True

    @telemetry.ZONE_METHOD
    def Approve(self, *args):
        self.stepLogger.IncrementNextTryCount()
        idx = self.availableSteps.index(self.stepID)
        if len(self.availableSteps) > idx + 1:
            nextStep = self.availableSteps[idx + 1]
            self.SwitchStep(nextStep)
            uicore.registry.SetFocus(self)

    @telemetry.ZONE_METHOD
    def SaveWithStartLocation(self, startInSpace, *args):
        settings.user.ui.Set('doTutorialDungeon', startInSpace)
        self.Save()

    def MinimalSave(self):
        total = 3
        try:
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/CharacterCreation/Registering'), localization.GetByLabel('UI/CharacterCreation/CompilePrefs'), 1, total)
            characterName = self.CheckAndGetName()
            if characterName is None:
                return
            confirmed = self.AskForPortraitConfirmation(characterName=characterName)
            if not confirmed:
                return
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/CharacterCreation/Registering'), localization.GetByLabel('UI/CharacterCreation/InsertingRecord'), 2, total)
            charID = sm.GetService('cc').CreateCharacterWithRandomDoll(bloodlineID=self.bloodlineID, genderID=self.genderID, characterName=characterName, ancestryID=self.ancestryID, schoolID=self.schoolID)
            sm.GetService('photo').AddPortrait(self.GetPortraitSnapshotPath(1), charID)
        finally:
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/CharacterCreation/Registering'), localization.GetByLabel('UI/Generic/Done'), 3, total)

        self.tryLoginElseCharacterSelection(charID)
        return

    def CheckAndGetName(self):
        isAvailable = self.sr.step.CheckAvailability()
        if isAvailable.charName is None:
            eve.Message('CustomInfo', {'info': isAvailable.reason})
        return isAvailable.charName

    @telemetry.ZONE_METHOD
    def Save(self, *args):
        if self.finalStepLogger:
            self.finalStepLogger.Finalize()
        self.stepLogger.IncrementNextTryCount()
        if self.IsInMinimalMode():
            self.MinimalSave()
        else:
            try:
                selectedPortraitInfo = self.portraitInfo[self.activePortraitIndex]
                if selectedPortraitInfo and selectedPortraitInfo.backgroundID > const.NCC_MAX_NORMAL_BACKGROUND_ID:
                    eve.Message('CustomInfo', {'info': localization.GetByLabel('UI/CharacterCreation/CannotSaveWithThisBackground')})
                    return
                self.LockEverything()
                if self.sr.step:
                    self.sr.step.ValidateStepComplete()
                if self.stepID != self.availableSteps[-1]:
                    raise UserError('CCCannotSave')
                if self.charID and self.modeObject.AskForPortraitConfirmation():
                    confirmed = self.AskForPortraitConfirmation()
                    if not confirmed:
                        return
                    self.UpdateExistingCharacter()
                    return
                if self.bloodlineID is None or self.genderID is None:
                    raise UserError('CCCannotSave2')
                else:
                    characterName = self.CheckAndGetName()
                    if characterName is None:
                        return
                    confirmed = self.AskForPortraitConfirmation(characterName=characterName)
                    if not confirmed:
                        return
                    self.SaveAndEnterCurrentCharacter(characterName)
            finally:
                if self and not self.destroyed:
                    self.UnlockEverything()

        return

    def SaveAndEnterCurrentCharacter(self, characterName):
        charID = self.SaveCurrentCharacter(characterName, self.bloodlineID, self.genderID, self.activePortraitIndex)
        if charID:
            self.characterSvc.CachePortraitInfo(charID, self.portraitInfo[self.activePortraitIndex])
            self.tryLoginElseCharacterSelection(charID)

    def tryLoginElseCharacterSelection(self, charID):
        experimentSvc = None
        self.DoLogEvent(finished=1)
        try:
            settings.user.ui.Set('doTutorialDungeon%s' % charID, 0)
            settings.user.ui.Set('doIntroTutorial%s' % charID, 1)
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/CharacterCreation'), localization.GetByLabel('UI/CharacterCreation/EnteringGameAs', player=charID), 1, 2)
            startInDungeon = sm.GetService('experimentClientSvc').ShouldStartInDungeon()
            sm.GetService('sessionMgr').PerformSessionChange('charcreation', sm.RemoteSvc('charUnboundMgr').SelectCharacterID, charID, startInDungeon, None)
            boundCharacterService = sm.RemoteSvc('charMgr')
            gatekeeper.character.Initialize(lambda args: boundCharacterService.GetCohortsForCharacter)
            experimentSvc = sm.StartService('experimentClientSvc')
            experimentSvc.Initialize(languageID=session.languageID)
        except:
            gatekeeper.character.Teardown()
            if experimentSvc is not None:
                experimentSvc.TearDown()
            sm.GetService('cc').GetCharactersToSelect(force=True)
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/CharacterCreation/CharacterSelection'), localization.GetByLabel('UI/CharacterCreation/FailedToEnterGame'), 2, 2)
            uthread.pool('GameUI::ActivateView::charsel', sm.GetService('viewState').ActivateView, 'charsel')
            raise

        return

    def OnEsc(self):
        self.Back()

    @telemetry.ZONE_METHOD
    def Back(self, *args):
        idx = self.availableSteps.index(self.stepID)
        if idx == 0:
            if self.modeObject.ExitToStation():
                msg = 'AskCancelCharCustomization'
            else:
                msg = 'AskCancelCharCreation'
            if eve.Message(msg, {}, uiconst.YESNO) != uiconst.ID_YES:
                return
            if self.modeObject.ExitToStation():
                self.ExitToStation(updateDoll=False)
            else:
                sm.StartService('cc').GoBack()
            self.DoLogEvent(finished=0)
        else:
            nextStep = self.availableSteps[idx - 1]
            self.SwitchStep(nextStep)
            uicore.registry.SetFocus(self)

    @telemetry.ZONE_METHOD
    def LockEverything(self, *args):
        if not getattr(self, 'setupDone', 0):
            return
        self.pickState = uiconst.TR2_SPS_OFF
        self.LockNavigation()

    @telemetry.ZONE_METHOD
    def LockNavigation(self, *args):
        if not getattr(self, 'setupDone', 0):
            return
        self.sr.buttonNav.state = uiconst.UI_DISABLED
        self.sr.mainNav.state = uiconst.UI_DISABLED

    @telemetry.ZONE_METHOD
    def UnlockEverything(self, *args):
        self.pickState = uiconst.TR2_SPS_CHILDREN
        self.UnlockNavigation()

    @telemetry.ZONE_METHOD
    def UnlockNavigation(self, *args):
        if not self.isopen:
            return
        self.sr.buttonNav.state = uiconst.UI_PICKCHILDREN
        if self.sr.mainNav:
            self.sr.mainNav.state = uiconst.UI_PICKCHILDREN

    @telemetry.ZONE_METHOD
    def SetActivePortrait(self, portraitNo, *args):
        self.activePortraitIndex = portraitNo
        self.activePortrait = self.facePortraits[portraitNo]

    @telemetry.ZONE_METHOD
    def GetActivePortrait(self):
        return self.activePortrait

    def GenerateAndSetPortrait(self):
        if self.IsInMinimalMode():
            path = self.GetBackgroundPathFromID(14)
            cameraConfigurator = PortraitCameraConfigurator()
            cameraConfigurator.SetupPortraitCamera(self.camera, self.minimalDoll.avatar)
            maker = PortraitMaker(self.camera, backdropPath=path)
            photo = maker.GetPortraitTexture(1)
            self.sr.step.SetPhoto(photo)
            cameraConfigurator.RevertToNormalCamera(self.camera, avatar=self.minimalDoll.avatar)
            self.activePortrait = photo

    @telemetry.ZONE_METHOD
    def SetFacePortrait(self, photo, portraitNo, *args):
        self.facePortraits[portraitNo] = photo
        self.SetActivePortrait(portraitNo)

    @telemetry.ZONE_METHOD
    def ClearFacePortrait(self, *args):
        self.facePortraits = [None] * ccConst.NUM_PORTRAITS
        self.ClearPortraitInfo()
        self.activePortraitIndex = 0
        self.activePortrait = None
        return

    @telemetry.ZONE_METHOD
    def SelectRace(self, raceID, check=1):
        if self.raceID != raceID:
            oldRaceID = self.raceID
            if check and oldRaceID is not None and ccConst.BLOODLINESTEP in self.stepsUsed:
                if self.stepID == ccConst.CUSTOMIZATIONSTEP:
                    dnaLog = self.GetDollDNAHistory()
                    if dnaLog and len(dnaLog) > 1:
                        if eve.Message('CharCreationLoseChangesRace', {}, uiconst.YESNO) != uiconst.ID_YES:
                            return
            self.ClearSteps(what='race')
            self.ResetClothesStorage()
            self.raceID = raceID
            self.SelectBloodline(None, check=check)
            if hasattr(self.sr.step, 'OnRaceSelected'):
                self.sr.step.OnRaceSelected(raceID)
            self.UpdateBackdrop()
        raceMap = {const.raceCaldari: 'caldari',
         const.raceAmarr: 'amarr',
         const.raceMinmatar: 'minmatar',
         const.raceGallente: 'gallente'}
        raceAsString = raceMap.get(raceID, None)
        if raceAsString:
            everesourceprefetch.ScheduleFront('interior_' + raceAsString)
            everesourceprefetch.ScheduleFront('bloodline_select_' + raceAsString)
        return

    @telemetry.ZONE_METHOD
    def SelectBloodline(self, bloodlineID, check=1):
        if self.bloodlineID != bloodlineID:
            oldBloodlineID = self.bloodlineID
            if check and oldBloodlineID is not None and ccConst.CUSTOMIZATIONSTEP in self.stepsUsed:
                if self.stepID == ccConst.CUSTOMIZATIONSTEP:
                    dnaLog = self.GetDollDNAHistory()
                    if dnaLog and len(dnaLog) > 1:
                        if eve.Message('CharCreationLoseChangeBloodline', {}, uiconst.YESNO) != uiconst.ID_YES:
                            return
            self.ClearSteps(what='bloodline')
            self.ResetClothesStorage()
            self.bloodlineID = bloodlineID
            if hasattr(self.sr.step, 'OnBloodlineSelected'):
                self.sr.step.OnBloodlineSelected(bloodlineID, oldBloodlineID)
            if self.bloodlineSelector is not None:
                self.bloodlineSelector.SelectBloodline(bloodlineID)
        return

    @telemetry.ZONE_METHOD
    def SelectGender(self, genderID, check=1):
        if not self.CanChangeGender():
            return
        else:
            if check and self.genderID not in [None, genderID] and ccConst.CUSTOMIZATIONSTEP in self.stepsUsed:
                if self.stepID == ccConst.CUSTOMIZATIONSTEP:
                    dnaLog = self.GetDollDNAHistory()
                    if dnaLog and len(dnaLog) > 1:
                        if eve.Message('CharCreationLoseChangeGender', {}, uiconst.YESNO) != uiconst.ID_YES:
                            return
            self.genderID = genderID
            self.ClearSteps(what='gender')
            self.ResetClothesStorage()
            if hasattr(self.sr.step, 'OnGenderSelected'):
                self.sr.step.OnGenderSelected(genderID)
            if getattr(self.sr.step.sr, 'historySlider'):
                self.sr.step.sr.historySlider.LoadHistory(0)
            return

    @telemetry.ZONE_METHOD
    def SelectAncestry(self, ancestryID):
        self.finalStepLogger.SetAncestry(ancestryID)
        self.ancestryID = ancestryID
        if hasattr(self.sr.step, 'OnAncestrySelected'):
            self.sr.step.OnAncestrySelected(ancestryID)

    @telemetry.ZONE_METHOD
    def SelectSchool(self, schoolID):
        self.finalStepLogger.SetSchool(schoolID)
        self.schoolID = schoolID
        if hasattr(self.sr.step, 'OnSchoolSelected'):
            self.sr.step.OnSchoolSelected(schoolID)

    @telemetry.ZONE_METHOD
    def OnDollUpdated(self, charID, redundantUpdate, fromWhere, *args):
        if fromWhere in ('AddCharacter', 'OnSetDevice'):
            return
        self.ClearSteps(what='dollUpdated')

    @telemetry.ZONE_METHOD
    def IsSlowMachine(self):
        if gfxsettings.Get(gfxsettings.GFX_CHAR_FAST_CHARACTER_CREATION):
            return True
        if gfxsettings.Get(gfxsettings.GFX_SHADER_QUALITY) < 2:
            return True
        return False

    @telemetry.ZONE_METHOD
    def OnGraphicSettingsChanged(self, changes):
        if gfxsettings.GFX_CHAR_FAST_CHARACTER_CREATION in changes:
            if eve.Message('CustomQuestion', {'header': localization.GetByLabel('UI/CharacterCreation/LoseChangesHeader'),
             'question': localization.GetByLabel('UI/CharacterCreation/LoseChanges')}, uiconst.YESNO) == uiconst.ID_YES:
                self.avatarScene = None
                self.SwitchStep(self.availableSteps[0])
            else:
                gfxsettings.Set(gfxsettings.GFX_CHAR_FAST_CHARACTER_CREATION, 0, pending=False)
        elif self.stepID == ccConst.BLOODLINESTEP:
            self.SwitchStep(self.stepID)
        if gfxsettings.UI_NCC_GREEN_SCREEN in changes:
            self.UpdateBackdrop()
            if self.floor:
                self.floor.display = not gfxsettings.Get(gfxsettings.UI_NCC_GREEN_SCREEN)
        return

    @telemetry.ZONE_METHOD
    def TearDown(self):
        self.Cleanup()
        self.characterSvc.TearDown()
        if paperDoll.SkinSpotLightShadows.instance is not None:
            paperDoll.SkinSpotLightShadows.instance.Clear(killThread=True)
            paperDoll.SkinSpotLightShadows.instance = None
        self.floor = None
        self.doll = None
        self.minimalDoll = None
        self.scene = None
        self.avatarScene = None
        self.ClearCamera()
        self.cameraUpdateJob = None
        if self.bloodlineSelector is not None:
            self.bloodlineSelector.TearDown()
        self.bloodlineSelector = None
        self.animateToStoredPortraitThread = None
        self.animatingToPortraitID = None
        self.freezingAnimation = False
        self.colorCodedBackDrop = None
        return

    @telemetry.ZONE_METHOD
    def StartRaceStep(self):
        if not sm.GetService('cc').GetCharactersToSelect():
            self.sr.backBtn.state = uiconst.UI_HIDDEN
        sm.GetService('dynamicMusic').UpdateDynamicMusic()
        self.sr.step = RaceStep(parent=self.sr.mainCont)
        sceneManager = sm.GetService('sceneManager')
        sceneManager.Show2DBackdropScene()
        self.SetupScene(ccConst.SCENE_PATH_RACE_SELECTION)
        self.camera = cameras.CharCreationCamera(None)
        self.camera.fieldOfView = 0.5
        self.camera.distance = 7.0
        self.camera.SetPointOfInterest((0.0, 1.3, 0.0))
        self.camera.frontClip = 3.5
        self.camera.backclip = 100.0
        self.SetupCameraUpdateJob()
        self.camera.ToggleMode(ccConst.CAMERA_MODE_DEFAULT, avatar=None)
        paperDoll.SkinSpotLightShadows.SetupForCharacterCreator(self.scene)
        return

    @telemetry.ZONE_METHOD
    def StartBloodlineStep(self):
        self.sr.step = CharacterBloodlineSelection(parent=self.sr.mainCont)
        sceneManager = sm.GetService('sceneManager')
        sceneManager.Show2DBackdropScene()
        self.SetupScene(ccConst.SCENE_PATH_RACE_SELECTION)
        self.bloodlineSelector = ccUtil.BloodlineSelector(self.scene)
        if self.raceID and self.bloodlineSelector:
            self.bloodlineSelector.LoadRace(self.raceID, callBack=self.sr.step.MakeUI)
        self.camera = cameras.CharCreationCamera(None)
        self.camera.fieldOfView = 0.5
        self.camera.distance = 7.0
        self.camera.SetPointOfInterest((0.0, 1.3, 0.0))
        self.camera.frontClip = 3.5
        self.camera.backclip = 100.0
        self.CorrectBloodlinePlacement()
        self.SetupCameraUpdateJob()
        paperDoll.SkinSpotLightShadows.SetupForCharacterCreator(self.scene)
        info = self.GetInfo()
        if info.bloodlineID is not None:
            self.bloodlineSelector.SelectBloodline(info.bloodlineID)
        return

    @telemetry.ZONE_METHOD
    def CorrectBloodlinePlacement(self):
        aspect = trinity.device.viewport.GetAspectRatio()
        newDistance = 9.31 / aspect
        newDistance = max(7.0, newDistance)
        self.camera.distance = newDistance
        newHeight = 1.729 / aspect
        newHeight = max(1.3, newHeight)
        self.camera.SetPointOfInterest((0, newHeight, 0))

    @telemetry.ZONE_METHOD
    def SetAvatarScene(self, skipAddCharacter=False):
        info = self.GetInfo()
        if self.avatarScene is None:
            self.SetupScene(ccConst.SCENE_PATH_CUSTOMIZATION)
            self.avatarScene = self.scene
            if not skipAddCharacter:
                self.AddCharacter(info.charID, info.bloodlineID, info.genderID, dna=info.dna)
            self.floor = trinity.Load(ccConst.CUSTOMIZATION_FLOOR)
            self.scene.dynamics.append(self.floor)
        else:
            self.scene = self.avatarScene
        sceneManager = sm.GetService('sceneManager')
        sceneManager.SetActiveScene(self.scene, sceneKey='characterCreation')
        return

    @telemetry.ZONE_METHOD
    def StartCustomizationStep(self, *args):
        info = self.GetInfo()
        sm.GetService('dynamicMusic').UpdateDynamicMusic()
        sceneManager = sm.GetService('sceneManager')
        sceneManager.Show2DBackdropScene()
        self.SetAvatarScene()
        avatar = self.characterSvc.GetSingleCharactersAvatar(info.charID)
        if avatar is not None:
            avatar.animationUpdater.network.SetControlParameter('ControlParameters|NetworkMode', 1)
            self.camera = cameras.CharCreationCamera(avatar, ccConst.CAMERA_MODE_FACE)
            self.camera.frontClip = 0.1
            self.camera.backclip = 100.0
            self.SetupCameraUpdateJob()
            self.camera.SetMoveCallback(self.CameraMoveCB)
        self.SetDefaultLighting()
        self.sr.step = CharacterCustomization(parent=self.sr.mainCont)
        if self.CanChangeBaseAppearance():
            self.StartEditMode(showPreview=True, callback=self.sr.step.ChangeSculptingCursor)
        self.camera.ToggleMode(ccConst.CAMERA_MODE_FACE, avatar=avatar, transformTime=500.0)
        if not sm.StartService('device').SupportsSM3():
            self.RemoveBodyModifications()
        paperDoll.SkinSpotLightShadows.SetupForCharacterCreator(self.scene)
        return

    def CameraMoveCB(self, viewMatrix):
        info = self.GetInfo()
        if info.charID not in self.characterSvc.characters:
            return
        if not len(self.characterSvc.characters):
            return
        avatar = self.characterSvc.GetSingleCharactersAvatar(info.charID)
        matrix = geo2.MatrixInverse(viewMatrix.transform)
        view = matrix[3][:3]
        joint = avatar.GetBoneIndex('Head')
        if joint == 4294967295L:
            return
        head = avatar.GetBonePosition(joint)
        rot = avatar.rotation
        vec = (view[0] - head[0], view[1] - head[1], view[2] - head[2])
        vecLength = geo2.Vec3Distance((0, 0, 0), vec)
        vec = geo2.QuaternionTransformVector(geo2.QuaternionInverse(rot), vec)
        norm = 1.0 / math.sqrt(vec[0] * vec[0] + vec[1] * vec[1] + vec[2] * vec[2])
        vec = (vec[0] * norm, vec[1] * norm, vec[2] * norm)
        leftright = math.atan2(vec[2], vec[0])
        updown = math.asin(vec[1])
        leftright = 1 - abs(leftright) / 3.1415927 * 2
        updown = 2 * updown / 3.1415927
        dist = (vecLength - 1.0) / 7.0
        network = avatar.animationUpdater.network
        network.SetControlParameter('ControlParameters|HeadLookLeftRight', leftright)
        network.SetControlParameter('ControlParameters|HeadLookUpDown', updown)
        network.SetControlParameter('ControlParameters|CameraDistance', dist)

    @telemetry.ZONE_METHOD
    def FetchOldPortraitData(self, charID):
        PREFIX = 'ControlParameters|'
        cache = self.characterSvc.GetCachedPortraitInfo(charID)
        if cache is not None:
            self.lightingID = cache.lightID
            self.lightColorID = cache.lightColorID
            self.lightIntensity = cache.lightIntensity
            path = self.GetBackgroundPathFromID(cache.backgroundID)
            if path in ccConst.backgroundOptions:
                self.backdropPath = path
            self.poseID = cache.poseData['PortraitPoseNumber']
            self.cameraPos = cache.cameraPosition
            self.cameraPoi = cache.cameraPoi
            self.cameraFov = cache.cameraFieldOfView
            params = []
            for key in cache.poseData:
                params.append((PREFIX + key, cache.poseData[key]))

            if len(params):
                self.characterSvc.SetControlParametersFromList(params, charID)
        else:
            portraitData = sm.GetService('cc').GetPortraitData(charID)
            if portraitData is not None:
                self.lightingID = portraitData.lightID
                self.lightColorID = portraitData.lightColorID
                self.lightIntensity = portraitData.lightIntensity
                path = self.GetBackgroundPathFromID(portraitData.backgroundID)
                if path in ccConst.backgroundOptions:
                    self.backdropPath = path
                self.poseID = portraitData.portraitPoseNumber
                self.cameraPos = (portraitData.cameraX, portraitData.cameraY, portraitData.cameraZ)
                self.cameraPoi = (portraitData.cameraPoiX, portraitData.cameraPoiY, portraitData.cameraPoiZ)
                self.cameraFov = portraitData.cameraFieldOfView
                params = self.GetControlParametersFromPoseData(portraitData, fromDB=True).values()
                self.characterSvc.SetControlParametersFromList(params, charID)
        self.alreadyLoadedOldPortraitData = True
        return

    @telemetry.ZONE_METHOD
    def StartPortraitStep(self):
        info = self.GetInfo()
        if not getattr(self, 'alreadyLoadedOldPortraitData', False):
            if self.modeObject.GetOldPortraitData():
                self.FetchOldPortraitData(info.charID)
        self.sr.step = CharacterPortrait(parent=self.sr.mainCont)
        self.SetAvatarScene()
        avatar = self.characterSvc.GetSingleCharactersAvatar(info.charID)
        if avatar is not None and avatar.animationUpdater is not None:
            avatar.animationUpdater.network.SetControlParameter('ControlParameters|NetworkMode', 2)
        if self.camera is None:
            self.camera = cameras.CharCreationCamera(avatar, ccConst.CAMERA_MODE_PORTRAIT)
            self.SetupCameraUpdateJob()
        else:
            self.camera.ToggleMode(ccConst.CAMERA_MODE_PORTRAIT, avatar=avatar, transformTime=500.0)
        if hasattr(self, 'cameraPos'):
            self.camera.PlacePortraitCamera(self.cameraPos, self.cameraPoi)
            xFactor, yFactor = self.camera.GetCorrectCameraXandYFactors(self.cameraPos, self.cameraPoi)
            self.camera.xFactor = self.camera.xTarget = xFactor
            self.camera.yFactor = self.camera.yTarget = yFactor
        if hasattr(self, 'storedPortraitCameraSettings'):
            self.camera.SetPointOfInterest(self.storedPortraitCameraSettings['poi'])
            self.camera.pitch = self.storedPortraitCameraSettings['pitch']
            self.camera.yaw = self.storedPortraitCameraSettings['yaw']
            self.camera.distance = self.storedPortraitCameraSettings['distance']
            self.camera.xFactor = self.storedPortraitCameraSettings['xFactor']
            self.camera.yFactor = self.storedPortraitCameraSettings['yFactor']
            self.camera.fieldOfView = self.storedPortraitCameraSettings['fieldOfView']
        self.UpdateLights()
        paperDoll.SkinSpotLightShadows.SetupForCharacterCreator(self.scene)
        self.characterSvc.StartPosing(charID=info.charID, callback=self.sr.step.ChangeSculptingCursor)
        return

    @telemetry.ZONE_METHOD
    def StartNamingStep(self, *args):
        self.sr.step = CharacterNaming(parent=self.sr.mainCont)
        info = self.GetInfo()
        self.SetAvatarScene()
        avatar = self.characterSvc.GetSingleCharactersAvatar(info.charID)
        if avatar is not None:
            if info.charID in self.characterSvc.characters:
                avatar.animationUpdater.network.SetControlParameter('ControlParameters|NetworkMode', 1)
        self.camera = cameras.CharCreationCamera(avatar=avatar)
        self.camera.fieldOfView = 0.3
        self.camera.distance = 8.0
        self.camera.frontClip = 3.5
        self.camera.backclip = 100.0
        self.SetupCameraUpdateJob()
        self.camera.SetPointOfInterest((0.0, self.camera.avatarEyeHeight / 2.0, 0.0))
        self.SetDefaultLighting()
        paperDoll.SkinSpotLightShadows.SetupForCharacterCreator(self.scene)
        return

    def StartMinimalNamingStep(self):
        from eve.client.script.ui.login.charcreation.steps.characterNamingMinimal import CharacterNamingMinimal
        self.sr.step = CharacterNamingMinimal(parent=self.sr.mainCont)
        info = self.GetInfo()
        self.SetAvatarScene(skipAddCharacter=True)
        loader = BloodlineDollLoader()
        doll = loader.GetClothedDoll(info.raceID, info.bloodlineID, info.genderID, scene=self.scene)
        self.minimalDoll = doll
        self.ApplyGraphicsSettingsToDoll(doll)
        avatar = doll.avatar
        if avatar is not None:
            avatar.animationUpdater.network.SetControlParameter('ControlParameters|NetworkMode', 1)
        self.camera = cameras.CharCreationCamera(avatar=avatar, modeName=ccConst.CAMERA_MODE_FACE)
        self.SetupCameraUpdateJob()
        self.SetDefaultLighting()
        paperDoll.SkinSpotLightShadows.SetupForCharacterCreator(self.scene)
        self.GenerateAndSetPortrait()
        return

    @telemetry.ZONE_METHOD
    def ClearSteps(self, what=None, force=0, *args):
        stepAlreadyCleared = getattr(self.sr.step, 'stepAlreadyCleared', 0)
        if not force and stepAlreadyCleared or not getattr(self.sr.mainNav, 'ResetToStep', None):
            return
        else:
            currentStepID = self.stepID
            if currentStepID <= ccConst.NAMINGSTEP:
                pass
            if currentStepID <= ccConst.MINIMALNAMINGSTEP:
                self.minimalDoll = None
            if currentStepID <= ccConst.PORTRAITSTEP:
                pass
            if currentStepID <= ccConst.CUSTOMIZATIONSTEP:
                self.ClearFacePortrait()
                self.ClearPortraitInfo()
                self.schoolID = None
                self.ancestryID = None
                if what in ('bloodline', 'race'):
                    self.ancestryID = None
                    self.schoolID = None
            if currentStepID <= ccConst.BLOODLINESTEP:
                self.avatarScene = None
                self.characterSvc.TearDown()
                self.ancestryID = None
                self.schoolID = None
            if currentStepID <= ccConst.RACESTEP:
                self.TearDown()
            self.stepsUsed = set(range(1, currentStepID)) or set([self.availableSteps[0]])
            self.sr.mainNav.ResetToStep(currentStepID, stepsUsed=self.stepsUsed)
            if self.sr.step:
                self.sr.step.stepAlreadyCleared = 1
            return

    @telemetry.ZONE_METHOD
    def Cleanup(self):
        self.characterSvc.StopEditing()
        info = self.GetInfo()
        charID = info.charID
        if charID in self.characterSvc.characters:
            self.characterSvc.StopPosing(charID)
        self.bloodlineSelector = None
        self.scene = None
        self.ClearCamera()
        sceneManager = sm.GetService('sceneManager')
        sceneManager.UnregisterScene('characterCreation')
        return

    @telemetry.ZONE_METHOD
    def SetupScene(self, path):
        scene = trinity.Load(path)
        blue.resMan.Wait()
        if self.IsSlowMachine():
            if hasattr(scene, 'shadowCubeMap'):
                scene.shadowCubeMap.enabled = False
            if hasattr(scene, 'ssao') and hasattr(scene.ssao, 'enable'):
                scene.ssao.enable = False
            if hasattr(scene, 'ambientColor'):
                scene.ambientColor = (0.25, 0.25, 0.25)
        elif scene:
            if hasattr(scene, 'shadowCubeMap'):
                scene.shadowCubeMap.enabled = False
        self.scene = scene
        if hasattr(scene, 'apexScene') and scene.apexScene is not None:
            scene.apexScene.CreatePlane((0, 0, 0), (0, 1, 0), 0)
        sceneManager = sm.GetService('sceneManager')
        sceneManager.RegisterScene(scene, 'characterCreation')
        sceneManager.SetRegisteredScenes('characterCreation')
        return

    @telemetry.ZONE_METHOD
    def ReduceLights(self):
        scene = self.scene
        if hasattr(scene, 'lights'):
            lightsToRemove = []
            for each in scene.lights:
                if each.name != 'FrontMain':
                    lightsToRemove.append(each)

            for each in lightsToRemove:
                scene.lights.remove(each)

            if len(scene.lights) > 0:
                if hasattr(scene.lights[0], 'color'):
                    scene.lights[0].color = (0.886, 0.98, 1.0)

    def ApplyGraphicsSettingsToDoll(self, doll):
        doll.overrideLod = paperDoll.LOD_SKIN
        textureQuality = gfxsettings.Get(gfxsettings.GFX_CHAR_TEXTURE_QUALITY)
        doll.textureResolution = ccConst.TEXTURE_RESOLUTIONS[textureQuality]
        if self.IsSlowMachine():
            doll.useFastShader = True
        else:
            doll.useFastShader = False

    @telemetry.ZONE_METHOD
    def AddCharacter(self, charID, bloodlineID, genderID, scene=None, dna=None, validateColors=True):
        self.ResetDna()
        self.characterSvc.AddCharacterToScene(charID, scene or self.scene, ccUtil.GenderIDToPaperDollGender(genderID), dna=dna, bloodlineID=bloodlineID, updateDoll=False)
        self.doll = self.characterSvc.GetSingleCharactersDoll(charID)
        while self.doll.IsBusyUpdating():
            blue.synchro.Yield()

        self.ApplyGraphicsSettingsToDoll(self.doll)
        self.characterSvc.SetDollBloodline(charID, bloodlineID)
        if validateColors:
            for categoryName in ccConst.COLORMAPPING.keys():
                self.UpdateColorSelectionFromDoll(categoryName)
                self.ValidateColors(categoryName)

        self.StartDnaLogging()
        self.characterSvc.UpdateDoll(charID, fromWhere='AddCharacter')

    @telemetry.ZONE_METHOD
    def GetAvailableStyles(self, modifier):
        info = self.GetInfo()
        gender = info.genderID
        bloodline = info.bloodlineID
        currentModifier = self.characterSvc.GetModifierByCategory(info.charID, modifier)
        itemTypes = self.characterSvc.GetAvailableTypesByCategory(modifier, gender, bloodline)
        activeIndex = None
        if currentModifier:
            currentType = currentModifier.GetTypeData()
            for i, each in enumerate(itemTypes):
                if each[1][0] == currentType[0] and each[1][1] == currentType[1] and each[1][2] == currentType[2]:
                    activeIndex = i

        return (itemTypes, activeIndex)

    def GetModifierIntensity(self, modifierPath):
        info = self.GetInfo()
        modifier = self.characterSvc.GetModifiersByCategory(info.charID, modifierPath)
        if modifier:
            return modifier[0].weight

    @telemetry.ZONE_METHOD
    def GetAvailableColors(self, modifier):
        info = self.GetInfo()
        colors, activeColorIndex = self.characterSvc.GetCharacterColorVariations(info.charID, modifier)
        colors = tuple(colors)
        retColors = []
        for name, color in colors:
            if color and type(color[0]) == types.TupleType:
                r = g = b = 0
                for _r, _g, _b, _a in color:
                    r += _r
                    g += _g
                    b += _b

                r = r / float(len(color))
                g = g / float(len(color))
                b = b / float(len(color))
                retColors.append((name, (r,
                  g,
                  b,
                  1.0), color))
            else:
                retColors.append((name, color, color))

        return (retColors, activeColorIndex)

    @telemetry.ZONE_METHOD
    def SetColorValue(self, modifier, primaryColor, secondaryColor=None, doUpdate=True, ignoreValidate=False):
        self._setColorsByCategory[modifier] = (primaryColor, secondaryColor)
        info = self.GetInfo()
        self.characterSvc.SetColorValueByCategory(info.charID, modifier, primaryColor, secondaryColor, doUpdate=False)
        if ccUtil.HasUserDefinedSpecularity(modifier):
            specValue = self._setSpecularityByCategory.setdefault(modifier, 0.5)
            self.SetColorSpecularity(modifier, specValue, doUpdate=False)
        if ccUtil.HasUserDefinedWeight(modifier):
            defaultIntensity = ccConst.defaultIntensity.get(modifier, 0.5)
            intensityValue = self._setIntensityByCategory.setdefault(modifier, defaultIntensity)
            self.SetIntensity(modifier, intensityValue, doUpdate=False)
        if not ignoreValidate:
            self.ValidateColors(modifier)
        if doUpdate:
            self.characterSvc.UpdateDoll(info.charID, fromWhere='SetColorValue')

    def GetSpecularityByCategory(self, category):
        return self._setSpecularityByCategory.get(category, 0.5)

    def GetIntensityByCategory(self, category):
        return self._setIntensityByCategory.get(category, 0.5)

    @telemetry.ZONE_METHOD
    def SetRandomColorSpecularity(self, modifier, doUpdate=True):
        self.SetColorSpecularity(modifier, random.random(), doUpdate=doUpdate)

    @telemetry.ZONE_METHOD
    def SetColorSpecularity(self, modifier, specularity, doUpdate=True):
        self._setSpecularityByCategory[modifier] = specularity
        info = self.GetInfo()
        self.characterSvc.SetColorSpecularityByCategory(info.charID, modifier, specularity, doUpdate=doUpdate)

    @telemetry.ZONE_METHOD
    def SetRandomHairDarkness(self, doUpdate=True):
        self.SetHairDarkness(random.random(), doUpdate=doUpdate)

    @telemetry.ZONE_METHOD
    def SetHairDarkness(self, darkness, doUpdate=True):
        info = self.GetInfo()
        self.characterSvc.SetHairDarkness(info.charID, darkness)
        if doUpdate:
            sm.GetService('character').UpdateDoll(info.charID, fromWhere='SetHairDarkness')

    @telemetry.ZONE_METHOD
    def SetRandomIntensity(self, modifier, doUpdate=True):
        self.SetIntensity(modifier, random.random(), doUpdate=doUpdate)

    @telemetry.ZONE_METHOD
    def SetIntensity(self, modifier, value, doUpdate=True):
        info = self.GetInfo()
        if modifier == ccConst.muscle:
            self.characterSvc.SetCharacterMuscularity(info.charID, value, doUpdate=doUpdate)
        elif modifier == ccConst.weight:
            self.characterSvc.SetCharacterWeight(info.charID, value, doUpdate=doUpdate)
        else:
            self._setIntensityByCategory[modifier] = value
            self.characterSvc.SetWeightByCategory(info.charID, modifier, value, doUpdate=doUpdate)

    @telemetry.ZONE_METHOD
    def SetItemType(self, itemType, weight=1.0, doUpdate=True):
        info = self.GetInfo()
        category = self.characterSvc.GetCategoryFromResPath(itemType[1][0])
        if category in CLOTHING_ITEMS:
            if category in self.clothesStorage:
                self.clothesStorage.pop(category)
            self.ToggleClothes(forcedValue=0, doUpdate=False)
        self.characterSvc.ApplyTypeToDoll(info.charID, itemType, weight=weight, doUpdate=False)
        if category in self._setColorsByCategory:
            var1, var2 = self._setColorsByCategory[category]
            self.SetColorValue(category, var1, var2, doUpdate=False)
        self.ValidateColors(category)
        if doUpdate:
            self.characterSvc.UpdateDoll(info.charID, fromWhere='SetItemType')

    @telemetry.ZONE_METHOD
    def SetStyle(self, category, style, variation=None, doUpdate=True):
        info = self.GetInfo()
        if style or variation or category in CLOTHING_ITEMS:
            self.ToggleClothes(forcedValue=0, doUpdate=False)
        self.characterSvc.ApplyItemToDoll(info.charID, category, style, removeFirst=True, variation=variation, doUpdate=False)
        if style:
            if category in self._setColorsByCategory:
                var1, var2 = self._setColorsByCategory[category]
                self.SetColorValue(category, var1, var2, doUpdate=False)
            self.ValidateColors(category)
        if doUpdate:
            self.characterSvc.UpdateDoll(info.charID, fromWhere='SetStyle')

    @telemetry.ZONE_METHOD
    def ValidateColors(self, category):
        if category not in ccConst.COLORMAPPING:
            return
        else:
            info = self.GetInfo()
            categoryColors = self.characterSvc.GetAvailableColorsForCategory(category, info.genderID, info.bloodlineID)
            if not categoryColors:
                return
            primary, secondary = categoryColors
            hasValidColor = False
            modifier = self.characterSvc.GetModifiersByCategory(info.charID, category)
            if modifier:
                currentColor = modifier[0].GetColorizeData()
                if secondary:
                    if modifier[0].metaData.numColorAreas > 1:
                        for primaryColorTuple in primary:
                            primaryColorName, primaryDisplayColor, primaryColorValue = primaryColorTuple
                            pA, pB, pC = primaryColorValue['colors']
                            for secondaryColorTuple in secondary:
                                secondaryColorName, secondaryDisplayColor, secondaryColorValue = secondaryColorTuple
                                srA, srB, srC = secondaryColorValue['colors']
                                if pA == currentColor[0] and srB == currentColor[1] and srC == currentColor[2]:
                                    hasValidColor = True
                                    if category not in self._setColorsByCategory or self._setColorsByCategory[category][1] == None:
                                        self.SetColorValue(category, primaryColorTuple, secondaryColorTuple, doUpdate=False, ignoreValidate=True)
                                    break

                            if hasValidColor:
                                break

                        if not hasValidColor:
                            for primaryColorTuple in primary:
                                primaryColorName, primaryDisplayColor, primaryColorValue = primaryColorTuple
                                if primaryColorValue['colors'] == currentColor:
                                    hasValidColor = True
                                    self.SetColorValue(category, primaryColorTuple, secondary[0], doUpdate=False, ignoreValidate=True)
                                    break

                    else:
                        for primaryColorTuple in primary:
                            primaryColorName, primaryDisplayColor, primaryColorValue = primaryColorTuple
                            if primaryColorValue['colors'] == currentColor:
                                hasValidColor = True
                                if category not in self._setColorsByCategory:
                                    self.SetColorValue(category, primaryColorTuple, None, doUpdate=False, ignoreValidate=True)
                                break
                        else:
                            if category in self._setColorsByCategory:
                                hasValidColor = True
                else:
                    for primaryColorTuple in primary:
                        primaryColorName, primaryDisplayColor, primaryColorValue = primaryColorTuple
                        if primaryColorValue['colors'] == currentColor:
                            hasValidColor = True
                            if category not in self._setColorsByCategory:
                                self.SetColorValue(category, primaryColorTuple, None, doUpdate=False, ignoreValidate=True)
                            break

                if not hasValidColor and primary:
                    if secondary:
                        var2 = secondary[0]
                    else:
                        var2 = None
                    self.SetColorValue(category, primary[0], var2, doUpdate=False, ignoreValidate=True)
            return

    def UpdateColorSelectionFromDoll(self, category):
        if category not in ccConst.COLORMAPPING:
            return
        else:
            info = self.GetInfo()
            categoryColors = self.characterSvc.GetAvailableColorsForCategory(category, info.genderID, info.bloodlineID)
            if not categoryColors:
                return
            primary, secondary = categoryColors
            modifier = self.characterSvc.GetModifiersByCategory(info.charID, category)
            if modifier:
                corPrimary = None
                corSecondary = None
                try:
                    chosenPrimary, chosenSecondary = self.characterSvc.GetSingleCharactersMetadata(info.charID).typeColors[category]
                    for primaryColorTuple in primary:
                        if primaryColorTuple[0] == chosenPrimary:
                            corPrimary = primaryColorTuple
                            break

                    if secondary and chosenSecondary:
                        for secondaryColorTuple in secondary:
                            if secondaryColorTuple[0] == chosenSecondary:
                                corSecondary = secondaryColorTuple
                                break

                except KeyError:
                    log.LogWarn('KeyError when getting Metadata for a single character in characterCreationLayer.UpdateColorSelectionFromDoll', info.charID, category)

                if corPrimary is not None:
                    self._setColorsByCategory[category] = (corPrimary, corSecondary)
                if category in self.characterSvc.characterMetadata[info.charID].typeWeights:
                    self._setIntensityByCategory[category] = self.characterSvc.characterMetadata[info.charID].typeWeights[category]
                if category in self.characterSvc.characterMetadata[info.charID].typeSpecularity:
                    self._setSpecularityByCategory[category] = self.characterSvc.characterMetadata[info.charID].typeSpecularity[category]
            return

    @telemetry.ZONE_METHOD
    def ClearCategory(self, category, doUpdate=True):
        self.SetStyle(category, style=None, doUpdate=doUpdate)
        return

    @telemetry.ZONE_METHOD
    def CheckDnaLog(self, trigger=None):
        if self.sr.step and self.sr.step.sr.historySlider:
            currentIndex, maxIndex = self.sr.step.sr.historySlider.GetCurrentIndexAndMaxIndex()
            if currentIndex != maxIndex:
                self.ClearDnaLogFromIndex(currentIndex)

    @telemetry.ZONE_METHOD
    def ClearCamera(self):
        if self.camera is not None:
            for priority, behavior in self.camera.cameraBehaviors:
                behavior.camera = None

            del self.camera.cameraBehaviors[:]
            self.camera.avatar = None
            self.camera = None
        return

    @telemetry.ZONE_METHOD
    def SetDefaultLighting(self):
        self.SetLightScene('res:/Graphics/Character/Global/PaperdollSettings/LightSettings/Normal.red')
        if self.IsSlowMachine():
            self.ReduceLights()

    @telemetry.ZONE_METHOD
    def SetupCameraUpdateJob(self):
        sceneManager = sm.GetService('sceneManager')
        sceneManager.RefreshJob(self.camera)
        if self.cameraUpdateJob is None:
            self.cameraUpdateJob = trinity.renderJob.CreateRenderJob('cameraUpdate')
            r = trinity.TriStepPythonCB()
            r.SetCallback(self.UpdateCamera)
            self.cameraUpdateJob.steps.append(r)
        sceneManager.characterRenderJob.SetCameraUpdate(self.cameraUpdateJob)
        return

    @telemetry.ZONE_METHOD
    def UpdateCamera(self):
        if self.camera is not None:
            self.camera.Update()
        return

    @telemetry.ZONE_METHOD
    def PickObjectUV(self, pos):
        return self.scene.PickObjectUV(pos[0], pos[1], self.camera.projectionMatrix, self.camera.viewMatrix, trinity.device.viewport)

    @telemetry.ZONE_METHOD
    def PickObjectAndArea(self, pos):
        return self.scene.PickObjectAndArea(pos[0], pos[1], self.camera.projectionMatrix, self.camera.viewMatrix, trinity.device.viewport)

    @telemetry.ZONE_METHOD
    def PickObject(self, pos):
        return self.scene.PickObject(pos[0], pos[1], self.camera.projectionMatrix, self.camera.viewMatrix, trinity.device.viewport)

    @telemetry.ZONE_METHOD
    def SaveCurrentCharacter(self, charactername, bloodlineID, genderID, portraitID):
        total = 3
        sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/CharacterCreation/Registering'), localization.GetByLabel('UI/CharacterCreation/CompilePrefs'), 1, total)
        try:
            try:
                if self.portraitInfo[portraitID] is None:
                    raise UserError('CharCreationNoPortrait')
                info = self.GetInfo()
                charInfo = self.characterSvc.GetCharacterAppearanceInfo(info.charID)
                charID = sm.GetService('cc').CreateCharacterWithDoll(charactername, bloodlineID, genderID, info.ancestryID, charInfo, self.portraitInfo[portraitID], info.schoolID)
                sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/CharacterCreation/Registering'), localization.GetByLabel('UI/CharacterCreation/InsertingRecord'), 2, total)
                sm.GetService('photo').AddPortrait(self.GetPortraitSnapshotPath(portraitID), charID)
                sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/CharacterCreation/Registering'), localization.GetByLabel('UI/Generic/Done'), 3, total)
                return charID
            except UserError as what:
                if not what.msg.startswith('CharNameInvalid'):
                    eve.Message(*what.args)
                    return
                sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/CharacterCreation/Registering'), localization.GetByLabel('UI/CharacterCreation/FailedForSomeReason'), 3, total)

        finally:
            self.sessionSounds = []

        return

    @telemetry.ZONE_METHOD
    def UpdateExistingCharacter(self, *args):
        portraitID = self.activePortraitIndex
        charID = self.charID
        if self.portraitInfo[portraitID] is None:
            raise UserError('CharCreationNoPortrait')
        dollExists = self.dna is not None
        dollInfo = self.characterSvc.GetCharacterAppearanceInfo(charID)
        availableTypeIDs = sm.GetService('cc').GetMyApparel()
        metadata = self.characterSvc.characterMetadata[charID]
        typesInUse = metadata.types
        for resourceID in typesInUse.itervalues():
            if resourceID:
                info = cfg.paperdollResources.Get(resourceID)
                if info.typeID is not None and info.typeID not in availableTypeIDs:
                    raise UserError('ItemNotAtStation', {'item': info.typeID})

        if self.mode == ccConst.MODE_FULL_RECUSTOMIZATION:
            sm.GetService('cc').UpdateExistingCharacterFull(charID, dollInfo, self.portraitInfo[portraitID], dollExists)
        elif self.mode == ccConst.MODE_LIMITED_RECUSTOMIZATION:
            sm.GetService('cc').UpdateExistingCharacterLimited(charID, dollInfo, self.portraitInfo[portraitID], dollExists)
        elif self.mode == ccConst.MODE_FULL_BLOODLINECHANGE:
            info = self.GetInfo()
            sm.GetService('cc').UpdateExistingCharacterBloodline(charID, dollInfo, self.portraitInfo[portraitID], dollExists, info.bloodlineID)
        sm.GetService('photo').AddPortrait(self.GetPortraitSnapshotPath(portraitID), charID)
        self.characterSvc.CachePortraitInfo(self.charID, self.portraitInfo[self.activePortraitIndex])
        if self.dollState != const.paperdollStateForceRecustomize:
            self.ExitToStation()
        else:
            uthread.pool('GameUI::ActivateView::charsel', sm.GetService('viewState').ActivateView, 'charsel')
        self.DoLogEvent(finished=1)
        return

    @telemetry.ZONE_METHOD
    def SetBackdrop(self, backdropPath):
        self.backdropPath = backdropPath

    @telemetry.ZONE_METHOD
    def SetPoseID(self, poseID):
        self.poseID = poseID

    @telemetry.ZONE_METHOD
    def SetLightScene(self, lightPath, scene=None):
        scene = scene or self.scene
        lightScene = trinity.Load(lightPath)
        if scene:
            lightList = []
            for l in scene.lights:
                lightList.append(l)

            for l in lightList:
                scene.RemoveLightSource(l)

            for l in lightScene.lights:
                scene.AddLightSource(l)

            if paperDoll.SkinSpotLightShadows.instance is not None:
                paperDoll.SkinSpotLightShadows.instance.RefreshLights()
        return

    @telemetry.ZONE_METHOD
    def SetLights(self, lightID):
        self.lightingID = lightID
        self.UpdateLights()

    @telemetry.ZONE_METHOD
    def GetLight(self):
        return self.lightingID

    @telemetry.ZONE_METHOD
    def SetLightColor(self, lightID):
        self.lightColorID = lightID
        self.UpdateLights()

    @telemetry.ZONE_METHOD
    def GetLightColor(self):
        return self.lightColorID

    @telemetry.ZONE_METHOD
    def SetLightsAndColor(self, lightID, colorID):
        self.lightingID = lightID
        self.lightColorID = colorID
        self.UpdateLights()

    @telemetry.ZONE_METHOD
    def SetLightIntensity(self, intensity):
        self.lightIntensity = intensity
        self.UpdateLights()

    @telemetry.ZONE_METHOD
    def GetLightIntensity(self):
        return self.lightIntensity

    @telemetry.ZONE_METHOD
    def UpdateLights(self):
        lightsPath = GetGraphicFile(self.lightingID)
        lightColorPath = GetGraphicFile(self.lightColorID)
        lightScene = trinity.Load(lightsPath)
        lightColorScene = trinity.Load(lightColorPath)
        ccUtil.SetupLighting(self.scene, lightScene, lightColorScene, self.lightIntensity)
        if self.IsSlowMachine():
            self.ReduceLights()

    @telemetry.ZONE_METHOD
    def GetBackdrop(self):
        return self.backdropPath

    @telemetry.ZONE_METHOD
    def GetPoseId(self):
        return getattr(self, 'poseID', 0)

    @telemetry.ZONE_METHOD
    def StartEditMode(self, callback=None, **kwds):
        if callback is None and kwds.get('mode', None) == 'sculpt':
            callback = getattr(self.sr.step, 'ChangeSculptingCursor', None)
        info = self.GetInfo()
        self.characterSvc.StartEditMode(info.charID, self.scene, self.camera, callback=callback, **kwds)
        return

    @telemetry.ZONE_METHOD
    def UpdateBackdropLite(self, raceID, mouseEnter=False, *args):
        bdScene = sm.GetService('sceneManager').Get2DBackdropScene()
        if not bdScene:
            return
        blue.resMan.SetUrgentResourceLoads(True)
        for each in bdScene.children:
            each.display = False
            if mouseEnter:
                if raceID:
                    if each.name == 'mouseoverSprite_%d' % raceID:
                        each.display = True
                else:
                    each.display = True
            elif each.name == 'backdropSprite':
                each.texturePrimary.resPath = 'res:/UI/Texture/CharacterCreation/bg/RACE_Background_%d.dds' % raceID
                each.display = True

        blue.resMan.SetUrgentResourceLoads(False)

    @telemetry.ZONE_METHOD
    def UpdateBackdrop(self, *args):
        bdScene = sm.GetService('sceneManager').Get2DBackdropScene()
        if not bdScene:
            return
        else:
            bdScene.clearBackground = True
            for each in bdScene.children[:]:
                bdScene.children.remove(each)

            for each in bdScene.curveSets[:]:
                bdScene.curveSets.remove(each)

            self.colorCodedBackDrop = None
            desktopWidth = int(uicore.desktop.width * uicore.desktop.dpiScaling)
            desktopHeight = int(uicore.desktop.height * uicore.desktop.dpiScaling)
            size = min(desktopHeight, desktopWidth)
            margin = -200
            info = self.GetInfo()
            if self.stepID == ccConst.RACESTEP:
                self.colorCodedBackDrop = blue.resMan.GetResource('res:/UI/Texture/CharacterCreation/bg/RACE_Background_Colorcoded.png', 'raw')
                bgSize = min(desktopWidth, desktopHeight) * 1.5
                backdropSprite = trinity.Tr2Sprite2d()
                backdropSprite.name = u'backdropSprite'
                backdropSprite.displayWidth = bgSize
                backdropSprite.displayHeight = bgSize
                backdropSprite.displayX = (desktopWidth - bgSize) / 2
                backdropSprite.displayY = (desktopHeight - bgSize) / 2
                backdropSprite.texturePrimary = trinity.Tr2Sprite2dTexture()
                backdropSprite.texturePrimary.resPath = 'res:/UI/Texture/CharacterCreation/bg/RACE_Background_START_None.dds'
                backdropSprite.display = True
                bdScene.children.append(backdropSprite)
                for race in [const.raceAmarr,
                 const.raceMinmatar,
                 const.raceCaldari,
                 const.raceGallente]:
                    mouseoverSprite = trinity.Tr2Sprite2d()
                    mouseoverSprite.name = u'mouseoverSprite_%d' % race
                    mouseoverSprite.displayWidth = bgSize
                    mouseoverSprite.displayHeight = bgSize
                    mouseoverSprite.displayX = (desktopWidth - bgSize) / 2
                    mouseoverSprite.displayY = (desktopHeight - bgSize) / 2
                    mouseoverSprite.texturePrimary = trinity.Tr2Sprite2dTexture()
                    mouseoverSprite.texturePrimary.resPath = 'res:/UI/Texture/CharacterCreation/bg/RACE_Background_START_%d.dds' % race
                    mouseoverSprite.display = False
                    bdScene.children.append(mouseoverSprite)

                if info.raceID:
                    self.UpdateBackdropLite(info.raceID)
            elif self.stepID == ccConst.BLOODLINESTEP:
                bgSize = max(desktopWidth, desktopHeight)
                backdropSprite = trinity.Tr2Sprite2d()
                backdropSprite.name = u'backdropSprite'
                backdropSprite.displayWidth = bgSize
                backdropSprite.displayHeight = bgSize
                backdropSprite.displayY = (desktopHeight - bgSize) / 2
                backdropSprite.displayX = (desktopWidth - bgSize) / 2
                backdropSprite.texturePrimary = trinity.Tr2Sprite2dTexture()
                backdropSprite.texturePrimary.resPath = 'res:/UI/Texture/CharacterCreation/bg/Bloodline_Background_%d.dds' % info.raceID
                backdropSprite.display = True
                bdScene.children.append(backdropSprite)
            else:
                if gfxsettings.Get(gfxsettings.UI_NCC_GREEN_SCREEN):
                    bgSize = max(desktopWidth, desktopHeight)
                    backdropSprite = trinity.Tr2Sprite2d()
                    backdropSprite.name = u'greenscreen'
                    backdropSprite.displayWidth = bgSize
                    backdropSprite.displayHeight = bgSize
                    backdropSprite.displayY = (desktopHeight - bgSize) / 2
                    backdropSprite.displayX = (desktopWidth - bgSize) / 2
                    backdropSprite.texturePrimary = trinity.Tr2Sprite2dTexture()
                    backdropSprite.texturePrimary.resPath = 'res:/UI/Texture/CharacterCreation/backdrops/Background_1001_thumb.dds'
                    backdropSprite.display = True
                    bdScene.children.append(backdropSprite)
                else:
                    if info.raceID == const.raceCaldari:
                        rn = 'caldari'
                        bgcolor = (74 / 255.0, 87 / 255.0, 97 / 255.0)
                    elif info.raceID == const.raceAmarr:
                        rn = 'amarr'
                        bgcolor = (93 / 255.0, 89 / 255.0, 74 / 255.0)
                    elif info.raceID == const.raceMinmatar:
                        rn = 'minmatar'
                        bgcolor = (92 / 255.0, 81 / 255.0, 80 / 255.0)
                    elif info.raceID == const.raceGallente:
                        rn = 'gallente'
                        bgcolor = (77 / 255.0, 94 / 255.0, 93 / 255.0)
                    else:
                        rn = 'caldari'
                        bgcolor = (74 / 255.0, 87 / 255.0, 97 / 255.0)
                        log.LogWarn('Unknown raceID in characterCreationLayer.UpdateBackground', info.raceID)
                    mainHalo = trinity.Tr2Sprite2d()
                    mainHalo.name = u'mainHalo'
                    mainHalo.texturePrimary = trinity.Tr2Sprite2dTexture()
                    mainHalo.blendMode = trinity.TR2_SBM_ADD
                    r, g, b = bgcolor
                    mainHalo.color = (r * 0.75,
                     g * 0.75,
                     b * 0.75,
                     1.0)
                    mainHalo.displayWidth = mainHalo.displayHeight = max(desktopWidth, desktopHeight) * 1.5
                    mainHalo.displayX = (desktopWidth - mainHalo.displayWidth) / 2
                    mainHalo.displayY = (desktopHeight - mainHalo.displayHeight) / 2
                    mainHalo.display = True
                    mainHalo.texturePrimary.resPath = 'res:/UI/Texture/CharacterCreation/mainCenterHalo.dds'
                    bdScene.children.append(mainHalo)
                if self.stepID == ccConst.PORTRAITSTEP:
                    activeBackdrop = self.GetBackdrop()
                    if activeBackdrop:
                        portraitBackground = trinity.Tr2Sprite2d()
                        portraitBackground.name = u'portraitBackground'
                        bdScene.children.insert(0, portraitBackground)
                        portraitBackground.displayX = (desktopWidth - size) * 0.5
                        portraitBackground.displayY = (desktopHeight - size) * 0.5
                        portraitBackground.displayWidth = size
                        portraitBackground.displayHeight = size
                        if not portraitBackground.texturePrimary:
                            portraitBackground.texturePrimary = trinity.Tr2Sprite2dTexture()
                            portraitBackground.texturePrimary.resPath = activeBackdrop
                        portraitBackground.color = (1, 1, 1, 1)
                        portraitBackground.display = True
                        portraitBackground.blendMode = trinity.TR2_SBM_BLEND
                else:
                    if gfxsettings.Get(gfxsettings.UI_NCC_GREEN_SCREEN):
                        return
                    mainSize = size - margin
                    cs = trinity.TriCurveSet()
                    cs.name = 'RotationCurveSet'
                    bdScene.curveSets.append(cs)
                    for textureNo, textureSize in ((1, 468 / 1024.0),
                     (2, 580 / 1024.0),
                     (3, 1.0),
                     (4, 1.0)):
                        tf = trinity.Tr2Sprite2dTransform()
                        tf.name = u'tf'
                        tf.displayX = desktopWidth * 0.5
                        tf.displayY = desktopHeight * 0.5
                        bdScene.children.append(tf)
                        circleBG = trinity.Tr2Sprite2d()
                        circleBG.name = u'circleBG'
                        circleBG.texturePrimary = trinity.Tr2Sprite2dTexture()
                        circleBG.texturePrimary.resPath = 'res:/UI/Texture/CharacterCreation/circularRaceBgs/%s_%s.dds' % (rn, textureNo)
                        circleBG.color = (0.025, 0.025, 0.025, 1.0)
                        circleBG.blendMode = trinity.TR2_SBM_BLEND
                        circleBG.displayWidth = mainSize * textureSize
                        circleBG.displayHeight = mainSize * textureSize
                        circleBG.displayX = -circleBG.displayWidth * 0.5
                        circleBG.displayY = -circleBG.displayHeight * 0.5
                        circleBG.display = True
                        tf.children.append(circleBG)
                        rotationCurve = self.CreatePerlinCurve(cs, scale=16.0, offset=10.0, speed=0.001, alpha=0.9, beta=1.0 + random.random())
                        self.CreateBinding(cs, rotationCurve, tf, 'rotation', 'value')

                    cs.Play()
            return

    @telemetry.ZONE_METHOD
    def CreateBinding(self, curveSet, curve, destinationObject, attribute, sourceAttribute='currentValue'):
        binding = trinity.TriValueBinding()
        curveSet.bindings.append(binding)
        binding.destinationObject = destinationObject
        binding.destinationAttribute = attribute
        binding.sourceObject = curve
        binding.sourceAttribute = sourceAttribute
        return binding

    @telemetry.ZONE_METHOD
    def CreateScalarCurve(self, curveSet, length, endValue, startTimeOffset=0.0, startValue=0.0, cycle=False):
        curve = trinity.Tr2ScalarCurve()
        if startTimeOffset:
            curve.AddKey(0.0, startValue)
        curve.AddKey(startTimeOffset, startValue)
        curve.AddKey(startTimeOffset + length, endValue)
        curve.interpolation = trinity.TR2CURVE_HERMITE
        curve.cycle = cycle
        curveSet.curves.append(curve)
        return curve

    @telemetry.ZONE_METHOD
    def CreatePerlinCurve(self, curveSet, scale=1.0, offset=6.0, speed=1.1, alpha=1.0, beta=1.1):
        curve = trinity.TriPerlinCurve()
        curve.scale = scale
        curve.offset = offset
        curve.speed = speed
        curve.alpha = alpha
        curve.beta = beta
        curveSet.curves.append(curve)
        return curve

    @telemetry.ZONE_METHOD
    def GetLightID(self):
        path = self.lightingID
        files = ccConst.LIGHT_SETTINGS_ID
        for i, light in enumerate(files):
            if path == light:
                return i

    @telemetry.ZONE_METHOD
    def GetLightColorID(self):
        path = self.lightColorID
        files = ccConst.LIGHT_COLOR_SETTINGS_ID
        for i, light in enumerate(files):
            if path == light:
                return i

    @telemetry.ZONE_METHOD
    def GetBackgroundID(self):
        path = self.backdropPath
        ID = path.split('_')[-1].split('.')[0]
        ID = int(ID)
        return ID

    @telemetry.ZONE_METHOD
    def GetBackgroundPathFromID(self, bgID):
        return 'res:/UI/Texture/CharacterCreation/backdrops/Background_' + str(bgID) + '.dds'

    @telemetry.ZONE_METHOD
    def CapturePortrait(self, portraitID, *args):
        if self.camera is None:
            return
        else:
            poseData = self.characterSvc.GetPoseData()
            if poseData is None:
                return
            self.portraitInfo[portraitID] = util.KeyVal(cameraPosition=self.camera.GetPosition(), cameraFieldOfView=self.camera.fieldOfView, cameraPoi=self.camera.GetPointOfInterest(), backgroundID=self.GetBackgroundID(), lightID=self.lightingID, lightColorID=self.lightColorID, lightIntensity=self.GetLightIntensity(), poseData=poseData)
            maker = PortraitMaker(self.camera, self.backdropPath)
            return maker.GetPortraitTexture(portraitID)

    @telemetry.ZONE_METHOD
    def GetPortraitSnapshotPath(self, portraitID):
        return blue.paths.ResolvePathForWriting(u'cache:/Pictures/Portraits/PortraitSnapshot_%s_%s.jpg' % (portraitID, session.userid))

    @telemetry.ZONE_METHOD
    def ClearPortraitInfo(self):
        self.portraitInfo = [None] * ccConst.NUM_PORTRAITS
        return

    @telemetry.ZONE_METHOD
    def GetPortraitInfo(self, portraitID):
        return self.portraitInfo[portraitID]

    @telemetry.ZONE_METHOD
    def GetDNA(self, getHiddenModifiers=False, getWeightless=False):
        return self.doll.GetDNA(getHiddenModifiers=getHiddenModifiers, getWeightless=getWeightless)

    @telemetry.ZONE_METHOD
    def GetRandomLastName(self, bloodlineID):
        try:
            return random.choice(cfg.bloodlineNames[bloodlineID])['lastName']
        except KeyError:
            self.characterSvc.LogError('Bloodline with ID', bloodlineID, 'has no last names defined!')
            return ''

    @telemetry.ZONE_METHOD
    def OnHideUI(self, *args):
        self.sr.uiContainer.state = uiconst.UI_HIDDEN

    @telemetry.ZONE_METHOD
    def OnShowUI(self, *args):
        self.sr.uiContainer.state = uiconst.UI_PICKCHILDREN

    def OnMapShortcut(self, *args):
        uicore.cmd.commandMap.UnloadAllAccelerators()
        uicore.cmd.commandMap.LoadAcceleratorsByCategory('general')

    @telemetry.ZONE_METHOD
    def ShowLoading(self, why='', top=200, forceOn=0, *args):
        wheel = self.sr.loadingWheel
        wheel.top = top
        wheel.hint = why
        wheel.forcedOn = forceOn
        wheel.Show()

    @telemetry.ZONE_METHOD
    def HideLoading(self, why='', forceOff=0, *args):
        wheel = self.sr.loadingWheel
        if not wheel.forcedOn or forceOff:
            self.sr.loadingWheel.Hide()
            wheel.forcedOn = 0

    @telemetry.ZONE_METHOD
    def OnCloseView(self):
        uicore.cmd.LoadAllAccelerators()
        sm.GetService('tutorial').ChangeTutorialWndState(visible=True)
        self.TearDown()
        audioService = sm.GetService('audio')
        audioService.SendUIEvent('wise:/ui_icc_sculpting_mouse_over_loop_stop')
        if audioService.GetWorldVolume() == 0.0:
            audioService.SetWorldVolume(self.worldLevel)
        sm.GetService('cc').ClearMyAvailabelTypeIDs()
        self.Flush()
        self.sr.step = None
        if self.previewWindowWasOpenOn is not None:
            charID = self.previewWindowWasOpenOn[0]
            self.previewWindowWasOpenOn = None
            sm.GetService('preview').PreviewCharacter(charID)
        sm.GetService('dynamicMusic').UpdateDynamicMusic()
        return

    @telemetry.ZONE_METHOD
    def ExitToStation(self, updateDoll=True):
        if session.worldspaceid is not None:
            dna = self.GetDNA()
            sm.GetService('viewState').CloseSecondaryView()
        else:
            self.OnCloseView()
            if session.structureid:
                change = {'structureid': (None, session.structureid)}
            else:
                change = {'stationid': (None, session.stationid)}
            sm.GetService('gameui').OnSessionChanged(isRemote=False, session=session, change=change)
        return

    def ToggleClothes(self, forcedValue=None, doUpdate=True, *args):
        valueBefore = self.clothesOff
        if forcedValue is None:
            self.clothesOff = not self.clothesOff
        else:
            self.clothesOff = forcedValue
        if valueBefore == self.clothesOff:
            return
        else:
            info = self.GetInfo()
            if info.charID in self.characterSvc.characters:
                character = self.characterSvc.GetSingleCharacter(info.charID)
                if self.clothesOff:
                    self.RemoveClothes(character, doUpdate=doUpdate)
                else:
                    self.ReApplyClothes(character, doUpdate=doUpdate)
            return

    @telemetry.ZONE_METHOD
    def ReApplyClothes(self, character, doUpdate=True):
        if not self.clothesStorage or character is None:
            return
        else:
            doll = character.doll
            bdm = doll.buildDataManager
            modifiers = doll.SortModifiersForBatchAdding(self.clothesStorage.values())
            for modifier in modifiers:
                bdm.AddModifier(modifier)

            self.ResetClothesStorage()
            if doUpdate:
                sm.GetService('character').UpdateDollsAvatar(character)
            return

    @telemetry.ZONE_METHOD
    def RemoveClothes(self, character, doUpdate=True):
        if self.clothesStorage or character is None:
            return
        else:
            categoriesToRemove = paperDoll.BODY_CATEGORIES - (paperDoll.BODY_CATEGORIES.SKIN,
             paperDoll.BODY_CATEGORIES.TATTOO,
             paperDoll.BODY_CATEGORIES.TOPUNDERWEAR,
             paperDoll.BODY_CATEGORIES.BOTTOMUNDERWEAR,
             paperDoll.BODY_CATEGORIES.SKINTONE,
             paperDoll.BODY_CATEGORIES.SKINTYPE,
             paperDoll.BODY_CATEGORIES.SCARS)
            categoriesToRemove = list(categoriesToRemove)
            categoriesToRemove.sort(key=lambda x: -paperDoll.DESIRED_ORDER.index(x))
            self.ResetClothesStorage()
            bdm = character.doll.buildDataManager
            for category in categoriesToRemove:
                categoryModifiers = bdm.GetModifiersByCategory(category)
                for modifier in categoryModifiers:
                    if modifier.respath not in paperDoll.DEFAULT_NUDE_PARTS:
                        self.clothesStorage[category] = modifier
                        bdm.RemoveModifier(modifier)

            modifier = self.characterSvc.GetModifierByCategory(self.charID, ccConst.glasses)
            if modifier:
                self.clothesStorage[ccConst.glasses] = modifier
                bdm.RemoveModifier(modifier)
            if doUpdate:
                sm.GetService('character').UpdateDollsAvatar(character)
            return

    def ResetClothesStorage(self, *args):
        self.clothesStorage.clear()

    def RemoveBodyModifications(self, *args):
        try:
            if getattr(self, 'bodyModRemoved', 0):
                return
            modifiersToRemove = [ccConst.p_earslow,
             ccConst.p_earshigh,
             ccConst.p_nose,
             ccConst.p_nostril,
             ccConst.p_brow,
             ccConst.p_lips,
             ccConst.p_chin,
             ccConst.t_head,
             ccConst.s_head]
            character = self.characterSvc.GetSingleCharacter(self.charID)
            for mod in modifiersToRemove:
                modifiers = self.characterSvc.GetModifiersByCategory(self.charID, mod)
                for m in modifiers:
                    character.doll.buildDataManager.RemoveModifier(m)
                    self.characterSvc.RemoveFromCharacterMetadata(self.charID, mod)

            self.bodyModRemoved = 1
            sm.GetService('character').UpdateDollsAvatar(character)
        except Exception:
            pass

    @telemetry.ZONE_METHOD
    def StartDnaLogging(self):
        self.dnaList = []
        self.lastLitHistoryBit = None
        return

    def ResetDna(self, *args):
        self.dnaList = None
        self.lastLitHistoryBit = None
        return

    @telemetry.ZONE_METHOD
    def ClearDnaLogFromIndex(self, fromIndex):
        if self.dnaList:
            to = fromIndex + 1
            if to > len(self.dnaList):
                to = len(self.dnaList)
            self.dnaList = self.dnaList[:to]

    def AskForPortraitConfirmation(self, characterName=None, *args):
        photo = self.GetActivePortrait()
        wnd = CCConfirmationWindow.Open(photo=photo, characterName=characterName)
        if wnd.ShowModal() == uiconst.ID_YES:
            return True
        else:
            return False

    @telemetry.ZONE_METHOD
    def GetDollDNAHistory(self):
        return self.dnaList

    def TryStoreDna(self, lastUpdateRedundant, fromWhere, sculpting=0, force=0, allowReduntant=0, *args):
        if not lastUpdateRedundant or fromWhere in ('RandomizeCharacterGroups', 'RandomizeCharacter', 'AddCharacter'):
            if not self.isopen:
                return
            if self.stepID == ccConst.CUSTOMIZATIONSTEP:
                if self.sr.step is None:
                    return
                if not force and self.sr.step.menuMode == self.sr.step.TATTOOMENU:
                    self.sr.step.tattooChangeMade = 1
                    return
            if self.dnaList is not None:
                self.CheckDnaLog('UpdateDoll')
                dna = self.GetDNA(getHiddenModifiers=False, getWeightless=True)
                if not allowReduntant:
                    try:
                        currentIndex, maxIndex = self.sr.step.sr.historySlider.GetCurrentIndexAndMaxIndex()
                        if dna == self.dnaList[currentIndex][0]:
                            return
                    except Exception:
                        pass

                currMetadata = copy.deepcopy(self.characterSvc.characterMetadata[self.charID])
                self.dnaList.append((dna, currMetadata))
                if lastUpdateRedundant or force:
                    sm.ScatterEvent('OnHistoryUpdated')
        return

    @telemetry.ZONE_METHOD
    def LoadDnaFromHistory(self, historyIndex):
        if len(self.characterSvc.characters) > 0:
            character = self.characterSvc.GetSingleCharacter(self.charID)
            if character:
                historyIndex = max(0, min(len(self.dnaList) - 1, historyIndex))
                dna, metadata = self.dnaList[historyIndex]
                metadata = copy.deepcopy(metadata)
                self.ToggleClothes(forcedValue=0, doUpdate=False)
                self.characterSvc.MatchDNA(character, dna)
                self.characterSvc.characterMetadata[self.charID] = metadata
                if self.characterSvc.GetSculptingActive():
                    sculpting = self.characterSvc.GetSculpting()
                    sculpting.UpdateFieldsBasedOnExistingValues(character.doll)
                self.characterSvc.UpdateDoll(self.charID, fromWhere='LoadDnaFromHistory', registerDna=False)
                self.characterSvc.SynchronizeHairColors(self.charID)

    @telemetry.ZONE_METHOD
    def PassMouseEventToSculpt(self, type, x, y):
        if not hasattr(self, 'characterSvc'):
            return
        else:
            pickValue = None
            sculpting = self.characterSvc.GetSculpting()
            if sculpting and self.characterSvc.GetSculptingActive():
                if type == 'LeftDown':
                    pickValue = sculpting.PickWrapper(x, y)
                elif type == 'LeftUp':
                    pickValue = sculpting.EndMotion(x, y)
                elif type == 'Motion':
                    pickValue = sculpting.MotionWrapper(x, y)
            return pickValue

    def UpdateRaceMusic(self, raceID=None):
        sm.GetService('dynamicMusic').UpdateDynamicMusic()

    def PickPortrait(self, newPortraitID):
        if self.stepID != ccConst.PORTRAITSTEP:
            return
        self.sr.step.PickPortrait(newPortraitID)

    def AnimateToStoredPortrait(self, newPortraitID):
        if self.stepID != ccConst.PORTRAITSTEP:
            return
        elif self.portraitInfo[newPortraitID] is None:
            return
        else:
            if self.animateToStoredPortraitThread and self.animateToStoredPortraitThread.alive:
                if self.animatingToPortraitID == newPortraitID:
                    return
                self.animateToStoredPortraitThread.kill()
            self.animateToStoredPortraitThread = uthread.new(self.AnimateToStoredPortrait_thread, newPortraitID)
            return

    def AnimateToStoredPortrait_thread(self, newPortraitID):
        portraitInfo = self.portraitInfo[newPortraitID]
        if portraitInfo is None:
            return
        else:
            newParams = self.GetControlParametersFromPortraitID(newPortraitID)
            if newParams is None:
                return
            oldParams = self.GetControlParametersFromPortraitID(None)
            if len(oldParams) < 1 or len(newParams) < 1:
                return
            self.animatingToPortraitID = newPortraitID
            thereIsCamera = self.camera is not None
            if thereIsCamera:
                oldCameraPos = self.camera.cameraPosition
                oldCameraPoi = self.camera.poi
                oldCameraFov = self.camera.fieldOfView
            info = self.GetInfo()
            start, ndt = blue.os.GetWallclockTime(), 0.0
            moveCamera = self.ShouldMoveCamera(portraitInfo.cameraPosition, portraitInfo.cameraPoi)
            while ndt != 1.0:
                timeValue = min(blue.os.TimeDiffInMs(start, blue.os.GetWallclockTime()) / 250.0, 1.0)
                ndt = math.sin(timeValue * math.pi - math.pi / 2.0) / 2.0 + 0.5
                params = []
                for shortKey, keyAndValue in oldParams.iteritems():
                    longKey, value = keyAndValue
                    if shortKey == 'HeadLookTarget':
                        lerpedValue = geo2.Lerp(value, newParams[shortKey][1], ndt)
                    elif shortKey == 'PortraitPoseNumber':
                        continue
                    else:
                        lerpedValue = mathUtil.Lerp(value, newParams[shortKey][1], ndt)
                    params.append([longKey, lerpedValue])

                sm.GetService('character').SetControlParametersFromList(params, info.charID)
                if thereIsCamera and moveCamera:
                    posValue = geo2.Lerp(oldCameraPos, portraitInfo.cameraPosition, ndt)
                    poiValue = geo2.Lerp(oldCameraPoi, portraitInfo.cameraPoi, ndt)
                    self.cameraPos = posValue
                    self.cameraPoi = poiValue
                    self.camera.PlacePortraitCamera(self.cameraPos, self.cameraPoi)
                blue.pyos.synchro.Yield()

            xFactor, yFactor = self.camera.GetCorrectCameraXandYFactors(portraitInfo.cameraPosition, portraitInfo.cameraPoi)
            self.camera.xFactor = self.camera.xTarget = xFactor
            self.camera.yFactor = self.camera.yTarget = yFactor
            self.lightingID = portraitInfo.lightID
            self.lightIntensity = portraitInfo.lightIntensity
            self.lightColorID = portraitInfo.lightColorID
            shouldSnapPortrait = False
            path = self.GetBackgroundPathFromID(portraitInfo.backgroundID)
            if path in ccConst.backgroundOptions or gfxsettings.Get(gfxsettings.UI_NCC_GREEN_SCREEN) and path in ccConst.greenscreenBackgroundOptions:
                self.backdropPath = path
            elif not gfxsettings.Get(gfxsettings.UI_NCC_GREEN_SCREEN):
                shouldSnapPortrait = True
            self.poseID = int(portraitInfo.poseData['PortraitPoseNumber'])
            sm.GetService('character').SetControlParametersFromList([['ControlParameters|PortraitPoseNumber', float(self.poseID)]], info.charID)
            uicore.layer.charactercreation.UpdateBackdrop()
            self.UpdateLights()
            sm.ScatterEvent('OnPortraitPicked')
            if shouldSnapPortrait and self.sr.step:
                self.sr.step.CapturePortrait(newPortraitID)
            return

    def ShouldMoveCamera(self, newPos, newPoi):
        newDirection = geo2.Subtract(newPos, newPoi)
        distanceDiff = abs(self.camera.distance - geo2.Vec3Length(newDirection))
        direction2 = geo2.Vec3Normalize(newDirection)
        yaw = math.acos(direction2[0])
        yawDiff = abs(self.camera.yaw - yaw)
        pitch = math.asin(direction2[1]) + math.pi / 2.0
        pitchDiff = math.sqrt(math.pow(self.camera.pitch - pitch, 2))
        diffPos = geo2.Vec3Distance(self.camera.GetPosition(), newPos)
        if distanceDiff < 5e-07 and yawDiff < 5e-05 and pitchDiff < 5e-05 and diffPos < 0.05:
            return False
        return True

    def GetControlParametersFromPortraitID(self, portraitID, *args):
        PREFIX = 'ControlParameters|'
        params = {}
        if portraitID is not None:
            portraitInfo = uicore.layer.charactercreation.portraitInfo[portraitID]
            if portraitInfo is None:
                return {}
            return self.GetControlParametersFromPoseData(portraitInfo.poseData)
        else:
            info = self.GetInfo()
            avatar = self.characterSvc.GetSingleCharactersAvatar(info.charID)
            if avatar is None:
                return {}
            for controlParameter in paperDollUtil.FACIAL_POSE_PARAMETERS.__dict__.iterkeys():
                if controlParameter.startswith('_'):
                    continue
                longKey = PREFIX + controlParameter
                value = avatar.animationUpdater.network.GetControlParameterValue(longKey)
                params[controlParameter] = (longKey, value)

            return params

    def GetControlParametersFromPoseData(self, poseData, fromDB=False):
        if poseData is None:
            return {}
        else:
            if fromDB:
                allParameterKeys = poseData.__keys__
            else:
                allParameterKeys = poseData.keys()
            params = {}
            PREFIX = 'ControlParameters|'
            for key in allParameterKeys:
                if key in ('headLookTargetX', 'headLookTargetY', 'headLookTargetZ', 'cameraX', 'cameraY', 'cameraZ'):
                    continue
                value = poseData[key]
                if fromDB:
                    key = key.replace(key[0], key[0].upper(), 1)
                params[key] = (PREFIX + key, value)

            if fromDB:
                params['HeadLookTarget'] = (PREFIX + 'HeadLookTarget', (poseData['headLookTargetX'], poseData['headLookTargetY'], poseData['headLookTargetZ']))
            return params

    def TryFreezeAnimation(self, *args):
        if sm.GetService('machoNet').GetGlobalConfig().get('disableFreezeAnimationInNCC'):
            return
        elif self.stepID != ccConst.CUSTOMIZATIONSTEP:
            return
        else:
            info = self.GetInfo()
            avatar = self.characterSvc.GetSingleCharactersAvatar(info.charID)
            if avatar is not None:
                avatar.animationUpdater.network.update = False
                self.freezingAnimation = True
            return

    def UnfreezeAnimationIfNeeded(self, *args):
        if self.freezingAnimation:
            info = self.GetInfo()
            avatar = self.characterSvc.GetSingleCharactersAvatar(info.charID)
            if avatar is not None:
                avatar.animationUpdater.network.update = True
                self.freezingAnimation = False
        return

    def DoLogEvent(self, finished=1, *args):
        self.stepLogger.Stop()
        info = self.GetInfo()
        endTime = blue.os.GetWallclockTime()
        openFor = round(float(endTime - self.startTime) / const.SEC)
        customizationMode = self.mode
        userID = session.userid
        sm.GetService('infoGatheringSvc').LogInfoEvent(eventTypeID=const.infoEventCCDuration, itemID=info.charID, itemID2=userID, int_1=1, char_1=finished, char_2=customizationMode, float_1=openFor)
        timeObject = self.stepLogger.GetTimeObject()
        infoEventServiceLogger = StepInfoEventServiceLogger(sm.GetService('infoGatheringSvc').LogInfoEvent, sessionID=session.sid, userID=userID)
        infoEventServiceLogger.LogTimeObject(timeObject)
        if self.finalStepLogger:
            if finished:
                self.finalStepLogger.End()
            else:
                self.finalStepLogger.Cancel()
        self.LogFinalResultsIfNeededAndDestroy()


class CharCreationNavigation(uiprimitives.Container):
    __guid__ = 'uicls.CharCreationNavigation'
    default_align = uiconst.TOPLEFT
    default_height = 110
    default_state = uiconst.UI_NORMAL
    ANIMATIONTIME = 500.0
    MOUSEOVEROPACITY = 0.8
    NORMALOPACITY = 0.3
    ACTIVEOPACITY = 1.0
    NUMSTEPS = 5
    FONTSIZE = 16
    stepLabelDict = {ccConst.RACESTEP: 'UI/CharacterCreation/Step1',
     ccConst.BLOODLINESTEP: 'UI/CharacterCreation/Step2',
     ccConst.CUSTOMIZATIONSTEP: 'UI/CharacterCreation/Step3',
     ccConst.PORTRAITSTEP: 'UI/CharacterCreation/Step4',
     ccConst.NAMINGSTEP: 'UI/CharacterCreation/Step5',
     ccConst.MINIMALNAMINGSTEP: 'UI/CharacterCreation/Step5'}

    @telemetry.ZONE_METHOD
    def ApplyAttributes(self, attributes):
        uiprimitives.Container.ApplyAttributes(self, attributes)
        self.stepID = attributes.stepID
        self.stepsUsed = attributes.stepsUsed
        self.availableSteps = attributes.availableSteps
        self.stepIndex = {}
        stepIndex = 0
        for stepID in self.availableSteps:
            self.stepIndex[stepIndex] = stepID
            stepIndex += 1

        self.attributesApplied = 0
        self.callbackFunc = attributes.func
        self.sr.header = uicls.CCLabel(name='header', parent=self, align=uiconst.TOTOP, top=0, width=300, uppercase=1, letterspace=2, color=(0.9, 0.9, 0.9, 0.8), fontsize=self.FONTSIZE, bold=False)
        width = self.NUMSTEPS * 36
        self.width = width
        self.sr.stepCont = uiprimitives.Container(name='stepCont', parent=self, align=uiconst.CENTERTOP, pos=(0,
         26,
         width,
         26))
        self.ResetToStep(self.stepID, set(self.stepsUsed))

    def StepIndexToStepId(self, stepindex):
        return self.stepIndex[stepindex]

    def GetNextStepIDForStepID(self, stepID):
        nextStepUpcoming = False
        for i in range(0, len(self.availableSteps)):
            currentStep = self.availableSteps[i]
            if nextStepUpcoming:
                return currentStep
            if currentStep is stepID:
                nextStepUpcoming = True

        return None

    def makeConnectors(self):
        left = 20
        connectorFile = 'res:/UI/Texture/CharacterCreation/navigator/connector.dds'
        gradientFile = 'res:/UI/Texture/CharacterCreation/navigator/connector_fade.dds'
        for stepID in self.availableSteps[1:]:
            cont = uiprimitives.Container(name='space%s' % stepID, parent=self.sr.stepCont, align=uiconst.TOPLEFT, pos=(left,
             10,
             0,
             16), state=uiconst.UI_DISABLED, clipChildren=1)
            self.sr.Set('connector%s' % stepID, cont)
            sprite = uiprimitives.Sprite(name='connector%s' % stepID, parent=cont, align=uiconst.TOPLEFT, pos=(0, 0, 32, 16), state=uiconst.UI_DISABLED, texturePath=connectorFile)
            sprite.SetAlpha(self.NORMALOPACITY)
            sprite = uiprimitives.Sprite(name='connector_fade%s' % stepID, parent=cont, align=uiconst.TOPLEFT, pos=(0, 0, 32, 16), state=uiconst.UI_DISABLED, texturePath=gradientFile)
            self.sr.Set('connector_fade%s' % stepID, sprite)
            left += 36

    @telemetry.ZONE_METHOD
    def CreateSteps(self, *args):
        self.sr.stepCont.Flush()
        left = 0
        circleFile = 'res:/UI/Texture/CharacterCreation/navigator/ring.dds'
        dotFile = 'res:/UI/Texture/CharacterCreation/navigator/dot.dds'
        for stepID in self.availableSteps:
            step = uiprimitives.Container(name='step%s' % stepID, parent=self.sr.stepCont, align=uiconst.TOPLEFT, pos=(left,
             0,
             36,
             36), state=uiconst.UI_DISABLED)
            step.tlCont = uiprimitives.Container(name='tlCont', parent=step, align=uiconst.TOPLEFT, pos=(2, 2, 16, 16), state=uiconst.UI_DISABLED, clipChildren=1)
            sprite = uiprimitives.Sprite(name='tlSprite', parent=step.tlCont, align=uiconst.TOPLEFT, pos=(0, 0, 32, 32), state=uiconst.UI_DISABLED, texturePath=circleFile)
            step.trCont = uiprimitives.Container(name='trCont', parent=step, align=uiconst.TOPRIGHT, pos=(2, 2, 16, 16), state=uiconst.UI_DISABLED, clipChildren=1)
            sprite = uiprimitives.Sprite(name='trSprite', parent=step.trCont, align=uiconst.TOPRIGHT, pos=(0, 0, 32, 32), state=uiconst.UI_DISABLED, texturePath=circleFile)
            step.blCont = uiprimitives.Container(name='blCont', parent=step, align=uiconst.BOTTOMLEFT, pos=(2, 2, 16, 16), state=uiconst.UI_DISABLED, clipChildren=1)
            sprite = uiprimitives.Sprite(name='blSprite', parent=step.blCont, align=uiconst.BOTTOMLEFT, pos=(0, 0, 32, 32), state=uiconst.UI_DISABLED, texturePath=circleFile)
            step.brCont = uiprimitives.Container(name='trCont', parent=step, align=uiconst.BOTTOMRIGHT, pos=(2, 2, 16, 16), state=uiconst.UI_DISABLED, clipChildren=1)
            sprite = uiprimitives.Sprite(name='brSprite', parent=step.brCont, align=uiconst.BOTTOMRIGHT, pos=(0, 0, 32, 32), state=uiconst.UI_DISABLED, texturePath=circleFile)
            sprite = uiprimitives.Sprite(name='step%s' % stepID, parent=step, align=uiconst.TOPLEFT, pos=(2, 2, 32, 32), state=uiconst.UI_DISABLED, texturePath=dotFile)
            step.SetOpacity(self.NORMALOPACITY)
            left += 36
            step.id = stepID
            step.OnMouseEnter = (self.OnStepMouseOver, step)
            step.OnMouseExit = (self.OnStepMouseExit, step)
            step.OnClick = (self.OnStepClicked, step)
            self.sr.Set('step%s' % stepID, step)

        self.sr.stepCont.width = left
        self.makeConnectors()
        self.attributesApplied = 1

    @telemetry.ZONE_METHOD
    def ResetToStep(self, resetToStep, stepsUsed, *args):
        self.stepID = resetToStep
        self.stepsUsed = stepsUsed
        self.CreateSteps()
        firstCont = self.GetStepContainer(self.availableSteps[0])
        firstCont.state = uiconst.UI_NORMAL
        self.OpenRight(firstCont, time=0.0)
        if max(stepsUsed) < 1:
            firstCont.SetOpacity(self.ACTIVEOPACITY)
            secondCont = self.GetStepContainer(self.availableSteps[1])
            secondCont.state = uiconst.UI_NORMAL
            self.OpenLeft(secondCont, time=0.0)
        else:
            for stepID in xrange(self.availableSteps[0], resetToStep + 1):
                self.PerformStepChange(stepID, stepsUsed, forceOpen=1, time=0)

        self.stepsUsed.add(resetToStep)

    def GetStepContainer(self, stepID):
        return self.sr.Get('step%s' % stepID)

    def GetStepContainerViaGetAttr(self, stepID):
        return getattr(self.sr, 'step%s' % stepID, None)

    def GetConnectorFadeViaGetAttr(self, stepID):
        return getattr(self.sr, 'connector_fade%s' % stepID, None)

    def GetConnectorForStep(self, stepID):
        return self.sr.Get('connector%s' % stepID)

    @telemetry.ZONE_METHOD
    def PerformStepChange(self, stepID, stepsUsed, forceOpen=0, time=None):
        if not forceOpen:
            sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_step_navigation_anim_play'))
        if not self.attributesApplied:
            return
        else:
            if time is None:
                time = self.ANIMATIONTIME
            self.stepID = stepID
            self.stepsUsed = stepsUsed
            labelPath = self.stepLabelDict.get(stepID)
            headerText = localization.GetByLabel(labelPath)
            self.sr.header.text = headerText
            self.sr.header.SetAlpha(1.0)
            container = self.GetStepContainerViaGetAttr(stepID)
            currentContainerStepID = container.id
            stepsUsed = self.stepsUsed.copy()
            try:
                if (max(stepsUsed) >= currentContainerStepID or self.GetNextStepIDForStepID(max(stepsUsed)) == currentContainerStepID) and self.callbackFunc:
                    for availableStepID in self.availableSteps:
                        connectorFade = self.GetConnectorFadeViaGetAttr(availableStepID)
                        cont = self.GetStepContainerViaGetAttr(availableStepID)
                        if connectorFade:
                            if availableStepID == currentContainerStepID:
                                connectorFade.state = uiconst.UI_DISABLED
                            else:
                                connectorFade.state = uiconst.UI_HIDDEN
                        if cont and availableStepID != currentContainerStepID:
                            cont.SetOpacity(self.NORMALOPACITY)

                    cont = self.GetStepContainerViaGetAttr(currentContainerStepID)
                    if currentContainerStepID not in stepsUsed or forceOpen:
                        connector = self.GetConnectorForStep(currentContainerStepID)
                        if connector:
                            if time:
                                uicore.effect.CombineEffects(connector, width=32, time=time)
                            else:
                                connector.width = 32
                            cont.SetOpacity(self.ACTIVEOPACITY)
                            if currentContainerStepID not in [self.availableSteps[0], self.availableSteps[-1]]:
                                self.OpenRight(container, time=time)
                        nextStepID = self.GetNextStepIDForStepID(currentContainerStepID)
                        nextStep = self.GetStepContainer(nextStepID)
                        if nextStep:
                            self.OpenLeft(nextStep, time=time)
                            nextStep.state = uiconst.UI_NORMAL
                    if not container.destroyed and container.id == self.stepID:
                        container.SetOpacity(self.ACTIVEOPACITY)
            except AttributeError as e:
                if self is None or self.destroyed or e.message == 'SetOpacity':
                    sm.GetService('cc').LogWarn('Attibute error ignored when performing step change')
                else:
                    raise

            return

    @telemetry.ZONE_METHOD
    def OnStepClicked(self, stepClicked, *args):
        if self.callbackFunc:
            if self.stepID == stepClicked.id:
                if not eve.session.role & service.ROLE_PROGRAMMER:
                    return
            apply(self.callbackFunc, (stepClicked.id,))

    @telemetry.ZONE_METHOD
    def OnStepMouseOver(self, container, *args):
        mousedStep = container.id
        sm.StartService('audio').SendUIEvent(unicode('wise:/ui_icc_button_mouse_over_play'))
        if mousedStep == self.stepID:
            return
        if max(self.stepsUsed) >= mousedStep or max(self.stepsUsed) + 1 == mousedStep:
            container.SetOpacity(self.MOUSEOVEROPACITY)
        else:
            return
        labelPath = self.stepLabelDict.get(mousedStep)
        headerText = localization.GetByLabel(labelPath)
        self.sr.header.text = headerText
        self.sr.header.SetAlpha(0.3)

    @telemetry.ZONE_METHOD
    def OnStepMouseExit(self, container, *args):
        if container.id == self.stepID:
            container.SetOpacity(self.ACTIVEOPACITY)
            return
        container.SetOpacity(self.NORMALOPACITY)
        labelPath = self.stepLabelDict.get(self.stepID)
        headerText = localization.GetByLabel(labelPath)
        self.sr.header.text = headerText
        self.sr.header.SetAlpha(1.0)

    @telemetry.ZONE_METHOD
    def OpenLeft(self, container, time=0.0, *args):
        tlCont = getattr(container, 'tlCont', None)
        blCont = getattr(container, 'blCont', None)
        if time == 0.0:
            tlCont.height = blCont.height = 10
            return
        else:
            uthread.new(uicore.effect.CombineEffects, tlCont, height=10, time=time)
            uicore.effect.CombineEffects(blCont, height=10, time=time)
            return

    @telemetry.ZONE_METHOD
    def OpenRight(self, container, time=0.0, *args):
        trCont = getattr(container, 'trCont', None)
        brCont = getattr(container, 'brCont', None)
        if time == 0.0:
            trCont.height = brCont.height = 10
            return
        else:
            uthread.new(uicore.effect.CombineEffects, trCont, height=10, time=time)
            uicore.effect.CombineEffects(brCont, height=10, time=time)
            return


class CCConfirmationWindow(uicontrols.Window):
    __guid__ = 'form.CCConfirmationWindow'
    default_width = 540
    default_height = 326
    default_windowID = 'ccConfirmationWindow'

    def ApplyAttributes(self, attributes):
        uicontrols.Window.ApplyAttributes(self, attributes)
        photo = attributes.photo
        characterName = attributes.characterName
        self.isModal = True
        self.SetTopparentHeight(0)
        self.sr.main.Flush()
        self.MakeUnResizeable()
        buttonContainer = uiprimitives.Container(name='', parent=self.sr.main, align=uiconst.TOBOTTOM, pos=(0, 0, 0, 30))
        self.sr.headerParent.state = uiconst.UI_HIDDEN
        self.width = self.default_width
        self.height = self.default_height
        btns = uicontrols.ButtonGroup(btns=[[localization.GetByLabel('UI/Generic/OK'), self.Confirm, ()], [localization.GetByLabel('UI/Generic/Cancel'), self.Cancel, ()]], parent=buttonContainer, idx=0)
        self.sr.centerCont = uiprimitives.Container(name='centerCont', parent=self.sr.main, align=uiconst.TOALL, pos=(0, 0, 0, 0), padding=(20, 20, 20, 0))
        self.sr.leftSide = uiprimitives.Container(name='leftSide', parent=self.sr.centerCont, align=uiconst.TOLEFT, pos=(0, 0, 260, 0))
        self.sr.portraitCont = uiprimitives.Container(name='portraitCont', parent=self.sr.leftSide, align=uiconst.TOPLEFT, pos=(0, 0, 256, 256))
        uicontrols.Frame(parent=self.sr.portraitCont, color=(1.0, 1.0, 1.0, 1.0))
        self.sr.facePortrait = uicontrols.Icon(parent=self.sr.portraitCont, align=uiconst.TOALL)
        if photo is not None:
            self.sr.facePortrait.texture.atlasTexture = photo
            self.sr.facePortrait.texture.atlasTexture.Reload()
        self.sr.rightSide = uiprimitives.Container(name='rightSide', parent=self.sr.centerCont, align=uiconst.TOALL, padding=(10, 0, 0, 0))
        caption = uicontrols.EveCaptionMedium(text=localization.GetByLabel('UI/CharacterCreation/ConfirmationHeader'), parent=self.sr.rightSide, align=uiconst.TOTOP, idx=-1, state=uiconst.UI_DISABLED, name='caption')
        text = uicontrols.EveLabelMedium(text=localization.GetByLabel('UI/CharacterCreation/Confirmation'), parent=self.sr.rightSide, align=uiconst.TOTOP, top=4)
        if characterName:
            nameText = uicontrols.EveLabelLarge(text='<center>%s' % characterName, parent=self.sr.leftSide, align=uiconst.TOTOP, top=260)
            self.height += nameText.textheight
        return

    def Confirm(self, *args):
        self.result = True
        self.SetModalResult(uiconst.ID_YES)

    def Cancel(self, *args):
        self.result = False
        self.SetModalResult(uiconst.ID_NO)