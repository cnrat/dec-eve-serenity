# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\client\script\graphics\graphicWrappers\loadAndWrap.py
import trinity
import log
import weakref
loadedObjects = weakref.WeakKeyDictionary()

def LoadAndWrap(resPath, urgent=False, convertSceneType=True):
    resPath = str(resPath)
    if urgent:
        triObject = trinity.LoadUrgent(resPath)
    else:
        triObject = trinity.Load(resPath)
    if triObject:
        return Wrap(triObject, resPath, convertSceneType=convertSceneType)
    log.LogError('Unable to load', resPath)


def Wrap(triObject, resPath=None, convertSceneType=True):
    import graphicWrappers
    resPath = str(resPath)
    wrapper = getattr(graphicWrappers, triObject.__typename__, None)
    if hasattr(wrapper, 'ConvertToInterior'):
        triObject = wrapper.ConvertToInterior(triObject, resPath)
        wrapper = getattr(graphicWrappers, triObject.__typename__, None)
    if wrapper:
        obj = wrapper.Wrap(triObject, resPath)
        if getattr(prefs, 'http', False):
            loadedObjects[obj] = True
        return obj
    else:
        return


def GetLoadedObjects():
    return loadedObjects


exports = {'graphicWrappers.LoadAndWrap': LoadAndWrap,
 'graphicWrappers.Wrap': Wrap,
 'graphicWrappers.GetLoadedObjects': GetLoadedObjects}