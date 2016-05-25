# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\coverage\html.py
import os, re, shutil, sys
import coverage
from coverage.backward import pickle
from coverage.misc import CoverageException, Hasher
from coverage.phystokens import source_token_lines, source_encoding
from coverage.report import Reporter
from coverage.results import Numbers
from coverage.templite import Templite
STATIC_PATH = ['/usr/share/javascript', os.path.join(os.path.dirname(__file__), 'htmlfiles')]

def data_filename(fname):
    for static_dir in STATIC_PATH:
        static_filename = os.path.join(static_dir, fname)
        if os.path.exists(static_filename):
            return static_filename

    raise CoverageException("Couldn't find static file %r" % fname)


def data(fname):
    data_file = open(data_filename(fname))
    try:
        return data_file.read()
    finally:
        data_file.close()


class HtmlReporter(Reporter):
    STATIC_FILES = ['style.css',
     'jquery.min.js',
     'jquery.hotkeys.js',
     'jquery.isonscreen.js',
     'jquery.tablesorter.min.js',
     'coverage_html.js',
     'keybd_closed.png',
     'keybd_open.png']

    def __init__(self, cov, config):
        super(HtmlReporter, self).__init__(cov, config)
        self.directory = None
        self.template_globals = {'escape': escape,
         'title': self.config.html_title,
         '__url__': coverage.__url__,
         '__version__': coverage.__version__}
        self.source_tmpl = Templite(data('pyfile.html'), self.template_globals)
        self.coverage = cov
        self.files = []
        self.arcs = self.coverage.data.has_arcs()
        self.status = HtmlStatus()
        self.extra_css = None
        self.totals = Numbers()
        return

    def report(self, morfs):
        self.status.read(self.config.html_dir)
        m = Hasher()
        m.update(self.config)
        these_settings = m.digest()
        if self.status.settings_hash() != these_settings:
            self.status.reset()
            self.status.set_settings_hash(these_settings)
        if self.config.extra_css:
            self.extra_css = os.path.basename(self.config.extra_css)
        self.report_files(self.html_file, morfs, self.config.html_dir)
        if not self.files:
            raise CoverageException('No data to report.')
        self.index_file()
        self.make_local_static_report_files()
        return self.totals.pc_covered

    def make_local_static_report_files(self):
        for static in self.STATIC_FILES:
            shutil.copyfile(data_filename(static), os.path.join(self.directory, static))

        if self.extra_css:
            shutil.copyfile(self.config.extra_css, os.path.join(self.directory, self.extra_css))

    def write_html(self, fname, html):
        fout = open(fname, 'wb')
        try:
            fout.write(html.encode('ascii', 'xmlcharrefreplace'))
        finally:
            fout.close()

    def file_hash(self, source, cu):
        m = Hasher()
        m.update(source)
        self.coverage.data.add_to_hash(cu.filename, m)
        return m.digest()

    def html_file(self, cu, analysis):
        source_file = cu.source_file()
        try:
            source = source_file.read()
        finally:
            source_file.close()

        flat_rootname = cu.flat_rootname()
        this_hash = self.file_hash(source, cu)
        that_hash = self.status.file_hash(flat_rootname)
        if this_hash == that_hash:
            self.files.append(self.status.index_info(flat_rootname))
            return
        self.status.set_file_hash(flat_rootname, this_hash)
        if sys.version_info < (3, 0):
            encoding = source_encoding(source)
            if encoding.startswith('utf-8') and source[:3] == '\xef\xbb\xbf':
                source = source[3:]
                encoding = 'utf-8'
        nums = analysis.numbers
        missing_branch_arcs = analysis.missing_branch_arcs()
        c_run = 'run hide_run'
        c_exc = 'exc'
        c_mis = 'mis'
        c_par = 'par ' + c_run
        lines = []
        for lineno, line in enumerate(source_token_lines(source)):
            lineno += 1
            line_class = []
            annotate_html = ''
            annotate_title = ''
            if lineno in analysis.statements:
                line_class.append('stm')
            if lineno in analysis.excluded:
                line_class.append(c_exc)
            elif lineno in analysis.missing:
                line_class.append(c_mis)
            elif self.arcs and lineno in missing_branch_arcs:
                line_class.append(c_par)
                annlines = []
                for b in missing_branch_arcs[lineno]:
                    if b < 0:
                        annlines.append('exit')
                    else:
                        annlines.append(str(b))

                annotate_html = '&nbsp;&nbsp; '.join(annlines)
                if len(annlines) > 1:
                    annotate_title = 'no jumps to these line numbers'
                elif len(annlines) == 1:
                    annotate_title = 'no jump to this line number'
            elif lineno in analysis.statements:
                line_class.append(c_run)
            html = []
            for tok_type, tok_text in line:
                if tok_type == 'ws':
                    html.append(escape(tok_text))
                else:
                    tok_html = escape(tok_text) or '&nbsp;'
                    html.append("<span class='%s'>%s</span>" % (tok_type, tok_html))

            lines.append({'html': ''.join(html),
             'number': lineno,
             'class': ' '.join(line_class) or 'pln',
             'annotate': annotate_html,
             'annotate_title': annotate_title})

        html = spaceless(self.source_tmpl.render({'c_exc': c_exc,
         'c_mis': c_mis,
         'c_par': c_par,
         'c_run': c_run,
         'arcs': self.arcs,
         'extra_css': self.extra_css,
         'cu': cu,
         'nums': nums,
         'lines': lines}))
        if sys.version_info < (3, 0):
            html = html.decode(encoding)
        html_filename = flat_rootname + '.html'
        html_path = os.path.join(self.directory, html_filename)
        self.write_html(html_path, html)
        index_info = {'nums': nums,
         'html_filename': html_filename,
         'name': cu.name}
        self.files.append(index_info)
        self.status.set_index_info(flat_rootname, index_info)

    def index_file(self):
        index_tmpl = Templite(data('index.html'), self.template_globals)
        self.totals = sum([ f['nums'] for f in self.files ])
        html = index_tmpl.render({'arcs': self.arcs,
         'extra_css': self.extra_css,
         'files': self.files,
         'totals': self.totals})
        if sys.version_info < (3, 0):
            html = html.decode('utf-8')
        self.write_html(os.path.join(self.directory, 'index.html'), html)
        self.status.write(self.directory)


