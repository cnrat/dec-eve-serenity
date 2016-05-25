# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\structureBrowser\extaColumnUtil.py
from eve.client.script.ui.station.stationServiceConst import serviceDataByNameID, serviceIDAlwaysPresent
from localization import GetByLabel
import structures

def GetSettingDataObectForServiceName(serviceName):
    serviceData = serviceDataByNameID.get(serviceName, None)
    if not serviceData or serviceData.serviceID == serviceIDAlwaysPresent:
        return
    else:
        settingIDForService = structures.SERVICES_ACCESS_SETTINGS.get(serviceData.serviceID, None)
        if settingIDForService is None:
            return
        settingInfo = structures.SETTING_OBJECT_BY_SETTINGID.get(settingIDForService, None)
        return settingInfo


def GetHeaderForService(serviceName):
    settingData = GetSettingDataObectForServiceName(serviceName)
    if settingData is None:
        return
    else:
        labelPath = settingData.labelPath
        if labelPath:
            return GetByLabel(labelPath)
        return


class ExtraColumnProvider(object):

    def GetColumnText(self, controller, serviceName):
        serviceData = serviceDataByNameID.get(serviceName, None)
        if not serviceData:
            return
        else:
            settingData = GetSettingDataObectForServiceName(serviceName)
            if settingData is None:
                return
            value = controller.GetInfoForExtraColumns(serviceData.serviceID, settingData)
            if value is None:
                return '-'
            text = self.FormatColumnValue(value, settingData.valueType)
            return text

    def FormatColumnValue(self, value, valueType):
        if valueType == structures.SETTINGS_TYPE_INT:
            return int(value)
        if valueType == structures.SETTINGS_TYPE_PERCENTAGE:
            return GetByLabel('UI/Structures/Browser/PercentageText', value=value)
        if valueType == structures.SETTINGS_TYPE_BOOL:
            return bool(value)
        return value