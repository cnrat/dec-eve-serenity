# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\industry\enum.py
import sys as _sys
__all__ = ['Enum', 'IntEnum', 'unique']
pyver = float('%s.%s' % _sys.version_info[:2])
try:
    any
except NameError:

    def any(iterable):
        for element in iterable:
            if element:
                return True

        return False


try:
    from collections import OrderedDict
except ImportError:
    OrderedDict = None

try:
    basestring
except NameError:
    basestring = str

class _RouteClassAttributeToGetattr(object):

    def __init__(self, fget=None):
        self.fget = fget

    def __get__(self, instance, ownerclass=None):
        if instance is None:
            raise AttributeError()
        return self.fget(instance)

    def __set__(self, instance, value):
        raise AttributeError("can't set attribute")

    def __delete__(self, instance):
        raise AttributeError("can't delete attribute")


def _is_descriptor(obj):
    return hasattr(obj, '__get__') or hasattr(obj, '__set__') or hasattr(obj, '__delete__')


def _is_dunder(name):
    return name[:2] == name[-2:] == '__' and name[2:3] != '_' and name[-3:-2] != '_' and len(name) > 4


def _is_sunder(name):
    return name[0] == name[-1] == '_' and name[1:2] != '_' and name[-2:-1] != '_' and len(name) > 2


def _make_class_unpicklable(cls):

    def _break_on_call_reduce(self, protocol=None):
        raise TypeError('%r cannot be pickled' % self)

    cls.__reduce_ex__ = _break_on_call_reduce
    cls.__module__ = '<unknown>'
    return


class _EnumDict(dict):

    def __init__(self):
        super(_EnumDict, self).__init__()
        self._member_names = []

    def __setitem__(self, key, value):
        if pyver >= 3.0 and key == '__order__':
            return
        if _is_sunder(key):
            raise ValueError('_names_ are reserved for future Enum use')
        elif _is_dunder(key):
            pass
        elif key in self._member_names:
            raise TypeError('Attempted to reuse key: %r' % key)
        elif not _is_descriptor(value):
            if key in self:
                raise TypeError('Key already defined as: %r' % self[key])
            self._member_names.append(key)
        super(_EnumDict, self).__setitem__(key, value)


Enum = None

