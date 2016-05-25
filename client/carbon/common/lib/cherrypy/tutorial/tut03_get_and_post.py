# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\cherrypy\tutorial\tut03_get_and_post.py
import cherrypy

class WelcomePage:

    def index(self):
        pass

    index.exposed = True

    def greetUser(self, name=None):
        if name:
            return "Hey %s, what's up?" % name
        elif name is None:
            return 'Please enter your name <a href="./">here</a>.'
        else:
            return 'No, really, enter your name <a href="./">here</a>.'
            return

    greetUser.exposed = True


import os.path
tutconf = os.path.join(os.path.dirname(__file__), 'tutorial.conf')
if __name__ == '__main__':
    cherrypy.quickstart(WelcomePage(), config=tutconf)
else:
    cherrypy.tree.mount(WelcomePage(), config=tutconf)