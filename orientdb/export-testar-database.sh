#!/bin/sh
# OrientDB will add ".gz" to export file name
exportfile="foo.dat"
/opt/orientdb/bin/console.sh "CONNECT remote:localhost/testar root testar; EXPORT DATABASE ${exportfile};"
