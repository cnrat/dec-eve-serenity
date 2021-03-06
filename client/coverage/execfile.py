# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\coverage\execfile.py
import imp, marshal, os, sys
from coverage.backward import exec_code_object, open_source
from coverage.misc import ExceptionDuringRun, NoCode, NoSource
try:
    BUILTINS = sys.modules['__builtin__']
except KeyError:
    BUILTINS = sys.modules['builtins']

def rsplit1(s, sep):
    parts = s.split(sep)
    return (sep.join(parts[:-1]), parts[-1])


def run_python_module(modulename, args):
    openfile = None
    glo, loc = globals(), locals()
    try:
        try:
            if '.' in modulename:
                packagename, name = rsplit1(modulename, '.')
                package = __import__(packagename, glo, loc, ['__path__'])
                searchpath = package.__path__
            else:
                packagename, name = None, modulename
                searchpath = None
            openfile, pathname, _ = imp.find_module(name, searchpath)
            if openfile is None and pathname is None:
                raise NoSource('module does not live in a file: %r' % modulename)
            if openfile is None:
                packagename = modulename
                name = '__main__'
                package = __import__(packagename, glo, loc, ['__path__'])
                searchpath = package.__path__
                openfile, pathname, _ = imp.find_module(name, searchpath)
        except ImportError:
            _, err, _ = sys.exc_info()
            raise NoSource(str(err))

    finally:
        if openfile:
            openfile.close()

    pathname = os.path.abspath(pathname)
    args[0] = pathname
    run_python_file(pathname, args, package=packagename)
    return


def run_python_file(filename, args, package=None):
    old_main_mod = sys.modules['__main__']
    main_mod = imp.new_module('__main__')
    sys.modules['__main__'] = main_mod
    main_mod.__file__ = filename
    if package:
        main_mod.__package__ = package
    main_mod.__builtins__ = BUILTINS
    old_argv = sys.argv
    sys.argv = args
    try:
        if filename.endswith('.pyc') or filename.endswith('.pyo'):
            code = make_code_from_pyc(filename)
        else:
            code = make_code_from_py(filename)
        try:
            exec_code_object(code, main_mod.__dict__)
        except SystemExit:
            raise
        except:
            typ, err, tb = sys.exc_info()
            raise ExceptionDuringRun(typ, err, tb.tb_next.tb_next)

    finally:
        sys.modules['__main__'] = old_main_mod
        sys.argv = old_argv


def make_code_from_py(filename):
    try:
        source_file = open_source(filename)
    except IOError:
        raise NoSource('No file to run: %r' % filename)

    try:
        source = source_file.read()
    finally:
        source_file.close()

    if not source or source[-1] != '\n':
        source += '\n'
    code = compile(source, filename, 'exec')
    return code


def make_code_from_pyc(filename):
    try:
        fpyc = open(filename, 'rb')
    except IOError:
        raise NoCode('No file to run: %r' % filename)

    try:
        magic = fpyc.read(4)
        if magic != imp.get_magic():
            raise NoCode('Bad magic number in .pyc file')
        fpyc.read(4)
        if sys.version_info >= (3, 3):
            fpyc.read(4)
        code = marshal.load(fpyc)
    finally:
        fpyc.close()

    return code