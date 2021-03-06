# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\services\eveSettingsSvc.py
import uicontrols
import log
import svc
import uicls

class EveSettingsSvc(svc.settings):
    __guid__ = 'svc.eveSettings'
    __replaceservice__ = 'settings'

    def LoadSettings(self):
        svc.settings.LoadSettings(self)
        settings.user.CreateGroup('audio')
        settings.user.CreateGroup('overview')
        settings.user.CreateGroup('notifications')
        settings.char.CreateGroup('generic')
        settings.char.CreateGroup('autorepeat')
        settings.char.CreateGroup('autoreload')
        settings.char.CreateGroup('inbox')
        settings.char.CreateGroup('notepad')
        settings.char.CreateGroup('notifications')
        try:
            self.FixListgroupSettings()
        except Exception:
            settings.char.ui.Set('listgroups', {})
            log.LogError('Something happened when fixing listgroups settings and they had to be deleted')

        uicontrols.Window.ValidateSettings()
        return settings

    def FixListgroupSettings(self):
        if not session.charid:
            return
        elif settings.char.ui.Get('listgroupSettingsUpdated', 0):
            return
        else:
            for key, value in settings.char.ui.Get('listgroups', {}).iteritems():
                for key2, value2 in value.iteritems():
                    items = value2.pop('items', None)
                    if items is not None:
                        value2['groupItems'] = items

            settings.char.ui.Set('listgroupSettingsUpdated', 1)
            return