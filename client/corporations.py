# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\lib\corporations.py
from ccp_exceptions import UserError
import appConst as const

def ValidateAccountantRole(role):
    if not role & const.corpRoleAccountant:
        raise UserError('CrpAccessDenied', {'reason': (const.UE_LOC, 'UI/Corporations/AccessRestrictions/NotFullAccountant')})


def ValidateAccountantOrJuniorAccountantRole(role):
    if not role & (const.corpRoleAccountant | const.corpRoleJuniorAccountant):
        raise UserError('CrpAccessDenied', {'reason': (const.UE_LOC, 'UI/Corporations/AccessRestrictions/NotAccountant')})


def ValidateAccountantOrTraderRole(role):
    if not role & (const.corpRoleAccountant | const.corpRoleJuniorAccountant):
        raise UserError('CrpAccessDenied', {'reason': (const.UE_LOC, 'UI/Corporations/AccessRestrictions/NoAccountantOrTrader')})


_CORP_WALLET_DIVISION_ROLES = {1000: const.corpRoleAccountCanTake1,
 1001: const.corpRoleAccountCanTake2,
 1002: const.corpRoleAccountCanTake3,
 1003: const.corpRoleAccountCanTake4,
 1004: const.corpRoleAccountCanTake5,
 1005: const.corpRoleAccountCanTake6,
 1006: const.corpRoleAccountCanTake7,
 10000: const.corpRoleAccountant}

def ValidateCorpWalletDivisionAccess(role, key):
    if key is None:
        raise UserError('CrpAccessDenied', {'reason': (const.UE_LOC, 'UI/Corporations/AccessRestrictions/NoAccessToWalletDivision')})
    if _CORP_WALLET_DIVISION_ROLES[key] & role == 0:
        raise UserError('CrpAccessDenied', {'reason': (const.UE_LOC, 'UI/Corporations/AccessRestrictions/NoAccessToWalletDivision')})
    return


def ValidateCorpWalletDivisionReadAccess(role, key):
    if key is None:
        raise UserError('CrpAccessDenied', {'reason': (const.UE_LOC, 'UI/Corporations/AccessRestrictions/NoAccessToWalletDivision')})
    if _CORP_WALLET_DIVISION_ROLES[key] & role == 0:
        raise UserError('CrpAccessDenied', {'reason': (const.UE_LOC, 'UI/Corporations/AccessRestrictions/NoAccessToWalletDivision')})
    return


def ValidateDirectorRole(role):
    if not role & const.corpRoleDirector:
        raise UserError('CrpAccessDenied', {'reason': (const.UE_LOC, 'UI/Corporations/AccessRestrictions/NotDirector')})