# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\trinutils\searchpath.py
import contextlib
import blue

@contextlib.contextmanager
def change_search_path_ctx(value, key='res'):

    def get_search_path():
        return blue.paths.GetSearchPath(key)

    def set_search_path(value_):
        blue.paths.SetSearchPath(key, unicode(value_))

    orig = get_search_path()
    set_search_path(value)
    try:
        yield
    finally:
        if orig is not None:
            set_search_path(orig)

    return