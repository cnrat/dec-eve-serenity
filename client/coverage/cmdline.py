# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\stdlib\coverage\cmdline.py
import optparse, os, sys, traceback
from coverage.backward import sorted
from coverage.execfile import run_python_file, run_python_module
from coverage.misc import CoverageException, ExceptionDuringRun, NoSource
from coverage.debug import info_formatter

class Opts(object):
    append = optparse.make_option('-a', '--append', action='store_false', dest='erase_first', help='Append coverage data to .coverage, otherwise it is started clean with each run.')
    branch = optparse.make_option('', '--branch', action='store_true', help='Measure branch coverage in addition to statement coverage.')
    debug = optparse.make_option('', '--debug', action='store', metavar='OPTS', help='Debug options, separated by commas')
    directory = optparse.make_option('-d', '--directory', action='store', metavar='DIR', help='Write the output files to DIR.')
    fail_under = optparse.make_option('', '--fail-under', action='store', metavar='MIN', type='int', help='Exit with a status of 2 if the total coverage is less than MIN.')
    help = optparse.make_option('-h', '--help', action='store_true', help='Get help on this command.')
    ignore_errors = optparse.make_option('-i', '--ignore-errors', action='store_true', help='Ignore errors while reading source files.')
    include = optparse.make_option('', '--include', action='store', metavar='PAT1,PAT2,...', help='Include files only when their filename path matches one of these patterns.  Usually needs quoting on the command line.')
    pylib = optparse.make_option('-L', '--pylib', action='store_true', help="Measure coverage even inside the Python installed library, which isn't done by default.")
    show_missing = optparse.make_option('-m', '--show-missing', action='store_true', help="Show line numbers of statements in each module that weren't executed.")
    old_omit = optparse.make_option('-o', '--omit', action='store', metavar='PAT1,PAT2,...', help='Omit files when their filename matches one of these patterns. Usually needs quoting on the command line.')
    omit = optparse.make_option('', '--omit', action='store', metavar='PAT1,PAT2,...', help='Omit files when their filename matches one of these patterns. Usually needs quoting on the command line.')
    output_xml = optparse.make_option('-o', '', action='store', dest='outfile', metavar='OUTFILE', help="Write the XML report to this file. Defaults to 'coverage.xml'")
    parallel_mode = optparse.make_option('-p', '--parallel-mode', action='store_true', help='Append the machine name, process id and random number to the .coverage data file name to simplify collecting data from many processes.')
    module = optparse.make_option('-m', '--module', action='store_true', help="<pyfile> is an importable Python module, not a script path, to be run as 'python -m' would run it.")
    rcfile = optparse.make_option('', '--rcfile', action='store', help="Specify configuration file.  Defaults to '.coveragerc'")
    source = optparse.make_option('', '--source', action='store', metavar='SRC1,SRC2,...', help='A list of packages or directories of code to be measured.')
    timid = optparse.make_option('', '--timid', action='store_true', help='Use a simpler but slower trace method.  Try this if you get seemingly impossible results!')
    title = optparse.make_option('', '--title', action='store', metavar='TITLE', help='A text string to use as the title on the HTML.')
    version = optparse.make_option('', '--version', action='store_true', help='Display version information and exit.')


class CoverageOptionParser(optparse.OptionParser, object):

    def __init__(self, *args, **kwargs):
        super(CoverageOptionParser, self).__init__(add_help_option=False, *args, **kwargs)
        self.set_defaults(actions=[], branch=None, debug=None, directory=None, fail_under=None, help=None, ignore_errors=None, include=None, omit=None, parallel_mode=None, module=None, pylib=None, rcfile=True, show_missing=None, source=None, timid=None, title=None, erase_first=None, version=None)
        self.disable_interspersed_args()
        self.help_fn = self.help_noop
        return

    def help_noop(self, error=None, topic=None, parser=None):
        pass

    class OptionParserError(Exception):
        pass

    def parse_args(self, args=None, options=None):
        try:
            options, args = super(CoverageOptionParser, self).parse_args(args, options)
        except self.OptionParserError:
            return (False, None, None)

        return (True, options, args)

    def error(self, msg):
        self.help_fn(msg)
        raise self.OptionParserError


