# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\assets\assetSafetyControllers.py


class SafetyControllerCharacter(object):

    def GetItemsInSafety(self):
        return sm.GetService('assetSafety').GetItemsInSafetyForCharacter()


class SafetyControllerCorp(object):

    def GetItemsInSafety(self):
        return sm.GetService('assetSafety').GetItemsInSafetyForCorp()