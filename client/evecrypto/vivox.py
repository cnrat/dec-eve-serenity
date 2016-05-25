# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\evecrypto\vivox.py
import base64
import binascii
import blue
import cPickle
from . import settings
from .crypto import GetCryptoContext

def get_vivox_public_key():
    pass


def vivox_sign(data):
    hashed = blue.crypto.CryptCreateHash(GetCryptoContext(), settings.cryptoAPI_CALG_hashMethod, None, 0)
    blue.crypto.CryptHashData(hashed, data, 0)
    sign = blue.crypto.CryptSignHash(hashed, blue.crypto.AT_KEYEXCHANGE, 0)
    return base64.encodestring(sign).replace('\n', '')


def vivox_verify(data, signature):
    cryptoContext = blue.crypto.CryptAcquireContext(None, blue.crypto.MS_ENHANCED_PROV, blue.crypto.PROV_RSA_FULL, blue.crypto.CRYPT_VERIFYCONTEXT | blue.crypto.CRYPT_SILENT)
    loadedkey = cPickle.loads(binascii.a2b_hex(get_vivox_public_key()))
    importedkey = blue.crypto.CryptImportKey(cryptoContext, loadedkey, None, 0)
    sign = base64.decodestring(signature)
    hashed = blue.crypto.CryptCreateHash(cryptoContext, blue.crypto.CALG_SHA, None, 0)
    blue.crypto.CryptHashData(hashed, data, 0)
    return blue.crypto.CryptVerifySignature(hashed, sign, importedkey, 0)