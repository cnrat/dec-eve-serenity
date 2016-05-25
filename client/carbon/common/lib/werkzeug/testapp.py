# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\werkzeug\testapp.py
import os
import sys
from werkzeug.templates import Template
from werkzeug.wrappers import BaseRequest as Request, BaseResponse as Response
logo = Response('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\n='.decode('base64'), mimetype='image/png')
TEMPLATE = Template(u'\\\n<%py\n    import sys, os\n    from textwrap import wrap\n    import werkzeug\n    from werkzeug.testapp import iter_sys_path\n    try:\n        import pkg_resources\n    except ImportError:\n        eggs = None\n    else:\n        eggs = list(pkg_resources.working_set)\n        eggs.sort(lambda a, b: cmp(a.project_name.lower(),\n                                   b.project_name.lower()))\n    sorted_environ = req.environ.items()\n    sorted_environ.sort(lambda a, b: cmp(str(a[0]).lower(), str(b[0]).lower()))\n%>\n<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"\n  "http://www.w3.org/TR/html4/loose.dtd">\n<title>WSGI Information</title>\n<style type="text/css">\n  body       { font-family: \'Lucida Grande\', \'Lucida Sans Unicode\', \'Geneva\',\n               \'Verdana\', sans-serif; background-color: #AFC1C4; Color: #000;\n               text-align: center; margin: 1em; padding: 0; }\n  #logo      { float: right; padding: 10px; }\n  div.box    { text-align: left; width: 45em; padding: 1em; margin: auto;\n               border: 1px solid #aaa; background-color: white; }\n  h1         { color: #11557C; font-size: 2em; margin: 0 0 0.8em 0; }\n  h2         { font-size: 1.4em; margin: 1em 0 0.5em 0; }\n  table      { width: 100%; border-collapse: collapse; border: 1px solid #AFC5C9 }\n  Table th   { background-color: #AFC1C4; color: white; font-size: 0.72em;\n               font-weight: normal; width: 18em; vertical-align: top;\n               padding: 0.5em 0 0.1em 0.5em; }\n  table td   { border: 1px solid #AFC5C9; padding: 0.1em 0 0.1em 0.5em; }\n  code       { font-family: \'Consolas\', \'Monaco\', \'Bitstream Vera Sans Mono\',\n               monospace; font-size: 0.7em; }\n  ul li      { line-height: 1.5em; }\n  ul.path    { font-size: 0.7em; margin: 0; padding: 8px; list-style: none;\n               background: #E9F5F7; border: 1px solid #AFC5C9; }\n  ul.path li { line-height: 1.6em; }\n  li.virtual { color: #999; text-decoration: underline; }\n  li.exp     { background: white; }\n</style>\n<div class="box">\n  <img src="?resource=logo" id="logo" alt="[The Werkzeug Logo]" />\n  <h1>WSGI Information</h1>\n  <p>\n    This page displays all available information about the WSGI server and\n    the underlying Python interpreter.\n  <h2 id="python-interpreter">Python Interpreter</h2>\n  <table>\n    <tr>\n      <th>Python Version</th>\n      <td>${\'<br>\'.join(escape(sys.version).splitlines())}</td>\n    </tr>\n    <tr>\n      <th>Platform</th>\n      <td>$escape(sys.platform) [$escape(os.name)]</td>\n    </tr>\n    <tr>\n      <th>API Version</th>\n      <td>$sys.api_version</td>\n    </tr>\n    <tr>\n      <th>Byteorder</th>\n      <td>$sys.byteorder</td>\n    </tr>\n    <tr>\n      <th>Werkzeug Version</th>\n      <td>$escape(werkzeug.__version__)</td>\n    </tr>\n  </table>\n  <h2 id="wsgi-environment">WSGI Environment</h2>\n  <table>\n  <% for key, value in sorted_environ %>\n    <tr>\n      <th>$escape(str(key))</th>\n      <td><code>${\' \'.join(wrap(escape(repr(value))))}</code></td>\n    </tr>\n  <% endfor %>\n  </table>\n  <% if eggs %>\n  <h2 id="installed-eggs">Installed Eggs</h2>\n  <p>\n    The following python packages were installed on the system as\n    Python eggs:\n  <ul>\n  <% for egg in eggs %>\n    <li>$escape(egg.project_name) <small>[$escape(egg.version)]</small></li>\n  <% endfor %>\n  </ul>\n  <% endif %>\n  <h2 id="sys-path">Package Load Path</h2>\n  <p>\n    The following paths are the current contents of the load path.  The\n    following entries are looked up for Python packages.  Note that not\n    all items in this path are folders.  Gray and underlined items are\n    entries pointing to invalid resources or used by custom import hooks\n    such as the zip importer.\n  <p>\n    Items with a bright background were expanded for display from a relative\n    path.  If you encounter such paths in the output you might want to check\n    your setup as relative paths are usually problematic in multithreaded\n    environments.\n  <ul class="path">\n  <% for item, virtual, expanded in iter_sys_path() %>\n    <%py\n      class_ = []\n      if virtual:\n          class_.append(\'virtual\')\n      if expanded:\n          class_.append(\'exp\')\n      class_ = \' \'.join(class_)\n    %>\n    <li<% if class_ %> class="$class_"<% endif %>>$escape(item)</li>\n  <% endfor %>\n  </ul>\n</div>')

def iter_sys_path():
    if os.name == 'posix':

        def strip(x):
            prefix = os.path.expanduser('~')
            if x.startswith(prefix):
                x = '~' + x[len(prefix):]
            return x

    else:
        strip = lambda x: x
    cwd = os.path.abspath(os.getcwd())
    for item in sys.path:
        path = os.path.join(cwd, item or os.path.curdir)
        yield (strip(os.path.normpath(path)), not os.path.isdir(path), path != item)


def test_app(environ, start_response):
    req = Request(environ, populate_request=False)
    if req.args.get('resource') == 'logo':
        response = logo
    else:
        response = Response(TEMPLATE.render(req=req), mimetype='text/html')
    return response(environ, start_response)


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('localhost', 5000, test_app, use_reloader=True)