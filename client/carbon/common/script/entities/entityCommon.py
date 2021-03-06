# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\entities\entityCommon.py
import cef
import log
import types
import utillib as util
from carbon.common.script.cef.baseComponentView import BaseComponentView

def GetComponentName(componentID):
    componentView = BaseComponentView.GetComponentViewByID(componentID)
    if type(componentID) is str:
        return componentID
    elif componentView is None:
        log.LogTraceback('UNKNOWN COMPONENT %s' % componentID)
        return 'UNKNOWN COMPONENT %s' % componentID
    else:
        return componentView.__COMPONENT_CODE_NAME__


def GetParentTypeString(parentType):
    if parentType == const.cef.PARENT_TYPEID:
        return 'Type'
    elif parentType == const.cef.PARENT_GROUPID:
        return 'Group'
    elif parentType == const.cef.PARENT_CATEGORYID:
        return 'Category'
    else:
        return 'UNKNOWN'


def GetIngredientInitialValue(initValueRow, tableName=const.cef.INGREDIENT_INITS_TABLE_FULL_NAME):
    if initValueRow.valueInt is not None:
        return initValueRow.valueInt
    elif initValueRow.valueFloat is not None:
        return initValueRow.valueFloat
    elif initValueRow.needsTranslation:
        return (initValueRow.valueString, tableName + '.valueString', initValueRow.dataID)
    else:
        return initValueRow.valueString
        return


def GetDBInitValuesFromValue(value):
    if type(value) is types.IntType:
        return util.KeyVal(valueInt=value, valueFloat=None, valueString=None)
    elif type(value) is types.FloatType:
        return util.KeyVal(valueInt=None, valueFloat=value, valueString=None)
    else:
        if type(value) is not types.StringType:
            try:
                value = str(value)
            except ValueError as e:
                return util.KeyVal(valueInt=None, valueFloat=None, valueString=None)

        try:
            valueInt = int(value)
        except ValueError as e:
            valueInt = None

        if valueInt is not None:
            valueFloat = None
        else:
            try:
                valueFloat = float(value)
            except ValueError as e:
                valueFloat = None

        if valueInt is not None or valueFloat is not None or value.strip() == '':
            value = None
        return util.KeyVal(valueInt=valueInt, valueFloat=valueFloat, valueString=value)


import carbon.common.script.util.autoexport as autoexport
exports = autoexport.AutoExports('entityCommon', locals())