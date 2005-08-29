#!/usr/local/bin/python

'''
#
# Purpose:
#
# Create bcp file for ALL_Label
#
# Uses environment variables to determine Server and Database
# (DSQUERY and MGD).
#
# Usage:
#	alllabel.py [alleleKey]
#
# If alleleKey is provided, then only create the bcp file for that allele.
#
# History
#
# 03/04/2005	lec
#	- TR 4289, MPR
#
'''

import sys
import os
import db
import mgi_utils

NL = '\n'
DL = '|'

loaddate = mgi_utils.date("%m/%d/%Y")

#
# priority	label type	label name
#
# 1		AS		allele symbol
# 2		AN		allele name
# 3		AY		synonym
#

def writeRecord(results, labelStatusKey, priority, labelType, labelTypeName):

    for r in results:

	if labelTypeName is None:
	    labelTypeName = r['labelTypeName']

        outBCP.write(mgi_utils.prvalue(r['_Allele_key']) + DL + \
        	mgi_utils.prvalue(labelStatusKey) + DL + \
        	mgi_utils.prvalue(priority) + DL + \
        	mgi_utils.prvalue(r['label']) + DL + \
        	mgi_utils.prvalue(labelType) + DL + \
        	mgi_utils.prvalue(labelTypeName) + DL + \
        	loaddate + DL + \
        	loaddate + NL)

    print 'processed (%d) records...%s' % (len(results), mgi_utils.date())

def priority1():

	# allele symbols

        print 'processing priority 1...%s' % mgi_utils.date()

	cmd = 'select distinct a._Allele_key, label = a.symbol ' + \
		'from ALL_Allele a ' + \
		'where a.isWildType = 0 '

	if alleleKey is not None:
		cmd = cmd + 'and a._Allele_key = %s\n' % alleleKey

	writeRecord(db.sql(cmd, 'auto'), 1, 1, 'AS', 'allele symbol')

def priority2():

	# allele names

        print 'processing priority 2...%s' % mgi_utils.date()

	cmd = 'select distinct a._Allele_key, label = a.name ' + \
		'from ALL_Allele a ' + \
		'where a.isWildType = 0 '

	if alleleKey is not None:
		cmd = cmd + 'and a._Allele_key = %s\n' % alleleKey

	writeRecord(db.sql(cmd, 'auto'), 1, 2, 'AN', 'allele name')

def priority3():

	# synonyms

        print 'processing priority 3...%s' % mgi_utils.date()

	cmd = 'select distinct _Allele_key = s._Object_key, label = s.synonym ' + \
		'from MGI_SynonymType st, MGI_Synonym s ' + \
		'where st._MGIType_key = 11 ' + \
		'and st._SynonymType_key = s._SynonymType_key '

	if alleleKey is not None:
		cmd = cmd + 'and s._Object_key = %s\n' % alleleKey

	writeRecord(db.sql(cmd, 'auto'), 1, 3, 'AY', 'synonym')

#
# Main Routine
#

db.useOneConnection(1)

if len(sys.argv) == 2:
	alleleKey = sys.argv[1]
else:
	alleleKey = None

outputDir = os.environ['ALLLABELBCPDIR']
print '%s' % mgi_utils.date()
outBCP = open(outputDir + '/ALL_Label.bcp', 'w')

priority1()
priority2()
priority3()

print '%s' % mgi_utils.date()
outBCP.close()
db.useOneConnection(0)

