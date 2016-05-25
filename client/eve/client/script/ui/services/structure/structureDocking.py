# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\services\structure\structureDocking.py
import service

class StructureDocking(service.Service):
    __guid__ = 'svc.structureDocking'
    __dependencies__ = ['autoPilot', 'clientDogmaIM', 'gameui']

    @property
    def dogmaLocation(self):
        return self.clientDogmaIM.GetDogmaLocation()

    def Undock(self, structureID):
        if session.structureid and session.solarsystemid and structureID == session.structureid:
            if session.shipid == session.structureid:
                shipID = None
            else:
                shipID = session.shipid
            sm.RemoteSvc('structureDocking').Undock(session.structureid, shipID)
        return

    def Dock(self, structureID):

        def RequestDocking():
            if session.shipid and session.solarsystemid:
                sm.RemoteSvc('structureDocking').Dock(structureID, session.shipid)

        self.autoPilot.NavigateSystemTo(structureID, 2500, RequestDocking)

    def ActivateShip(self, shipID):
        if session.structureid:
            typeID = sm.GetService('invCache').GetInventoryFromId(shipID).GetTypeID()
            self.dogmaLocation.CheckSkillRequirementsForType(None, typeID, 'ShipHasSkillPrerequisites')
            self.dogmaLocation.MakeShipActive(shipID)
        return

    def LeaveShip(self, shipID):
        if session.structureid:
            capsuleID = self.gameui.GetShipAccess().LeaveShip(shipID)
            self.dogmaLocation.MakeShipActive(capsuleID)