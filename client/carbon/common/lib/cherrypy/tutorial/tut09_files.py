# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\cherrypy\tutorial\tut09_files.py
import os
localDir = os.path.dirname(__file__)
absDir = os.path.join(os.getcwd(), localDir)
import cherrypy
from cherrypy.lib import static

class FileDemo(object):

    def index(self):
        pass

    index.exposed = True

    def upload(self, myFile):
        out = '<html>\n        <body>\n            myFile length: %s<br />\n            myFile filename: %s<br />\n            myFile mime-type: %s\n        </body>\n        </html>'
        size = 0
        while True:
            data = myFile.file.read(8192)
            if not data:
                break
            size += len(data)

        return out % (size, myFile.filename, myFile.content_type)

    upload.exposed = True

    def download(self):
        path = os.path.join(absDir, 'pdf_file.pdf')
        return static.serve_file(path, 'application/x-download', 'attachment', os.path.basename(path))

    download.exposed = True


import os.path
tutconf = os.path.join(os.path.dirname(__file__), 'tutorial.conf')
if __name__ == '__main__':
    cherrypy.quickstart(FileDemo(), config=tutconf)
else:
    cherrypy.tree.mount(FileDemo(), config=tutconf)