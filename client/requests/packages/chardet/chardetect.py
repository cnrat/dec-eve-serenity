# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\packages\chardet\chardetect.py
from io import open
from sys import argv, stdin
from chardet.universaldetector import UniversalDetector

def description_of(file, name='stdin'):
    u = UniversalDetector()
    for line in file:
        u.feed(line)

    u.close()
    result = u.result
    if result['encoding']:
        return '%s: %s with confidence %s' % (name, result['encoding'], result['confidence'])
    else:
        return '%s: no result' % name


def main():
    if len(argv) <= 1:
        print description_of(stdin)
    else:
        for path in argv[1:]:
            with open(path, 'rb') as f:
                print description_of(f, path)


if __name__ == '__main__':
    main()