class EnumMeta(type):

    @classmethod
    def __prepare__(metacls, cls, bases):
        return _EnumDict()

    def __new__(metacls, cls, bases, classdict):
        if type(classdict) is dict:
            original_dict = classdict
            classdict = _EnumDict()
            for k, v in original_dict.items():
                classdict[k] = v

        member_type, first_enum = metacls._get_mixins_(bases)
        __new__, save_new, use_args = metacls._find_new_(classdict, member_type, first_enum)
        members = dict(((k, classdict[k]) for k in classdict._member_names))
        for name in classdict._member_names:
            del classdict[name]

        __order__ = classdict.get('__order__')
        if __order__ is None:
            __order__ = classdict._member_names
            if pyver < 3.0:
                order_specified = False
            else:
                order_specified = True
        else:
            del classdict['__order__']
            order_specified = True
            if pyver < 3.0:
                __order__ = __order__.replace(',', ' ').split()
                aliases = [ name for name in members if name not in __order__ ]
                __order__ += aliases
        invalid_names = set(members) & set(['mro'])
        if invalid_names:
            raise ValueError('Invalid enum member name(s): %s' % (', '.join(invalid_names),))
        enum_class = super(EnumMeta, metacls).__new__(metacls, cls, bases, classdict)
        enum_class._member_names_ = []
        if order_specified and OrderedDict is not None:
            enum_class._member_map_ = OrderedDict()
        else:
            enum_class._member_map_ = {}
        enum_class._member_type_ = member_type
        enum_class._value2member_map_ = {}
        if __new__ is None:
            __new__ = enum_class.__new__
        for member_name in __order__:
            value = members[member_name]
            if not isinstance(value, tuple):
                args = (value,)
            else:
                args = value
            if member_type is tuple:
                args = (args,)
            if not use_args or not args:
                enum_member = __new__(enum_class)
                if not hasattr(enum_member, '_value_'):
                    enum_member._value_ = value
            else:
                enum_member = __new__(enum_class, *args)
                if not hasattr(enum_member, '_value_'):
                    enum_member._value_ = member_type(*args)
            value = enum_member._value_
            enum_member._name_ = member_name
            enum_member.__objclass__ = enum_class
            enum_member.__init__(*args)
            for name, canonical_member in enum_class._member_map_.items():
                if canonical_member.value == enum_member._value_:
                    enum_member = canonical_member
                    break
            else:
                enum_class._member_names_.append(member_name)

            enum_class._member_map_[member_name] = enum_member
            try:
                enum_class._value2member_map_[value] = enum_member
            except TypeError:
                pass

        if not order_specified:
            enum_class._member_names_ = [ e[0] for e in sorted([ (name, enum_class._member_map_[name]) for name in enum_class._member_names_ ], key=lambda t: t[1]._value_) ]
        if Enum is not None:
            setattr(enum_class, '__getnewargs__', Enum.__getnewargs__)
            setattr(enum_class, '__reduce_ex__', Enum.__reduce_ex__)
        for name in ('__repr__', '__str__', '__format__'):
            class_method = getattr(enum_class, name)
            obj_method = getattr(member_type, name, None)
            enum_method = getattr(first_enum, name, None)
            if obj_method is not None and obj_method is class_method:
                setattr(enum_class, name, enum_method)

        if member_type is not object:
            methods = ('__getnewargs_ex__', '__getnewargs__', '__reduce_ex__', '__reduce__')
            if not any(map(member_type.__dict__.get, methods)):
                _make_class_unpicklable(enum_class)
        if pyver < 2.6:
            if issubclass(enum_class, int):
                setattr(enum_class, '__cmp__', getattr(int, '__cmp__'))
        elif pyver < 3.0:
            if issubclass(enum_class, int):
                for method in ('__le__', '__lt__', '__gt__', '__ge__', '__eq__', '__ne__', '__hash__'):
                    setattr(enum_class, method, getattr(int, method))

        if Enum is not None:
            if save_new:
                setattr(enum_class, '__member_new__', enum_class.__dict__['__new__'])
            setattr(enum_class, '__new__', Enum.__dict__['__new__'])
        return enum_class

    def __call__(cls, value, names=None, module=None, type=None):
        if names is None:
            return cls.__new__(cls, value)
        else:
            return cls._create_(value, names, module=module, type=type)

    def __contains__(cls, member):
        return isinstance(member, cls) and member.name in cls._member_map_

    def __delattr__(cls, attr):
        if attr in cls._member_map_:
            raise AttributeError('%s: cannot delete Enum member.' % cls.__name__)
        super(EnumMeta, cls).__delattr__(attr)

    def __dir__(self):
        return ['__class__',
         '__doc__',
         '__members__',
         '__module__'] + self._member_names_

    @property
    def __members__(cls):
        return cls._member_map_.copy()

    def __getattr__(cls, name):
        if _is_dunder(name):
            raise AttributeError(name)
        try:
            return cls._member_map_[name]
        except KeyError:
            raise AttributeError(name)

    def __getitem__(cls, name):
        return cls._member_map_[name]

    def __iter__(cls):
        return (cls._member_map_[name] for name in cls._member_names_)

    def __reversed__(cls):
        return (cls._member_map_[name] for name in reversed(cls._member_names_))

    def __len__(cls):
        return len(cls._member_names_)

    def __repr__(cls):
        return '<enum %r>' % cls.__name__

    def __setattr__(cls, name, value):
        member_map = cls.__dict__.get('_member_map_', {})
        if name in member_map:
            raise AttributeError('Cannot reassign members.')
        super(EnumMeta, cls).__setattr__(name, value)

    def _create_(cls, class_name, names=None, module=None, type=None):
        metacls = cls.__class__
        if type is None:
            bases = (cls,)
        else:
            bases = (type, cls)
        classdict = metacls.__prepare__(class_name, bases)
        __order__ = []
        if isinstance(names, basestring):
            names = names.replace(',', ' ').split()
        if isinstance(names, (tuple, list)) and isinstance(names[0], basestring):
            names = [ (e, i + 1) for i, e in enumerate(names) ]
        for item in names:
            if isinstance(item, basestring):
                member_name, member_value = item, names[item]
            else:
                member_name, member_value = item
            classdict[member_name] = member_value
            __order__.append(member_name)

        if not isinstance(item, basestring):
            classdict['__order__'] = ' '.join(__order__)
        enum_class = metacls.__new__(metacls, class_name, bases, classdict)
        if module is None:
            try:
                module = _sys._getframe(2).f_globals['__name__']
            except (AttributeError, ValueError):
                pass

        if module is None:
            _make_class_unpicklable(enum_class)
        else:
            enum_class.__module__ = module
        return enum_class

    @staticmethod
    def _get_mixins_(bases):
        if not bases or Enum is None:
            return (object, Enum)
        else:
            member_type = first_enum = None
            for base in bases:
                if base is not Enum and issubclass(base, Enum) and base._member_names_:
                    raise TypeError('Cannot extend enumerations')

            if not issubclass(base, Enum):
                raise TypeError('new enumerations must be created as `ClassName([mixin_type,] enum_type)`')
            if not issubclass(bases[0], Enum):
                member_type = bases[0]
                first_enum = bases[-1]
            else:
                for base in bases[0].__mro__:
                    if issubclass(base, Enum):
                        if first_enum is None:
                            first_enum = base
                    elif member_type is None:
                        member_type = base

            return (member_type, first_enum)

    if pyver < 3.0:

        @staticmethod
        def _find_new_(classdict, member_type, first_enum):
            __new__ = classdict.get('__new__', None)
            if __new__:
                return (None, True, True)
            else:
                N__new__ = getattr(None, '__new__')
                O__new__ = getattr(object, '__new__')
                if Enum is None:
                    E__new__ = N__new__
                else:
                    E__new__ = Enum.__dict__['__new__']
                for method in ('__member_new__', '__new__'):
                    for possible in (member_type, first_enum):
                        try:
                            target = possible.__dict__[method]
                        except (AttributeError, KeyError):
                            target = getattr(possible, method, None)

                        if target not in [None,
                         N__new__,
                         O__new__,
                         E__new__]:
                            if method == '__member_new__':
                                classdict['__new__'] = target
                                return (None, False, True)
                            if isinstance(target, staticmethod):
                                target = target.__get__(member_type)
                            __new__ = target
                            break

                    if __new__ is not None:
                        break
                else:
                    __new__ = object.__new__

                if __new__ is object.__new__:
                    use_args = False
                else:
                    use_args = True
                return (__new__, False, use_args)

    else:

        @staticmethod
        def _find_new_(classdict, member_type, first_enum):
            __new__ = classdict.get('__new__', None)
            save_new = __new__ is not None
            if __new__ is None:
                for method in ('__member_new__', '__new__'):
                    for possible in (member_type, first_enum):
                        target = getattr(possible, method, None)
                        if target not in (None,
                         None.__new__,
                         object.__new__,
                         Enum.__new__):
                            __new__ = target
                            break

                    if __new__ is not None:
                        break
                else:
                    __new__ = object.__new__

            if __new__ is object.__new__:
                use_args = False
            else:
                use_args = True
            return (__new__, save_new, use_args)


