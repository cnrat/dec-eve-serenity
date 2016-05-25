# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\parklife\fightersSvc.py
from appConst import defaultPadding
from carbon.common.script.sys.service import Service
from carbon.common.script.sys.serviceConst import ROLE_GML
from eve.client.script.parklife import states
from eve.client.script.ui.services.menuSvcExtras import movementFunctions
from eveexceptions import UserError
from fighters.abilityAttributes import GetDogmaEffectIDForAbilityID
import uicontrols
import uiprimitives
from carbonui.const import TOPLEFT, YESNO, ID_YES
import geo2
from eve.client.script.ui.inflight.squadrons.shipFighterState import ShipFighterState
from eve.common.script.mgt import fighterConst
from eve.common.script.mgt.fighterConst import TUBE_STATE_RECALLING, TUBE_STATE_INSPACE, TUBE_STATE_READY
import evetypes
from fighters import ABILITY_SLOT_0, ABILITY_SLOT_1, ABILITY_SLOT_2, GetAbilityIDForSlot, GetAbilityNameIDForSlot, DEFAULT_CONTROLLER_ORBIT_DISTANCE
from inventorycommon.const import categoryFighter
from spacecomponents.client.components.behavior import EnableDebugging
import carbonui.const as uiconst

class FighterDebugWindow(uicontrols.Window):
    default_windowID = 'FighterDebugWindow'
    default_width = 250
    default_height = 360
    default_caption = 'Fighter debugger'
    default_icon = '41_13'
    currentFighterID = None

    def ApplyAttributes(self, attributes):
        uicontrols.Window.ApplyAttributes(self, attributes)
        self.SetTopparentHeight(0)
        self.SetMinSize([250, 360])
        self.MakeUnResizeable()
        mainCont = uiprimitives.Container(name='mainCont', parent=self.sr.main, pos=(defaultPadding,
         defaultPadding,
         defaultPadding,
         defaultPadding))
        uicontrols.Label(text='Fighter ID', parent=mainCont, pos=(10, 10, 0, 0), align=TOPLEFT)
        self.fighterIDBox = uicontrols.SinglelineEdit(name='fighterID', parent=mainCont, pos=(80, 10, 130, 20), align=TOPLEFT, OnChange=self.OnFighterIDBoxChange)
        self.fighterIDBox.SetText(self._GetFighterID())
        uicontrols.Button(parent=mainCont, name='DebugFighter', label='DBG', pos=(220, 10, 100, 0), fixedwidth=20, func=self.OnDebugFighterButton, align=TOPLEFT)
        uicontrols.Label(text='Target ID', parent=mainCont, pos=(10, 40, 0, 0), align=TOPLEFT)
        self.targetIDBox = uicontrols.SinglelineEdit(name='targetID', parent=mainCont, pos=(80, 40, 160, 20), align=TOPLEFT)
        self.targetIDBox.SetText(session.shipid)
        uicontrols.Button(parent=mainCont, name='OrbitTarget', label='Orbit Target', pos=(10, 70, 0, 0), fixedwidth=110, func=self.OnOrbitTargetButton)
        uicontrols.Button(parent=mainCont, name='OrbitMe', label='Orbit Me', pos=(130, 70, 0, 0), fixedwidth=110, func=self.OnOrbitMeButton)
        uicontrols.Button(parent=mainCont, name='StopMovement', label='Stop movement', pos=(10, 100, 0, 0), fixedwidth=110, func=self.OnMoveStopButton)
        uicontrols.Label(text='x,y,z', parent=mainCont, pos=(10, 130, 0, 0), align=TOPLEFT)
        self.gotoPosBox = uicontrols.SinglelineEdit(name='gotoPos', parent=mainCont, pos=(40, 130, 190, 20), align=TOPLEFT)
        uicontrols.ButtonIcon(name='pickXYZ', parent=mainCont, pos=(230, 130, 16, 16), align=TOPLEFT, width=16, iconSize=16, texturePath='res:/UI/Texture/Icons/38_16_150.png', hint='Pick random position near target', func=self.OnPickXYZ)
        uicontrols.Button(parent=mainCont, name='GotoPoint', label='Goto this point', pos=(130, 150, 0, 0), fixedwidth=110, func=self.OnGotoPointButton)
        uicontrols.Button(parent=mainCont, name='ToggleMoveMode', label='Toggle Movement', pos=(10, 150, 0, 0), fixedwidth=110, func=self.OnToggleMoveButton)
        uicontrols.Label(text='Ability 0', parent=mainCont, pos=(10, 180, 0, 0), align=TOPLEFT)
        uicontrols.Button(parent=mainCont, name='ActivateAbilityOnTarget', label='Activate (target)', pos=(10, 200, 0, 0), fixedwidth=80, func=self.OnActivateAbilityOnTarget, args=(ABILITY_SLOT_0,))
        uicontrols.Button(parent=mainCont, name='ActivateAbilityOnSelf', label='Activate (self)', pos=(95, 200, 0, 0), fixedwidth=80, func=self.OnActivateAbilityOnSelf, args=(ABILITY_SLOT_0,))
        uicontrols.Button(parent=mainCont, name='DeactivateAbility', label='Deactivate', pos=(180, 200, 0, 0), fixedwidth=60, func=self.OnDeactivateAbility, args=(ABILITY_SLOT_0,))
        uicontrols.Label(text='Ability 1', parent=mainCont, pos=(10, 230, 0, 0), align=TOPLEFT)
        uicontrols.Button(parent=mainCont, name='ActivateAbilityOnTarget', label='Activate (target)', pos=(10, 250, 0, 0), fixedwidth=80, func=self.OnActivateAbilityOnTarget, args=(ABILITY_SLOT_1,))
        uicontrols.Button(parent=mainCont, name='ActivateAbilityOnSelf', label='Activate (self)', pos=(95, 250, 0, 0), fixedwidth=80, func=self.OnActivateAbilityOnSelf, args=(ABILITY_SLOT_1,))
        uicontrols.Button(parent=mainCont, name='DeactivateAbility', label='Deactivate', pos=(180, 250, 0, 0), fixedwidth=60, func=self.OnDeactivateAbility, args=(ABILITY_SLOT_1,))
        uicontrols.Label(text='Ability 2', parent=mainCont, pos=(10, 280, 0, 0), align=TOPLEFT)
        uicontrols.Button(parent=mainCont, name='ActivateAbilityOnTarget', label='Activate (target)', pos=(10, 300, 0, 0), fixedwidth=80, func=self.OnActivateAbilityOnTarget, args=(ABILITY_SLOT_2,))
        uicontrols.Button(parent=mainCont, name='ActivateAbilityOnSelf', label='Activate (self)', pos=(95, 300, 0, 0), fixedwidth=80, func=self.OnActivateAbilityOnSelf, args=(ABILITY_SLOT_2,))
        uicontrols.Button(parent=mainCont, name='DeactivateAbility', label='Deactivate', pos=(180, 300, 0, 0), fixedwidth=60, func=self.OnDeactivateAbility, args=(ABILITY_SLOT_2,))

    def _GetFighterID(self):
        return self.currentFighterID

    def _GetTargetID(self):
        try:
            return int(self.targetIDBox.text.strip())
        except ValueError:
            return None

        return None

    def OnFighterIDBoxChange(self, *args):
        try:
            self.currentFighterID = int(self.fighterIDBox.text.strip())
        except ValueError:
            pass

    def OnDebugFighterButton(self, *args):
        self._OnDebugFighterButton(*args)

    def _OnDebugFighterButton(self, *args):
        fighterID = self._GetFighterID()
        if fighterID is not None:
            EnableDebugging(fighterID)
        return

    def OnPickXYZ(self, *args):
        self._OnPickXYZ(*args)

    def _OnPickXYZ(self, *args):
        michelle = sm.GetService('michelle')
        targetID = self._GetTargetID() or session.shipid
        ball = michelle.GetBall(targetID)
        if ball:
            import random
            shipPos = geo2.VectorD(ball.x, ball.y, ball.z)
            offsetRange = ball.radius + 2000
            offset = geo2.Vector(random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1))
            targetPos = geo2.Vec3AddD(shipPos, geo2.Vec3Scale(geo2.Vec3Normalize(offset), offsetRange))
            self.gotoPosBox.SetText('%.0f, %.0f, %0.f' % (targetPos[0], targetPos[1], targetPos[2]))

    def OnGotoPointButton(self, *args):
        self._OnGotoPointButton(*args)

    def _OnGotoPointButton(self, *args):
        fighterID = self._GetFighterID()
        if fighterID is not None:
            point = geo2.VectorD([ float(v.strip()) for v in self.gotoPosBox.text.strip().split(',') ])
            sm.GetService('fighters').CmdGotoPoint([fighterID], list(point))
        return

    def OnToggleMoveButton(self, *args):
        self._OnOnToggleMoveButton(*args)

    def _OnOnToggleMoveButton(self, *args):
        selectedSquadrons = uicore.layer.shipui.fighterCont.GetSelectedSquadrons()
        selectedIDs = [ squadron.fighterItemID for squadron in selectedSquadrons ]
        fighterID = self._GetFighterID()
        if len(selectedIDs) > 0:
            uicore.layer.inflight.positionalControl.StartFighterMoveCommand(selectedIDs)
        elif fighterID is not None:
            uicore.layer.inflight.positionalControl.StartFighterMoveCommand([fighterID])
        return

    def OnOrbitTargetButton(self, *args):
        self._OnOrbitTargetButton(*args)

    def _OnOrbitTargetButton(self, *args):
        fighterID = self._GetFighterID()
        targetID = self._GetTargetID()
        if fighterID is not None and targetID is not None:
            sm.GetService('fighters').CmdMovementOrbit([fighterID], targetID, 5000)
        return

    def OnOrbitMeButton(self, *args):
        self._OnOrbitMeButton(*args)

    def _OnOrbitMeButton(self, *args):
        fighterID = self._GetFighterID()
        if fighterID is not None:
            sm.GetService('fighters').CmdMovementOrbit([fighterID], session.shipid, 5000)
        return

    def OnMoveStopButton(self, *args):
        self._OnMoveStopButton(*args)

    def _OnMoveStopButton(self, *args):
        fighterID = self._GetFighterID()
        if fighterID is not None:
            sm.GetService('fighters').CmdMovementStop([fighterID])
        return

    def OnActivateAbilityOnTarget(self, abilitySlotID):
        self._OnActivateAbilityOnTarget(abilitySlotID)

    def _OnActivateAbilityOnTarget(self, abilitySlotID):
        fighterID = self._GetFighterID()
        targetID = self._GetTargetID()
        if fighterID is not None and targetID is not None:
            sm.GetService('fighters').ActivateAbilitySlotsOnTarget([fighterID], abilitySlotID, targetID)
        return

    def OnActivateAbilityOnSelf(self, abilitySlotID):
        self._OnActivateAbilityOnSelf(abilitySlotID)

    def _OnActivateAbilityOnSelf(self, abilitySlotID):
        fighterID = self._GetFighterID()
        if fighterID is not None:
            sm.GetService('fighters').ActivateAbilitySlotsOnSelf([fighterID], abilitySlotID)
        return

    def OnDeactivateAbility(self, abilitySlotID):
        self._OnDeactivateAbility(abilitySlotID)

    def _OnDeactivateAbility(self, abilitySlotID):
        fighterID = self._GetFighterID()
        if fighterID is not None:
            sm.GetService('fighters').DeactivateAbilitySlots([fighterID], abilitySlotID)
        return


