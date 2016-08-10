# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\evegraphics\fsd\base.py
import os
try:
    import fsd.schemas.binaryLoader as binaryLoader
except ImportError:
    import site
    branchRoot = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
    site.addsitedir(os.path.abspath(os.path.join(branchRoot, 'packages')))
    import fsd.schemas.binaryLoader as binaryLoader

class BuiltDataLoader(object):
    __binary__ = None
    __resBuiltFile__ = None
    __autobuildBuiltFile__ = None

    @classmethod
    def __LoadBinary(cls):
        try:
            data = binaryLoader.LoadFSDDataForCFG(cls.__resBuiltFile__)
            if data is None:
                raise ImportError
            return data
        except ImportError:
            import devenv
            pathRelativeToBranchRoot = cls.__autobuildBuiltFile__
            autobuildFilePath = os.path.abspath(os.path.join(devenv.BRANCHROOT, pathRelativeToBranchRoot))
            return binaryLoader.LoadFSDDataInPython(autobuildFilePath)

        return

    @classmethod
    def GetData(cls):
        if cls.__binary__ is None:
            cls.__binary__ = cls.__LoadBinary()
        return cls.__binary__