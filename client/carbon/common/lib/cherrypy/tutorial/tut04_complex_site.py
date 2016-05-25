# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\cherrypy\tutorial\tut04_complex_site.py
import cherrypy

class HomePage:

    def index(self):
        pass

    index.exposed = True


class JokePage:

    def index(self):
        pass

    index.exposed = True


class LinksPage:

    def __init__(self):
        self.extra = ExtraLinksPage()

    def index(self):
        pass

    index.exposed = True


class ExtraLinksPage:

    def index(self):
        pass

    index.exposed = True


root = HomePage()
root.joke = JokePage()
root.links = LinksPage()
import os.path
tutconf = os.path.join(os.path.dirname(__file__), 'tutorial.conf')
if __name__ == '__main__':
    cherrypy.quickstart(root, config=tutconf)
else:
    cherrypy.tree.mount(root, config=tutconf)