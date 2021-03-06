# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\entities\AI\decisionCommon.py
import zaction
import GameWorld
import collections
import carbon.common.script.entities.AI.decisionProcs as decisionProcs

class DecisionComponent(zaction.ActionComponent):
    __guid__ = 'ai.DecisionComponent'
    rootIDs = []
    instances = []


class DecisionTreeCommon(zaction.zactionCommonBase):
    __guid__ = 'ai.decisionTreeCommon'
    __componentTypes__ = ['decision']

    @classmethod
    def GetTreeSystemID(cls):
        return const.ztree.TREE_SYSTEM_ID_DICT[const.ai.AI_SCHEMA]

    def __init__(self):
        treeManager = GameWorld.DecisionTreeManager()
        treeManager.Initialize()
        zaction.zactionCommon.__init__(self, treeManager)
        GameWorld.RegisterPythonActionProc('ForceDecisionTreeToRoot', decisionProcs.ForceDecisionTreeToRootFunc, ('ENTID',))

    def RegisterComponent(self, entity, component):
        for index in range(const.ai.DECISION_MAX_INSTANCES):
            if component.instances[index] is not None:
                self.treeManager.AddTreeInstanceWithDebug(component.instances[index], self.createDebugItems)
                treeNode = self.treeManager.GetTreeNodeByID(component.rootIDs[index])
                component.instances[index].SetDefaultActionID(component.rootIDs[index])
                component.instances[index].ForceAction(treeNode)

        return

    def UnRegisterComponent(self, entity, component):
        for index in range(const.ai.DECISION_MAX_INSTANCES):
            if component.instances[index] is not None:
                self.treeManager.RemoveTreeInstance(component.instances[index])

        return

    def ReportState(self, component, entity):
        report = collections.OrderedDict()
        for index in range(const.ai.DECISION_MAX_INSTANCES):
            if component.instances[index] is not None:
                report['Type'] = const.ai.DECISION_TYPE_NAMES[index]
                report['Current Decision'] = '???'
                report['RootNode ID'] = component.rootIDs[index]
                if component.instances[index]:
                    decisionTreeNode = component.instances[index].GetCurrentTreeNode()
                    if decisionTreeNode and component.instances[index].debugItem:
                        report['CurrentNode'] = 'name=%s  duration=%f' % (decisionTreeNode.name, component.instances[index].debugItem.duration)
                    else:
                        report['CurrentNode'] = decisionTreeNode.name

        return report