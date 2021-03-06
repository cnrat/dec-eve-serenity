# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\notifications\common\formatters\achievementTask.py
from achievements.common.achievementLoader import AchievementLoader
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter

class AchievementTaskFormatter(BaseNotificationFormatter):

    @staticmethod
    def MakeData(achievementID):
        return {'achievementID': achievementID}

    def Format(self, notification):
        allAchievements = AchievementLoader().GetAchievements(getDisabled=False)
        data = notification.data
        taskID = data['achievementID']
        taskInfo = allAchievements[taskID]
        subject = taskInfo.notificationText
        if not subject:
            subject = taskInfo.name
        notification.subject = subject

    def MakeSampleData(self):
        from utillib import KeyVal
        msg = KeyVal({'taskName': 'taskNAme',
         'achievementName': 'the notification text!!!'})
        return AchievementTaskFormatter.MakeData(msg)