class ClassicOptionParser(CoverageOptionParser):

    def __init__(self):
        super(ClassicOptionParser, self).__init__()
        self.add_action('-a', '--annotate', 'annotate')
        self.add_action('-b', '--html', 'html')
        self.add_action('-c', '--combine', 'combine')
        self.add_action('-e', '--erase', 'erase')
        self.add_action('-r', '--report', 'report')
        self.add_action('-x', '--execute', 'execute')
        self.add_options([Opts.directory,
         Opts.help,
         Opts.ignore_errors,
         Opts.pylib,
         Opts.show_missing,
         Opts.old_omit,
         Opts.parallel_mode,
         Opts.timid,
         Opts.version])

    def add_action(self, dash, dashdash, action_code):
        option = self.add_option(dash, dashdash, action='callback', callback=self._append_action)
        option.action_code = action_code

    def _append_action(self, option, opt_unused, value_unused, parser):
        parser.values.actions.append(option.action_code)


class CmdOptionParser(CoverageOptionParser):

    def __init__(self, action, options=None, defaults=None, usage=None, cmd=None, description=None):
        if usage:
            usage = '%prog ' + usage
        super(CmdOptionParser, self).__init__(prog='coverage %s' % (cmd or action), usage=usage, description=description)
        self.set_defaults(actions=[action], **(defaults or {}))
        if options:
            self.add_options(options)
        self.cmd = cmd or action

    def __eq__(self, other):
        return other == '<CmdOptionParser:%s>' % self.cmd


GLOBAL_ARGS = [Opts.rcfile, Opts.help]
CMDS = {'annotate': CmdOptionParser('annotate', [Opts.directory,
              Opts.ignore_errors,
              Opts.omit,
              Opts.include] + GLOBAL_ARGS, usage='[options] [modules]', description='Make annotated copies of the given files, marking statements that are executed with > and statements that are missed with !.'),
 'combine': CmdOptionParser('combine', GLOBAL_ARGS, usage=' ', description="Combine data from multiple coverage files collected with 'run -p'.  The combined results are written to a single file representing the union of the data."),
 'debug': CmdOptionParser('debug', GLOBAL_ARGS, usage='<topic>', description="Display information on the internals of coverage.py, for diagnosing problems. Topics are 'data' to show a summary of the collected data, or 'sys' to show installation information."),
 'erase': CmdOptionParser('erase', GLOBAL_ARGS, usage=' ', description='Erase previously collected coverage data.'),
 'help': CmdOptionParser('help', GLOBAL_ARGS, usage='[command]', description='Describe how to use coverage.py'),
 'html': CmdOptionParser('html', [Opts.directory,
          Opts.fail_under,
          Opts.ignore_errors,
          Opts.omit,
          Opts.include,
          Opts.title] + GLOBAL_ARGS, usage='[options] [modules]', description='Create an HTML report of the coverage of the files.  Each file gets its own page, with the source decorated to show executed, excluded, and missed lines.'),
 'report': CmdOptionParser('report', [Opts.fail_under,
            Opts.ignore_errors,
            Opts.omit,
            Opts.include,
            Opts.show_missing] + GLOBAL_ARGS, usage='[options] [modules]', description='Report coverage statistics on modules.'),
 'run': CmdOptionParser('execute', [Opts.append,
         Opts.branch,
         Opts.debug,
         Opts.pylib,
         Opts.parallel_mode,
         Opts.module,
         Opts.timid,
         Opts.source,
         Opts.omit,
         Opts.include] + GLOBAL_ARGS, defaults={'erase_first': True}, cmd='run', usage='[options] <pyfile> [program options]', description='Run a Python program, measuring code execution.'),
 'xml': CmdOptionParser('xml', [Opts.fail_under,
         Opts.ignore_errors,
         Opts.omit,
         Opts.include,
         Opts.output_xml] + GLOBAL_ARGS, cmd='xml', usage='[options] [modules]', description='Generate an XML report of coverage results.')}
OK, ERR, FAIL_UNDER = (0, 1, 2)

