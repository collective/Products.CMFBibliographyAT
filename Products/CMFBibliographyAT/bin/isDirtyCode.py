#! /usr/bin/python
#
# this script detects
#
#   o tabs
#   o CRs
#
# the script accepts a list of files (or file wildcards)
# as sysargs...
#

import sys, os.path, string
tabsize = 8

if len(sys.argv) < 2:
    print "Usage: %s INPUT" % (os.path.basename(sys.argv[0]))
    sys.exit(1)

for filename in sys.argv[1:]:
    try:
        data = open(filename).read()
        count = 0

        if (string.find('\t', data) != -1) and (len(data) > 0):
            print 'Found tabs in file: %s.' % filename
        if (string.find('\r', data) != -1) and (len(data) > 0):
            print 'Found CRs in file: %s' % filename

    except IOError:
        pass