temp_enum_dict = {}
temp_enum_dict['__doc__'] = 'Generic enumeration.\n\n    Derive from this class to define new enumerations.\n\n'

def __new__(cls, value):
    if type(value) is cls:
        value = value.value
    try:
        if value in cls._value2member_map_:
            return cls._value2member_map_[value]
    except TypeError:
        for member in cls._member_map_.values():
            if member.value == value:
                return member

    raise ValueError('%s is not a valid %s' % (value, cls.__name__))


temp_enum_dict['__new__'] = __new__
del __new__

def __repr__(self):
    return '<%s.%s: %r>' % (self.__class__.__name__, self._name_, self._value_)


temp_enum_dict['__repr__'] = __repr__
del __repr__

def __str__(self):
    return '%s.%s' % (self.__class__.__name__, self._name_)


temp_enum_dict['__str__'] = __str__
del __str__

def __dir__(self):
    added_behavior = [ m for m in self.__class__.__dict__ if m[0] != '_' ]
    return ['__class__',
     '__doc__',
     '__module__',
     'name',
     'value'] + added_behavior


temp_enum_dict['__dir__'] = __dir__
del __dir__

def __format__(self, format_spec):
    if self._member_type_ is object:
        cls = str
        val = str(self)
    else:
        cls = self._member_type_
        val = self.value
    return cls.__format__(val, format_spec)


