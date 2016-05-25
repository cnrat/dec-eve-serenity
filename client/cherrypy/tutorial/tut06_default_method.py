# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\cherrypy\tutorial\tut06_default_method.py
import cherrypy

class UsersPage:

    def index(self):
        pass

    index.exposed = True

    def default(self, user):
        if user == 'remi':
            out = 'Remi Delon, CherryPy lead developer'
        elif user == 'hendrik':
            out = 'Hendrik Mans, CherryPy co-developer & crazy German'
        elif user == 'lorenzo':
            out = 'Lorenzo Lamas, famous actor and singer!'
        else:
            out = 'Unknown user. :-('
        return '%s (<a href="./">back</a>)' % out

    default.exposed = True


import os.path
tutconf = os.path.join(os.path.dirname(__file__), 'tutorial.conf')
if __name__ == '__main__':
    cherrypy.quickstart(UsersPage(), config=tutconf)
else:
    cherrypy.tree.mount(UsersPage(), config=tutconf)