# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\spaceObject\buildableStructure.py
import uthread
from eve.client.script.environment.spaceObject.LargeCollidableStructure import LargeCollidableStructure
from evegraphics.utils import GetResPathFromGraphicID, GetCorrectEffectPath
import locks
import trinity
NANO_CONTAINER_GRAPHIC_ID = 20930

class BuildableStructure(LargeCollidableStructure):

    def __init__(self):
        LargeCollidableStructure.__init__(self)
        self.overlayEffects = {}
        self.nanoContainerModel = None
        self.nanoContainerModelLoadedEvent = locks.Event()
        self.structureModel = None
        self.structureModelLoadedEvent = locks.Event()
        self.isConstructing = False
        self.oldClipSphereCenter = (0.0, 0.0, 0.0)
        return

    def Prepare(self):
        self.LogInfo('BuildableStructure: Preparing')
        self.LoadStructureModel()
        LargeCollidableStructure.Prepare(self)

    def OnDamageState(self, damageState):
        LargeCollidableStructure.OnDamageState(self, damageState)

    def LoadNanoContainerModel(self):
        self.LogInfo('BuildableStructure: Loading nano container model')
        self.nanoContainerModel = self.LoadAdditionalModel(GetResPathFromGraphicID(NANO_CONTAINER_GRAPHIC_ID))
        self.nanoContainerModel.name += '_nanocontainer'
        self.nanoContainerModelLoadedEvent.set()

    def LoadStructureModel(self):
        self.LogInfo('BuildableStructure: Loading structure model')
        self.structureModel = self.LoadAdditionalModel()
        self.structureModelLoadedEvent.set()

    def SetModelDisplay(self, model, display):
        if model is not None:
            model.display = display
        return

    def LoadUnLoadedModels(self):
        if self.structureModel is None:
            self.LoadStructureModel()
        return

    def SetupModel(self, unanchored):
        sendOutModelLoadedEvent = self.model is None
        if self.isConstructing:
            self.model = self.GetStructureModel()
            self.GetNanoContainerModel()
            self.model.display = True
            self.Assemble()
        elif unanchored:
            self.structureModel.display = False
            self.model = self.GetNanoContainerModel()
        else:
            self.model = self.GetStructureModel()
        if sendOutModelLoadedEvent:
            self.NotifyModelLoaded()
        if self.animationSequencer is None:
            self.SetAnimationSequencer(self.model)
        return

    def GetNanoContainerModel(self):
        if self.nanoContainerModel is None:
            self.LoadNanoContainerModel()
        return self.nanoContainerModel

    def GetStructureModel(self):
        if self.structureModel is None:
            self.LogInfo('BuildableStructure: waiting for structure model')
            self.structureModelLoadedEvent.wait()
            self.LogInfo('BuildableStructure: done waiting for structure model')
        if self.structureModel is None:
            self.LogWarn('BuildableStructure: Failed to get a valid structure model')
            return
        else:
            if self.animationSequencer is None:
                self.SetupAnimationInformation(self.structureModel)
            return self.structureModel

    def HasModels(self):
        return self.nanoContainerModel is not None or self.structureModel is not None

    def ClearAndRemoveAllModels(self, scene):
        LargeCollidableStructure.ClearAndRemoveAllModels(self, scene)
        self.RemoveAndClearModel(self.nanoContainerModel, scene)
        self.RemoveAndClearModel(self.structureModel, scene)
        self.nanoContainerModel = None
        self.structureModel = None
        self.model = None
        return

    def RemoveAllModelsFromScene(self, scene):
        LargeCollidableStructure.RemoveAllModelsFromScene(self, scene)
        scene.objects.fremove(self.nanoContainerModel)
        scene.objects.fremove(self.structureModel)

    def PreBuildingSteps(self):
        self.isConstructing = True
        self.SetupModel(False)
        self.StartNanoContainerAnimation()

    def PostBuildingSteps(self, built):
        self.isConstructing = False
        if built:
            self.RemoveAndClearModel(self.nanoContainerModel)
            self.nanoContainerModel = None
        else:
            self.EndNanoContainerAnimation()
        return

    def StartNanoContainerAnimation(self, deployScale=1):
        if self.nanoContainerModel is not None:
            self.nanoContainerModel.PlayAnimationEx('Deploy', 1, 0, deployScale)
            self.nanoContainerModel.ChainAnimationEx('OpenLoop', 0, 0, 1)
        return

    def EndNanoContainerAnimation(self):
        if self.nanoContainerModel is not None:
            self.nanoContainerModel.PlayAnimation('Pack')
        return