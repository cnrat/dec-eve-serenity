# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\jinja2\exceptions.py


class TemplateError(Exception):

    def __init__(self, message=None):
        if message is not None:
            message = unicode(message).encode('utf-8')
        Exception.__init__(self, message)
        return

    @property
    def message(self):
        if self.args:
            message = self.args[0]
            if message is not None:
                return message.decode('utf-8', 'replace')
        return


class TemplateNotFound(IOError, LookupError, TemplateError):
    message = None

    def __init__(self, name, message=None):
        IOError.__init__(self)
        if message is None:
            message = name
        self.message = message
        self.name = name
        self.templates = [name]
        return

    def __str__(self):
        return self.message.encode('utf-8')

    def __unicode__(self):
        return self.message


class TemplatesNotFound(TemplateNotFound):

    def __init__(self, names=(), message=None):
        if message is None:
            message = u'non of the templates given were found: ' + u', '.join(map(unicode, names))
        TemplateNotFound.__init__(self, names and names[-1] or None, message)
        self.templates = list(names)
        return


class TemplateSyntaxError(TemplateError):

    def __init__(self, message, lineno, name=None, filename=None):
        TemplateError.__init__(self, message)
        self.lineno = lineno
        self.name = name
        self.filename = filename
        self.source = None
        self.translated = False
        return

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        if self.translated:
            return self.message
        else:
            location = 'line %d' % self.lineno
            name = self.filename or self.name
            if name:
                location = 'File "%s", %s' % (name, location)
            lines = [self.message, '  ' + location]
            if self.source is not None:
                try:
                    line = self.source.splitlines()[self.lineno - 1]
                except IndexError:
                    line = None

                if line:
                    lines.append('    ' + line.strip())
            return u'\n'.join(lines)


class TemplateAssertionError(TemplateSyntaxError):
    pass


class TemplateRuntimeError(TemplateError):
    pass


class UndefinedError(TemplateRuntimeError):
    pass


class SecurityError(TemplateRuntimeError):
    pass


class FilterArgumentError(TemplateRuntimeError):
    pass