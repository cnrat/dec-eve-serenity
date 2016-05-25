# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\certs.py
import os.path

def where():
    return os.path.join(os.path.dirname(__file__), 'cacert.pem')


if __name__ == '__main__':
    print where()