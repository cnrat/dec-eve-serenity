# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\spaceObject\forceField.py
from eve.client.script.environment.spaceObject.spaceObject import SpaceObject
import blue

class ForceField(SpaceObject):

    def Assemble(self):
        self.model.boundingSphereRadius = 0.5
        self.model.scaling = (self.radius * 2, self.radius * 2, self.radius * 2)
        timeNow = blue.os.GetSimTime()
        timeStart = self.typeData.get('slimItem').forcefieldStartTime
        if timeStart is None:
            return
        else:
            if blue.os.TimeDiffInMs(timeStart, timeNow) > 10000.0:
                for cs in self.model.curveSets:
                    cs.PlayFrom(10.0)

            return