class FightersSvc(Service):
    __dependencies__ = ['michelle', 'consider', 'crimewatchSvc']
    __guid__ = 'svc.fighters'
    __servicename__ = 'fighters'
    __displayname__ = 'Fighters service'
    __neocommenuitem__ = (('Fighter debugger', None), 'ShowDebugWindow', ROLE_GML)
    __notifyevents__ = ['OnStateChange']
    shipFighterState = None

    def Run(self, memStream=None):
        self.LogInfo('Starting fighters service')
        self.shipFighterState = ShipFighterState(self)

    def ShowDebugWindow(self):
        wnd = FighterDebugWindow.GetIfOpen()
        if wnd:
            wnd.Maximize()
        else:
            FighterDebugWindow.Open()

    def FightersMenu(self):

        def SpawnFighterInBay(fighterTypeID):
            self.LogInfo('Spawning fighter via /fit', fighterTypeID, evetypes.GetEnglishName(fighterTypeID))
            sm.RemoteSvc('slash').SlashCmd('/fit me %d %d' % (fighterTypeID, 1))

        groupMenu = []
        for fighterGroupID in evetypes.GetGroupIDsByCategory(categoryFighter):
            groupName = evetypes.GetGroupNameByGroup(fighterGroupID)
            typeMenu = []
            for fighterTypeID in evetypes.GetTypeIDsByGroup(fighterGroupID):
                fighterName = evetypes.GetEnglishName(fighterTypeID)
                typeMenu.append((fighterName, SpawnFighterInBay, (fighterTypeID,)))

            typeMenu.sort()
            groupMenu.append((groupName, typeMenu))

        groupMenu.sort()
        return [('NEW FIGHTERS', groupMenu)]

    def CmdReturnAndOrbit(self, fighterIDs):
        self.CmdMovementOrbit(fighterIDs, session.shipid, DEFAULT_CONTROLLER_ORBIT_DISTANCE)

    def CmdMovementOrbit(self, fighterIDs, targetID, followRange):
        self._ExecuteMovementCommandOnFighters(fighterConst.MOVEMENT_COMMAND_ORBIT, fighterIDs, targetID, followRange)

    def CmdMovementFollow(self, fighterIDs, targetID, followRange):
        self._ExecuteMovementCommandOnFighters(fighterConst.MOVEMENT_COMMAND_FOLLOW, fighterIDs, targetID, followRange)

    def CmdMovementStop(self, fighterIDs):
        self._ExecuteMovementCommandOnFighters(fighterConst.MOVEMENT_COMMAND_STOP, fighterIDs)

    def CmdGotoPoint(self, fighterIDs, point):
        self._ExecuteMovementCommandOnFighters(fighterConst.MOVEMENT_COMMAND_GOTO_POINT, fighterIDs, point)

    def _ExecuteMovementCommandOnFighters(self, command, fighterIDs, *args, **kwargs):
        if fighterIDs:
            sm.RemoteSvc('fighterMgr').ExecuteMovementCommandOnFighters(fighterIDs, command, *args, **kwargs)

    def GetFightersForShip(self):
        return sm.RemoteSvc('fighterMgr').GetFightersForShip()

    def LoadFightersToTube(self, fighterID, tubeFlagID):
        return sm.RemoteSvc('fighterMgr').LoadFightersToTube(fighterID, tubeFlagID)

    def UnloadTubeToFighterBay(self, tubeFlagID):
        return sm.RemoteSvc('fighterMgr').UnloadTubeToFighterBay(tubeFlagID)

    def LaunchFightersFromTubes(self, tubeFlagIDs):
        tubeFlagIDs = [ tubeFlagID for tubeFlagID in tubeFlagIDs if self.shipFighterState.GetTubeStatus(tubeFlagID).statusID == TUBE_STATE_READY ]
        if not tubeFlagIDs:
            return
        errorsByTubeID = sm.RemoteSvc('fighterMgr').LaunchFightersFromTubes(tubeFlagIDs)
        for tubeID, error in errorsByTubeID.iteritems():
            if error:
                sm.GetService('gameui').OnRemoteMessage(*error.args)

    def RecallFightersToTubes(self, fighterIDs):
        fighterTubesByID = {}
        for fighterID in fighterIDs:
            fighterInSpace = self.shipFighterState.GetFighterInSpaceByID(fighterID)
            if fighterInSpace is None:
                continue
            tubeStatus = self.shipFighterState.GetTubeStatus(fighterInSpace.tubeFlagID)
            if tubeStatus.statusID != TUBE_STATE_INSPACE:
                continue
            fighterTubesByID[fighterID] = fighterInSpace.tubeFlagID

        if not fighterTubesByID:
            return
        else:
            errorsByFighterID = sm.RemoteSvc('fighterMgr').RecallFightersToTubes(fighterTubesByID.keys())
            for fighterID, error in errorsByFighterID.iteritems():
                if error:
                    sm.GetService('gameui').OnRemoteMessage(*error.args)
                else:
                    tubeFlagID = fighterTubesByID[fighterID]
                    self.shipFighterState.OnFighterTubeTaskStatus(tubeFlagID, TUBE_STATE_RECALLING, None, None)

            return

    def _CheckSafetyLevelForAbility(self, fighterID, abilitySlotID, targetID=None):
        fighterInSpace = self.shipFighterState.GetFighterInSpaceByID(fighterID)
        if fighterInSpace is None:
            raise ValueError('Cannot activate ability for unknown fighter')
        abilityID = GetAbilityIDForSlot(fighterInSpace.typeID, abilitySlotID)
        effectID = GetDogmaEffectIDForAbilityID(abilityID)
        effect = cfg.dgmeffects.Get(effectID)
        requiredSafetyLevel = self.crimewatchSvc.GetRequiredSafetyLevelForEffect(effect, targetID)
        if not self.consider.SafetyCheckPasses(requiredSafetyLevel):
            abilityNameID = GetAbilityNameIDForSlot(fighterInSpace.typeID, abilitySlotID)
            raise UserError('CannotActivateAbilityViolatesSafety', {'fighterTypeID': fighterInSpace.typeID,
             'abilityNameID': abilityNameID})
        return

    def ActivateAbilitySlotsOnTarget(self, fighterIDs, abilitySlotID, targetID):
        if not targetID:
            fighterInSpace = self.shipFighterState.GetFighterInSpaceByID(fighterIDs[0])
            abilityNameID = GetAbilityNameIDForSlot(fighterInSpace.typeID, abilitySlotID)
            raise UserError('CannotActivateAbilityRequiresTarget', {'fighterTypeID': fighterInSpace.typeID,
             'abilityNameID': abilityNameID})
        [ self._CheckSafetyLevelForAbility(fighterID, abilitySlotID) for fighterID in fighterIDs ]
        errorsByFighterID = self._ActivateAbilitySlots(fighterIDs, abilitySlotID, targetID)
        for fighterID, error in errorsByFighterID.iteritems():
            if not error:
                self.shipFighterState.OnAbilityActivatedAtTarget(fighterID, abilitySlotID, targetID)

    def ActivateAbilitySlotsOnSelf(self, fighterIDs, abilitySlotID):
        [ self._CheckSafetyLevelForAbility(fighterID, abilitySlotID) for fighterID in fighterIDs ]
        self._ActivateAbilitySlots(fighterIDs, abilitySlotID)

    def ActivateAbilitySlotsAtPoint(self, fighterIDs, abilitySlotID, selectedPoint):
        [ self._CheckSafetyLevelForAbility(fighterID, abilitySlotID) for fighterID in fighterIDs ]
        self._ActivateAbilitySlots(fighterIDs, abilitySlotID, selectedPoint)

    def _ActivateAbilitySlots(self, fighterIDs, abilitySlotID, *abilityArgs, **abilityKwargs):
        if not fighterIDs:
            return
        fighterMgr = sm.RemoteSvc('fighterMgr')
        errorsByFighterID = fighterMgr.CmdActivateAbilitySlots(fighterIDs, abilitySlotID, *abilityArgs, **abilityKwargs)
        for fighterID, error in errorsByFighterID.iteritems():
            if error:
                sm.GetService('gameui').OnRemoteMessage(*error.args)
            else:
                self.shipFighterState.OnAbilityActivationPending(fighterID, abilitySlotID)

        return errorsByFighterID

    def DeactivateAbilitySlots(self, fighterIDs, abilitySlotID):
        if not fighterIDs:
            return
        fighterMgr = sm.RemoteSvc('fighterMgr')
        errorsByFighterID = fighterMgr.CmdDeactivateAbilitySlots(fighterIDs, abilitySlotID)
        for fighterID, error in errorsByFighterID.iteritems():
            if error:
                sm.GetService('gameui').OnRemoteMessage(*error.args)
            else:
                self.shipFighterState.OnAbilityDeactivationPending(fighterID, abilitySlotID)

    def LaunchAllFighters(self):
        tubeIDsToLaunch = self.shipFighterState.fightersInLaunchTubes.keys()
        self.LaunchFightersFromTubes(tubeIDsToLaunch)

    def RecallAllFightersToTubes(self):
        fighterIDsInSpace = self.shipFighterState.GetAllFighterIDsInSpace()
        self.RecallFightersToTubes(fighterIDsInSpace)

    def RecallAllFightersAndOrbit(self):
        fighterIDsInSpace = self.shipFighterState.GetAllFighterIDsInSpace()
        self.CmdReturnAndOrbit(fighterIDsInSpace)

    def AbandonFighter(self, fighterID):
        if eve.Message('ConfirmAbandonFighter', {}, YESNO) != ID_YES:
            return
        return sm.RemoteSvc('fighterMgr').CmdAbandonFighter(fighterID)

    def ScoopAbandonedFighterFromSpace(self, fighterID, toFlagID):
        return sm.RemoteSvc('fighterMgr').CmdScoopAbandonedFighterFromSpace(fighterID, toFlagID)

    def OnStateChange(self, itemID, flag, status, *args):
        if flag == states.selected and status:
            if itemID in self.shipFighterState.GetAllFighterIDsInSpace() or itemID == session.shipid:
                if not uicore.uilib.Key(uiconst.VK_CONTROL):
                    movementFunctions.DeselectAllForNavigation()
                movementFunctions.SelectForNavigation(itemID)