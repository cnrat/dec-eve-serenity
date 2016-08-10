# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\evegraphics\explosions\spaceObjectExplosionManager.py
import blue
import trinity
import geo2
import uthread
import random
import logging
from evegraphics.fsd.explosionBuckets import GetRandomExplosion, GetExplosionBucketByTypeID
from tacticalNavigation.ballparkFunctions import AddClientBall, RemoveClientBall
log = logging.getLogger(__name__)
RANDOM_LOCATOR_SORTING = 'random'
FROM_CENTER_SORTING = 'fromCenter'
FROM_LOCATOR_SORTING = 'fromLocator'

class SpaceObjectExplosionManager(object):
    USE_EXPLOSION_BUCKETS = False
    BALLPARK_MODE = True
    explosionLinkMap = {}

    @staticmethod
    def SetUpChildExplosion(explosionModel, spaceObjectModel=None, explosionSorting='random', initialLocatorIdx=-1):
        explosionChildren = explosionModel.Find('trinity.EveChildExplosion', 2)
        if spaceObjectModel is not None:
            explosionLocatorSets = None
            if hasattr(spaceObjectModel, 'locatorSets'):
                explosionLocatorSets = spaceObjectModel.locatorSets.FindByName('explosions')
            explosionLocators = explosionLocatorSets.locators if explosionLocatorSets else spaceObjectModel.damageLocators
            locators = [ (each[0], each[1]) for each in explosionLocators ]
            transforms = []
            if explosionSorting == FROM_CENTER_SORTING:
                point = spaceObjectModel.GetBoundingSphereCenter()
                radius = spaceObjectModel.GetBoundingSphereRadius() * 0.2
                locators.sort(key=lambda explosion: geo2.Vec3Distance(point, explosion[0]) + (random.random() - random.random()) * radius)
            elif explosionSorting == FROM_LOCATOR_SORTING:
                if initialLocatorIdx < 0 or initialLocatorIdx > len(locators):
                    initialLocatorIdx = random.randint(0, len(locators) - 1)
                point = locators[initialLocatorIdx][0]
                locators.sort(key=lambda explosion: geo2.Vec3Distance(point, explosion[0]))
            else:
                random.shuffle(locators)
            for position, direction in locators:
                rotation = direction
                transform = geo2.MatrixTransformation((0, 0, 0), (0, 0, 0, 1), (1, 1, 1), (0, 0, 0), rotation, position)
                transforms.append(transform)

            for each in explosionChildren:
                each.SetLocalExplosionTransforms(transforms)

        return

    @staticmethod
    def PlayExplosion(explosionModel):
        explosionChildren = explosionModel.Find('trinity.EveChildExplosion', 2)
        for each in explosionChildren:
            each.Play()

    @staticmethod
    def PlayClientSideExplosionBall(gfxResPath, scene, worldPos, rotation, spaceObjectModel, explosionSorting='random', initialLocatorIdx=-1, explosionLink=None):
        explosionModel = trinity.Load(gfxResPath)
        clientBall = None
        if SpaceObjectExplosionManager.BALLPARK_MODE:
            clientBall = AddClientBall(worldPos)
        if clientBall:
            explosionModel.translationCurve = clientBall
            explosionModel.rotation = rotation
        elif spaceObjectModel:
            explosionModel.translationCurve = spaceObjectModel.translationCurve
            explosionModel.rotationCurve = spaceObjectModel.rotationCurve
        scene.objects.append(explosionModel)
        SpaceObjectExplosionManager.SetUpChildExplosion(explosionModel, spaceObjectModel, explosionSorting, initialLocatorIdx)
        explosionDuration = 60.0
        if isinstance(explosionModel, trinity.EveEffectRoot2):
            for child in explosionModel.effectChildren:
                explosionDuration = max(explosionDuration, getattr(child, 'globalDuration', 0))

        if clientBall:
            uthread.new(SpaceObjectExplosionManager._DelayedBallRemove, clientBall, scene, explosionModel, explosionDuration, explosionLink)
        SpaceObjectExplosionManager.PlayExplosion(explosionModel)
        return (explosionDuration, explosionModel)

    @staticmethod
    def _DelayedBallRemove(clientBall, scene, explosionModel, secTillBallRemove, explosionLink=None):
        blue.synchro.Sleep(secTillBallRemove * 1000)
        scene.objects.fremove(explosionModel)
        RemoveClientBall(clientBall)
        if explosionLink is not None:
            del SpaceObjectExplosionManager.explosionLinkMap[explosionLink]
        return

    @staticmethod
    def ExplodeBucket(explosionBucketID, scene, pos, rotation, spaceObjectModel, initialLocatorIdx=-1, explosionLinkID=None):
        explosion = GetRandomExplosion(explosionBucketID)
        if explosion is None:
            return (0, 0, None)
        else:
            if explosionLinkID is not None:
                SpaceObjectExplosionManager.explosionLinkMap[explosionLinkID] = explosion
            return SpaceObjectExplosionManager.Explode(explosion.filePath, explosion.modelSwitchDelayInMs, scene, pos, rotation, spaceObjectModel, explosion.childExplosionType, initialLocatorIdx, explosionLinkID)

    @staticmethod
    def ExplodeBucketForBall(ball, scene, initialLocatorIdx=-1):
        explosionBucket = GetExplosionBucketByTypeID(ball.typeData['typeID'])
        if not explosionBucket:
            log.warning("ball '%s' (type '%s') doesn't have an explosionbucket assigned" % (ball.id, ball.typeData['typeID']))
            return 0
        rotationQuaternion = ball.GetStaticRotation()
        if rotationQuaternion == geo2.QuaternionIdentity():
            rotationQuaternion = geo2.QuaternionRotationSetYawPitchRoll(ball.yaw, ball.pitch, ball.roll)
        return SpaceObjectExplosionManager.ExplodeBucket(explosionBucket, scene, (ball.x, ball.y, ball.z), rotationQuaternion, ball.model, initialLocatorIdx, explosionLinkID=ball.id)

    @staticmethod
    def Explode(resPath, modelSwitchDelayInMs, scene, pos, rotation, spaceObjectModel, explosionSorting='random', initialLocatorIdx=-1, explosionLink=None):
        explosionDuration, explosionModel = SpaceObjectExplosionManager.PlayClientSideExplosionBall(resPath, scene, pos, rotation, spaceObjectModel, explosionSorting, initialLocatorIdx, explosionLink)
        return (modelSwitchDelayInMs, explosionDuration, explosionModel)

    @staticmethod
    def GetExplosionForBallID(ballID):
        return SpaceObjectExplosionManager.explosionLinkMap.get(ballID, None)