# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\paperDoll\AvatarGhost.py
import trinity
import blue
from eve.common.script.paperDoll.paperDollCommonFunctions import Yield

class AvatarGhost(object):
    __guid__ = 'paperDoll.AvatarGhost'
    renderStepSlot = None

    def __init__(self):
        pass

    def __del__(self):
        self.StopGhostRenderJob()

    def StopGhostRenderJob(self):
        if hasattr(self, 'ghostRJ') and self.ghostRJ is not None:
            if AvatarGhost.renderStepSlot is not None and AvatarGhost.renderStepSlot.object is not None:
                AvatarGhost.renderStepSlot.object.job = None
            else:
                self.ghostRJ.UnscheduleRecurring()
            self.ghostRJ = None
        return

    def StartGhostRenderJob(self, avatar, fxPath, rjName='Avatar Ghost', meshFilter=None, insertFront=True):
        self.StopGhostRenderJob()
        if avatar is None or avatar.visualModel is None or not avatar.visualModel.meshes:
            return
        else:
            rj = trinity.CreateRenderJob(rjName)
            self.ghostRJ = rj
            self.avatar = avatar.CloneTo()
            self.avatar.clothMeshes.removeAt(-1)
            self.avatar.rotation = avatar.rotation
            self.avatar.translation = avatar.translation
            self.avatar.animationUpdater = avatar.animationUpdater
            for meshIx in xrange(len(avatar.visualModel.meshes)):
                mesh = avatar.visualModel.meshes[meshIx]
                self.avatar.visualModel.meshes[meshIx].SetGeometryRes(mesh.geometry)

            effect = trinity.Tr2Effect()
            effect.effectFilePath = fxPath
            effect.PopulateParameters()
            effect.RebuildCachedData()
            while effect.effectResource.isLoading:
                Yield()

            fx = []
            index = 0
            while index < len(self.avatar.visualModel.meshes):
                mesh = self.avatar.visualModel.meshes[index]
                if meshFilter is not None and not meshFilter(mesh):
                    self.avatar.visualModel.meshes.removeAt(index)
                else:
                    index = index + 1
                    areasList = [mesh.opaqueAreas, mesh.decalAreas, mesh.transparentAreas]
                    for areas in areasList:
                        for area in areas:
                            area.effect = effect
                            fx.append(area.effect)

            self.ghostScene = trinity.WodBakingScene()
            self.ghostScene.Avatar = self.avatar
            rj.SetStdRndStates(trinity.RM_OPAQUE)
            rj.Update(self.ghostScene)
            rj.RenderScene(self.ghostScene)
            if AvatarGhost.renderStepSlot is not None and AvatarGhost.renderStepSlot.object is not None:
                AvatarGhost.renderStepSlot.object.job = rj
            else:
                rj.ScheduleRecurring(insertFront=insertFront)
            return fx

    @staticmethod
    def CreateSculptingStep(renderJob, append=True):
        ghostStep = trinity.TriStepRunJob()
        ghostStep.name = 'Sculpting overlay'
        if append:
            renderJob.steps.append(ghostStep)
        AvatarGhost.renderStepSlot = blue.BluePythonWeakRef(ghostStep)
        return ghostStep