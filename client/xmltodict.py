# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\xmltodict.py
from xml.parsers import expat
from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import AttributesImpl
try:
    from cStringIO import StringIO
except ImportError:
    try:
        from StringIO import StringIO
    except ImportError:
        from io import StringIO

try:
    from collections import OrderedDict
except ImportError:
    OrderedDict = dict

try:
    _basestring = basestring
except NameError:
    _basestring = str

try:
    _unicode = unicode
except NameError:
    _unicode = str

__author__ = 'Martin Blech'
__version__ = '0.4.4'
__license__ = 'MIT'

class ParsingInterrupted(Exception):
    pass


class _DictSAXHandler(object):

    def __init__(self, item_depth=0, item_callback=lambda *args: True, xml_attribs=True, attr_prefix='@', cdata_key='#text', force_cdata=False, cdata_separator='', postprocessor=None, dict_constructor=OrderedDict):
        self.path = []
        self.stack = []
        self.data = None
        self.item = None
        self.item_depth = item_depth
        self.xml_attribs = xml_attribs
        self.item_callback = item_callback
        self.attr_prefix = attr_prefix
        self.cdata_key = cdata_key
        self.force_cdata = force_cdata
        self.cdata_separator = cdata_separator
        self.postprocessor = postprocessor
        self.dict_constructor = dict_constructor
        return

    def startElement(self, name, attrs):
        attrs = self.dict_constructor(zip(attrs[0::2], attrs[1::2]))
        self.path.append((name, attrs or None))
        if len(self.path) > self.item_depth:
            self.stack.append((self.item, self.data))
            if self.xml_attribs:
                attrs = self.dict_constructor(((self.attr_prefix + key, value) for key, value in attrs.items()))
            else:
                attrs = None
            self.item = attrs or None
            self.data = None
        return

    def endElement(self, name):
        if len(self.path) == self.item_depth:
            item = self.item
            if item is None:
                item = self.data
            should_continue = self.item_callback(self.path, item)
            if not should_continue:
                raise ParsingInterrupted()
        if len(self.stack):
            item, data = self.item, self.data
            self.item, self.data = self.stack.pop()
            if data and self.force_cdata and item is None:
                item = self.dict_constructor()
            if item is not None:
                if data:
                    self.push_data(item, self.cdata_key, data)
                self.item = self.push_data(self.item, name, item)
            else:
                self.item = self.push_data(self.item, name, data)
        else:
            self.item = self.data = None
        self.path.pop()
        return

    def characters(self, data):
        if not self.data:
            self.data = data
        else:
            self.data += self.cdata_separator + data

    def push_data(self, item, key, data):
        if self.postprocessor is not None:
            result = self.postprocessor(self.path, key, data)
            if result is None:
                return item
            key, data = result
        if item is None:
            item = self.dict_constructor()
        try:
            value = item[key]
            if isinstance(value, list):
                value.append(data)
            else:
                item[key] = [value, data]
        except KeyError:
            item[key] = data

        return item


def parse(xml_input, *args, **kwargs):
    handler = _DictSAXHandler(*args, **kwargs)
    parser = expat.ParserCreate()
    parser.ordered_attributes = True
    parser.StartElementHandler = handler.startElement
    parser.EndElementHandler = handler.endElement
    parser.CharacterDataHandler = handler.characters
    if hasattr(xml_input, 'read'):
        parser.ParseFile(xml_input)
    else:
        parser.Parse(xml_input, True)
    return handler.item


def _emit(key, value, content_handler, attr_prefix='@', cdata_key='#text', root=True, preprocessor=None):
    if preprocessor is not None:
        result = preprocessor(key, value)
        if result is None:
            return
        key, value = result
    if not isinstance(value, (list, tuple)):
        value = [value]
    if root and len(value) > 1:
        raise ValueError('document with multiple roots')
    for v in value:
        if v is None:
            v = OrderedDict()
        elif not isinstance(v, dict):
            v = _unicode(v)
        if isinstance(v, _basestring):
            v = OrderedDict(((cdata_key, v),))
        cdata = None
        attrs = OrderedDict()
        children = []
        for ik, iv in v.items():
            if ik == cdata_key:
                cdata = iv
                continue
            if ik.startswith(attr_prefix):
                attrs[ik[len(attr_prefix):]] = iv
                continue
            children.append((ik, iv))

        content_handler.startElement(key, AttributesImpl(attrs))
        for child_key, child_value in children:
            _emit(child_key, child_value, content_handler, attr_prefix, cdata_key, False, preprocessor)

        if cdata is not None:
            content_handler.characters(cdata)
        content_handler.endElement(key)

    return


def unparse(item, output=None, encoding='utf-8', **kwargs):
    (key, value) = item.items()
    must_return = False
    if output == None:
        output = StringIO()
        must_return = True
    content_handler = XMLGenerator(output, encoding)
    content_handler.startDocument()
    _emit(key, value, content_handler, **kwargs)
    content_handler.endDocument()
    if must_return:
        value = output.getvalue()
        try:
            value = value.decode(encoding)
        except AttributeError:
            pass

        return value
    else:
        return