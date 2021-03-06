# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\cherrypy\tutorial\tut08_generators_and_yield.py
import cherrypy

class GeneratorDemo:

    def header(self):
        pass

    def footer(self):
        pass

    def index(self):
        users = ['Remi',
         'Carlos',
         'Hendrik',
         'Lorenzo Lamas']
        yield self.header()
        yield '<h3>List of users:</h3>'
        for user in users:
            yield '%s<br/>' % user

        yield self.footer()

    index.exposed = True


import os.path
tutconf = os.path.join(os.path.dirname(__file__), 'tutorial.conf')
if __name__ == '__main__':
    cherrypy.quickstart(GeneratorDemo(), config=tutconf)
else:
    cherrypy.tree.mount(GeneratorDemo(), config=tutconf)