class CoverageScript(object):

    def __init__(self, _covpkg=None, _run_python_file=None, _run_python_module=None, _help_fn=None):
        if _covpkg:
            self.covpkg = _covpkg
        else:
            import coverage
            self.covpkg = coverage
        self.run_python_file = _run_python_file or run_python_file
        self.run_python_module = _run_python_module or run_python_module
        self.help_fn = _help_fn or self.help
        self.classic = False
        self.coverage = None
        return

    def command_line(self, argv):
        if not argv:
            self.help_fn(topic='minimum_help')
            return OK
        else:
            self.classic = argv[0].startswith('-')
            if self.classic:
                parser = ClassicOptionParser()
            else:
                parser = CMDS.get(argv[0])
                if not parser:
                    self.help_fn("Unknown command: '%s'" % argv[0])
                    return ERR
                argv = argv[1:]
            parser.help_fn = self.help_fn
            ok, options, args = parser.parse_args(argv)
            if not ok:
                return ERR
            if self.do_help(options, args, parser):
                return OK
            if not self.args_ok(options, args):
                return ERR
            source = unshell_list(options.source)
            omit = unshell_list(options.omit)
            include = unshell_list(options.include)
            debug = unshell_list(options.debug)
            self.coverage = self.covpkg.coverage(data_suffix=options.parallel_mode, cover_pylib=options.pylib, timid=options.timid, branch=options.branch, config_file=options.rcfile, source=source, omit=omit, include=include, debug=debug)
            if 'debug' in options.actions:
                return self.do_debug(args)
            if 'erase' in options.actions or options.erase_first:
                self.coverage.erase()
            else:
                self.coverage.load()
            if 'execute' in options.actions:
                self.do_execute(options, args)
            if 'combine' in options.actions:
                self.coverage.combine()
                self.coverage.save()
            report_args = dict(morfs=args, ignore_errors=options.ignore_errors, omit=omit, include=include)
            if 'report' in options.actions:
                total = self.coverage.report(show_missing=options.show_missing, **report_args)
            if 'annotate' in options.actions:
                self.coverage.annotate(directory=options.directory, **report_args)
            if 'html' in options.actions:
                total = self.coverage.html_report(directory=options.directory, title=options.title, **report_args)
            if 'xml' in options.actions:
                outfile = options.outfile
                total = self.coverage.xml_report(outfile=outfile, **report_args)
            if options.fail_under is not None:
                if total >= options.fail_under:
                    return OK
                else:
                    return FAIL_UNDER
            else:
                return OK
            return

    def help(self, error=None, topic=None, parser=None):
        if error:
            print error
            print "Use 'coverage help' for help."
        elif parser:
            print parser.format_help().strip()
        else:
            help_msg = HELP_TOPICS.get(topic, '').strip()
            if help_msg:
                print help_msg % self.covpkg.__dict__
            else:
                print "Don't know topic %r" % topic

    def do_help(self, options, args, parser):
        if options.help:
            if self.classic:
                self.help_fn(topic='help')
            else:
                self.help_fn(parser=parser)
            return True
        if 'help' in options.actions:
            if args:
                for a in args:
                    parser = CMDS.get(a)
                    if parser:
                        self.help_fn(parser=parser)
                    else:
                        self.help_fn(topic=a)

            else:
                self.help_fn(topic='help')
            return True
        if options.version:
            self.help_fn(topic='version')
            return True
        return False

    def args_ok(self, options, args):
        for i in ['erase', 'execute']:
            for j in ['annotate',
             'html',
             'report',
             'combine']:
                if i in options.actions and j in options.actions:
                    self.help_fn("You can't specify the '%s' and '%s' options at the same time." % (i, j))
                    return False

        if not options.actions:
            self.help_fn('You must specify at least one of -e, -x, -c, -r, -a, or -b.')
            return False
        args_allowed = 'execute' in options.actions or 'annotate' in options.actions or 'html' in options.actions or 'debug' in options.actions or 'report' in options.actions or 'xml' in options.actions
        if not args_allowed and args:
            self.help_fn('Unexpected arguments: %s' % ' '.join(args))
            return False
        if 'execute' in options.actions and not args:
            self.help_fn('Nothing to do.')
            return False
        return True

    def do_execute(self, options, args):
        old_path0 = sys.path[0]
        self.coverage.start()
        code_ran = True
        try:
            try:
                if options.module:
                    sys.path[0] = ''
                    self.run_python_module(args[0], args)
                else:
                    filename = args[0]
                    sys.path[0] = os.path.abspath(os.path.dirname(filename))
                    self.run_python_file(filename, args)
            except NoSource:
                code_ran = False
                raise

        finally:
            self.coverage.stop()
            if code_ran:
                self.coverage.save()
            sys.path[0] = old_path0

    def do_debug(self, args):
        if not args:
            self.help_fn('What information would you like: data, sys?')
            return ERR
        for info in args:
            if info == 'sys':
                print '-- sys ----------------------------------------'
                for line in info_formatter(self.coverage.sysinfo()):
                    print ' %s' % line

            elif info == 'data':
                print '-- data ---------------------------------------'
                self.coverage.load()
                print 'path: %s' % self.coverage.data.filename
                print 'has_arcs: %r' % self.coverage.data.has_arcs()
                summary = self.coverage.data.summary(fullpath=True)
                if summary:
                    filenames = sorted(summary.keys())
                    print '\n%d files:' % len(filenames)
                    for f in filenames:
                        print '%s: %d lines' % (f, summary[f])

                else:
                    print 'No data collected'
            else:
                self.help_fn("Don't know what you mean by %r" % info)
                return ERR

        return OK


