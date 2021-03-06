# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\client\script\util\debugSelectionClient.py
import service
import carbonui.const as uiconst
import uiprimitives
import uicontrols

class DebugSelectionWindow(uicontrols.Window):
    __guid__ = 'uicls.DebugSelectionWindow'
    default_windowID = 'DebugSelectionWindow'
    default_width = 420
    default_height = 110

    def ApplyAttributes(self, attributes):
        super(DebugSelectionWindow, self).ApplyAttributes(attributes)
        self.SetMinSize([40, self.default_height])
        self.SetCaption('Debug Selection')
        self.sr.content.padding = 5
        self.debugSelectionClient = sm.GetService('debugSelectionClient')
        self.debugSelectionClient._SetUpdateFunc(self._UpdateSelectionEntity)
        self.displayName = uicontrols.Label(parent=self.sr.content, align=uiconst.TOTOP, text=' ', padding=(0, 5, 0, 5))
        topContainer = uiprimitives.Container(parent=self.sr.content, align=uiconst.CENTER, height=25)
        bottomContainer = uiprimitives.Container(parent=self.sr.content, align=uiconst.CENTERBOTTOM, height=25)
        width = 0
        width += uicontrols.Button(parent=topContainer, align=uiconst.TOLEFT, label='Select Player', padding=(2, 0, 2, 0), func=self._SelectPlayer).width + 4
        width += uicontrols.Button(parent=topContainer, align=uiconst.TOLEFT, label='Select Target', padding=(2, 0, 2, 0), func=self._SelectSelected).width
        width += uicontrols.Button(parent=topContainer, align=uiconst.TOLEFT, label='Clear Selection', padding=(2, 0, 2, 0), func=self._ClearSelection).width + 4
        topContainer.width = width
        width = 0
        width += uicontrols.Button(parent=bottomContainer, align=uiconst.TOLEFT, label='Select Previous', padding=(2, 0, 2, 0), func=self._SelectPrevious).width + 4
        width += uicontrols.Button(parent=bottomContainer, align=uiconst.TOLEFT, label='Select Next', padding=(2, 0, 2, 0), func=self._SelectNext).width + 4
        bottomContainer.width = width
        self.SetMinSize([max(bottomContainer.width, topContainer.width) + 10, self.default_height])
        self._UpdateSelectionEntity(self.debugSelectionClient.GetSelectedID(), ' ')

    def _UpdateSelectionEntity(self, entityID, entityName):
        if entityID is None:
            self.displayName.text = ' '
        else:
            self.displayName.text = '%s (%s)' % (entityName, entityID)
        return

    def _ClearSelection(self, *args):
        self.debugSelectionClient.ClearSelection()

    def _SelectPlayer(self, *args):
        self.debugSelectionClient.SelectPlayer()

    def _SelectSelected(self, *args):
        self.debugSelectionClient.SelectSelected()

    def _SelectNext(self, *args):
        self.debugSelectionClient.SelectNext()

    def _SelectPrevious(self, *args):
        self.debugSelectionClient.SelectPrevious()


class debugSelectionClient(service.Service):
    __guid__ = 'svc.debugSelectionClient'
    __dependencies__ = ['entityClient']
    __notifyevents__ = ['OnSessionChanged']

    def __init__(self, *args):
        service.Service.__init__(self, *args)
        self.selectedEntityID = None
        self.updateFunc = None
        return

    def OnSessionChanged(self, isRemote, session, change):
        if 'worldspaceid' in change:
            if session.charid is not None:
                self.selectedEntityID = session.charid
        return

    def Run(self, *args):
        service.Service.Run(self, *args)

    def _GetEntityName(self, entityID):
        pass

    def _SetUpdateFunc(self, func):
        self.updateFunc = func

    def _SetEntityID(self, entityID):
        oldID = self.selectedEntityID
        self.selectedEntityID = entityID
        if self.updateFunc is not None:
            self.updateFunc(self.selectedEntityID, self._GetEntityName(self.selectedEntityID))
        if oldID is not entityID:
            sm.ScatterEvent('OnDebugSelectionChanged', entityID)
        return

    def ClearSelection(self):
        self._SetEntityID(None)
        return

    def SelectSelected(self):
        if boot.appname == 'WOD':
            entityID = sm.GetService('selection').GetSelectedEntID()
        else:
            entityID = sm.GetService('selectionClient').GetSelectedEntityID()
        if entityID == 0:
            self.ClearSelection()
        else:
            self._SetEntityID(entityID)

    def SelectPlayer(self):
        entity = self.entityClient.GetPlayerEntity()
        if entity is not None:
            self._SetEntityID(entity.entityID)
        else:
            self._SetEntityID(None)
        return

    def SelectPrevious(self):
        if self.selectedEntityID is None:
            playerEntity = self.entityClient.GetPlayerEntity()
            entityList = self.entityClient.GetEntityIdsInScene(playerEntity.scene.sceneID)
            entityID = entityList[-1]
        else:
            entity = self.GetSelectedEntity()
            entityList = self.entityClient.GetEntityIdsInScene(entity.scene.sceneID)
            try:
                index = entityList.index(self.selectedEntityID)
                listLength = len(entityList)
                entityID = entityList[(index + listLength - 1) % listLength]
            except:
                entityID = entityList[-1]

        self._SetEntityID(entityID)
        return

    def SelectNext(self):
        if self.selectedEntityID is None:
            playerEntity = self.entityClient.GetPlayerEntity()
            entityList = self.entityClient.GetEntityIdsInScene(playerEntity.scene.sceneID)
            entityID = entityList[0]
        else:
            entity = self.GetSelectedEntity()
            entityList = self.entityClient.GetEntityIdsInScene(entity.scene.sceneID)
            try:
                index = entityList.index(self.selectedEntityID)
                entityID = entityList[(index + 1) % len(entityList)]
            except:
                entityID = entityList[0]

        self._SetEntityID(entityID)
        return

    def GetSelectedID(self):
        return self.selectedEntityID

    def GetSelectedEntity(self):
        return self.entityClient.FindEntityByID(self.selectedEntityID)