class HtmlStatus(object):
    STATUS_FILE = 'status.dat'
    STATUS_FORMAT = 1

    def __init__(self):
        self.reset()

    def reset(self):
        self.settings = ''
        self.files = {}

    def read(self, directory):
        usable = False
        try:
            status_file = os.path.join(directory, self.STATUS_FILE)
            fstatus = open(status_file, 'rb')
            try:
                status = pickle.load(fstatus)
            finally:
                fstatus.close()

        except (IOError, ValueError):
            usable = False
        else:
            usable = True
            if status['format'] != self.STATUS_FORMAT:
                usable = False
            elif status['version'] != coverage.__version__:
                usable = False

        if usable:
            self.files = status['files']
            self.settings = status['settings']
        else:
            self.reset()

    def write(self, directory):
        status_file = os.path.join(directory, self.STATUS_FILE)
        status = {'format': self.STATUS_FORMAT,
         'version': coverage.__version__,
         'settings': self.settings,
         'files': self.files}
        fout = open(status_file, 'wb')
        try:
            pickle.dump(status, fout)
        finally:
            fout.close()

    def settings_hash(self):
        return self.settings

    def set_settings_hash(self, settings):
        self.settings = settings

    def file_hash(self, fname):
        return self.files.get(fname, {}).get('hash', '')

    def set_file_hash(self, fname, val):
        self.files.setdefault(fname, {})['hash'] = val

    def index_info(self, fname):
        return self.files.get(fname, {}).get('index', {})

    def set_index_info(self, fname, info):
        self.files.setdefault(fname, {})['index'] = info


def escape(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace("'", '&#39;').replace('"', '&quot;').replace('  ', '&nbsp; ').replace('  ', '&nbsp; ')


def spaceless(html):
    html = re.sub('>\\s+<p ', '>\n<p ', html)
    return html