temp_enum_dict['__format__'] = __format__
del __format__
if pyver < 2.6:

    def __cmp__(self, other):
        if type(other) is self.__class__:
            if self is other:
                return 0
            return -1
        return NotImplemented


    temp_enum_dict['__cmp__'] = __cmp__
    del __cmp__
else:

    def __le__(self, other):
        raise TypeError('unorderable types: %s() <= %s()' % (self.__class__.__name__, other.__class__.__name__))


    temp_enum_dict['__le__'] = __le__
    del __le__

    def __lt__(self, other):
        raise TypeError('unorderable types: %s() < %s()' % (self.__class__.__name__, other.__class__.__name__))


    temp_enum_dict['__lt__'] = __lt__
    del __lt__

    def __ge__(self, other):
        raise TypeError('unorderable types: %s() >= %s()' % (self.__class__.__name__, other.__class__.__name__))


    temp_enum_dict['__ge__'] = __ge__
    del __ge__

    def __gt__(self, other):
        raise TypeError('unorderable types: %s() > %s()' % (self.__class__.__name__, other.__class__.__name__))


    temp_enum_dict['__gt__'] = __gt__
    del __gt__

def __eq__(self, other):
    if type(other) is self.__class__:
        return self is other
    return NotImplemented


temp_enum_dict['__eq__'] = __eq__
del __eq__

def __ne__(self, other):
    if type(other) is self.__class__:
        return self is not other
    return NotImplemented


temp_enum_dict['__ne__'] = __ne__
del __ne__

def __getnewargs__(self):
    return (self._value_,)


temp_enum_dict['__getnewargs__'] = __getnewargs__
del __getnewargs__

def __hash__(self):
    return hash(self._name_)


temp_enum_dict['__hash__'] = __hash__
del __hash__

def __reduce_ex__(self, proto):
    return (self.__class__, self.__getnewargs__())


temp_enum_dict['__reduce_ex__'] = __reduce_ex__
del __reduce_ex__

@_RouteClassAttributeToGetattr
def name(self):
    return self._name_


temp_enum_dict['name'] = name
del name

@_RouteClassAttributeToGetattr
def value(self):
    return self._value_


temp_enum_dict['value'] = value
del value
Enum = EnumMeta('Enum', (object,), temp_enum_dict)
del temp_enum_dict

class IntEnum(int, Enum):
    pass


def unique(enumeration):
    duplicates = []
    for name, member in enumeration.__members__.items():
        if name != member.name:
            duplicates.append((name, member.name))

    if duplicates:
        duplicate_names = ', '.join([ '%s -> %s' % (alias, name) for alias, name in duplicates ])
        raise ValueError('duplicate names found in %r: %s' % (enumeration, duplicate_names))
    return enumeration