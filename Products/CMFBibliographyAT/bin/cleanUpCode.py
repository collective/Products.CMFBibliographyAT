#! /usr/bin/python
#
# this script will
#
#   o read (only) one file
#   o replace tabs with spaces
#   o removed CRs
#   o write clean code to stdout
#

import sys, os.path
tabsize = 8

if len(sys.argv) < 2:
    print "Usage: %s INPUT" % (os.path.basename(sys.argv[0]))
    sys.exit(1)

data = open(sys.argv[1]).read()
count = 0

for ch in data:
    if ch == '\n':
        sys.stdout.write(ch)
        count = 0
    elif ch == '\r':
        pass
    elif ch == '\t':
        newcount = count + tabsize
        newcount -= newcount % tabsize
        for i in range(newcount - count):
            sys.stdout.write(' ')
            count = newcount
    else:
        sys.stdout.write(ch)
        count += 1