def unshell_list(s):
    if not s:
        return None
    else:
        if sys.platform == 'win32':
            s = s.strip("'")
        return s.split(',')


HELP_TOPICS = {'classic': "Coverage.py version %(__version__)s\nMeasure, collect, and report on code coverage in Python programs.\n\nUsage:\n\ncoverage -x [-p] [-L] [--timid] MODULE.py [ARG1 ARG2 ...]\n    Execute the module, passing the given command-line arguments, collecting\n    coverage data.  With the -p option, include the machine name and process\n    id in the .coverage file name.  With -L, measure coverage even inside the\n    Python installed library, which isn't done by default.  With --timid, use a\n    simpler but slower trace method.\n\ncoverage -e\n    Erase collected coverage data.\n\ncoverage -c\n    Combine data from multiple coverage files (as created by -p option above)\n    and store it into a single file representing the union of the coverage.\n\ncoverage -r [-m] [-i] [-o DIR,...] [FILE1 FILE2 ...]\n    Report on the statement coverage for the given files.  With the -m\n    option, show line numbers of the statements that weren't executed.\n\ncoverage -b -d DIR [-i] [-o DIR,...] [FILE1 FILE2 ...]\n    Create an HTML report of the coverage of the given files.  Each file gets\n    its own page, with the file listing decorated to show executed, excluded,\n    and missed lines.\n\ncoverage -a [-d DIR] [-i] [-o DIR,...] [FILE1 FILE2 ...]\n    Make annotated copies of the given files, marking statements that\n    are executed with > and statements that are missed with !.\n\n-d DIR\n    Write output files for -b or -a to this directory.\n\n-i  Ignore errors while reporting or annotating.\n\n-o DIR,...\n    Omit reporting or annotating files when their filename path starts with\n    a directory listed in the omit list.\n    e.g. coverage -i -r -o c:\\python25,lib\\enthought\\traits\n\nCoverage data is saved in the file .coverage by default.  Set the\nCOVERAGE_FILE environment variable to save it somewhere else.\n",
 'help': 'Coverage.py, version %(__version__)s\nMeasure, collect, and report on code coverage in Python programs.\n\nusage: coverage <command> [options] [args]\n\nCommands:\n    annotate    Annotate source files with execution information.\n    combine     Combine a number of data files.\n    erase       Erase previously collected coverage data.\n    help        Get help on using coverage.py.\n    html        Create an HTML report.\n    report      Report coverage stats on modules.\n    run         Run a Python program and measure code execution.\n    xml         Create an XML report of coverage results.\n\nUse "coverage help <command>" for detailed help on any command.\nUse "coverage help classic" for help on older command syntax.\nFor more information, see %(__url__)s\n',
 'minimum_help': "Code coverage for Python.  Use 'coverage help' for help.\n",
 'version': 'Coverage.py, version %(__version__)s.  %(__url__)s\n'}

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    try:
        status = CoverageScript().command_line(argv)
    except ExceptionDuringRun:
        _, err, _ = sys.exc_info()
        traceback.print_exception(*err.args)
        status = ERR
    except CoverageException:
        _, err, _ = sys.exc_info()
        print err
        status = ERR
    except SystemExit:
        _, err, _ = sys.exc_info()
        if err.args:
            status = err.args[0]
        else:
            status = None

    return status