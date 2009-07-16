#!/usr/local/bin/python

#
# Program: allstrain.py.py
#
# Original Author: Lori Corbani
#
# Purpose:
#
# To sync up the Allele Strain of Origin (SOO) and Parent Cell Line Strain
#
# Requirements Satisfied by This Program:
#
# Usage:
#
#	allstrain.py
#
# Envvars:
#
# Inputs:
#
# Outputs:
#
# Exit Codes:
#
# Assumes:
#
# Bugs:
#
# Implementation:
#
#    Modules:
#
# Modification History:
#
# 07/14/2009	lec
#	- QA#2260, TR7493 (gene trapped less filling)
#	- this was originally coded in the ALL_CellLine trigger
#	  but due to the number of alleles attached to some parent cell lines,
#	  we decided to run this as a nightly process instead
#

import sys 
import os
import getopt
import string
import db
import reportlib

CRT = reportlib.CRT
SPACE = reportlib.SPACE
TAB = reportlib.TAB
PAGE = reportlib.PAGE

def showUsage():
	'''
	#
	# Purpose: Displays the correct usage of this program and exits
	#
	'''
 
	usage = 'usage: %s\n' % sys.argv[0] + \
		'-S server\n' + \
		'-D database\n' + \
		'-U user\n' + \
		'-P password file\n'

	sys.stderr.write(usage)
	sys.exit(1)
 
def qcreport():
	'''
	#
	# Generate a QC report for the Pheno group
	#
	'''

	fp = reportlib.init('allstrain', 'Allele Strain of Origin vs. Parent Cell Line Strain', os.environ['QCOUTPUTDIR'])

	fp.write('this report excludes parent cell lines:  "Not Specified", "Other (see notes)"' + CRT*2)

	fp.write(string.ljust('symbol', 35) + TAB)
	fp.write(string.ljust('parentCellLine', 25) + TAB)
	fp.write(string.ljust('sooKey', 5) + TAB)
	fp.write(string.ljust('alleleStrain', 25) + TAB)
	fp.write(string.ljust('parentKey', 10) + TAB)
	fp.write(string.ljust('parentStrain', 25) + CRT)

	fp.write(string.ljust('------', 35) + TAB)
	fp.write(string.ljust('--------------', 25) + TAB)
	fp.write(string.ljust('------', 5) + TAB)
	fp.write(string.ljust('------------', 25) + TAB)
	fp.write(string.ljust('---------', 10) + TAB)
	fp.write(string.ljust('------------', 25) + CRT*2)

	results = db.sql('select * from #toUpdate order by sooKey, parentStrain', 'auto')
	for r in results:

	    fp.write(string.ljust(r['symbol'], 35) + TAB)
	    fp.write(string.ljust(r['parentCellLine'], 25) + TAB)
	    fp.write(string.ljust(str(r['sooKey']), 5) + TAB)
	    fp.write(string.ljust(r['alleleStrain'], 25) + TAB)
	    fp.write(string.ljust(str(r['parentKey']), 10) + TAB)
	    fp.write(string.ljust(r['parentStrain'], 25) + CRT)

	fp.write('\n(%d rows affected)\n' % (len(results)))

def doUpdate():
	'''
	#
	# Run the update
	#
	'''

	db.sql('create index idx_allele on #toUpdate(_Allele_key)', None)

	updateSQL = '''update ALL_Allele
			set _Strain_key = t.parentKey
			from #toUpdate t, ALL_Allele a
			where t._Allele_key = a._Allele_key
			'''

	db.sql(updateSQL, None)

#
# Main Routine
#

try:
	optlist, args = getopt.getopt(sys.argv[1:], 'S:D:U:P:K:')
except:
	showUsage()

server = None
database = None
user = None
password = None

for opt in optlist:
	if opt[0] == '-S':
		server = opt[1]
	elif opt[0] == '-D':
		database = opt[1]
	elif opt[0] == '-U':
		user = opt[1]
	elif opt[0] == '-P':
		password = string.strip(open(opt[1], 'r').readline())
	else:
		showUsage()

if server is None or \
   database is None or \
   user is None or \
   password is None:
	showUsage()

db.set_sqlLogin(user, password, server, database)
db.useOneConnection(1)
db.set_sqlLogFunction(db.sqlLogAll)

#
# select all alleles where:
#
#	allele SOO != parent cell line strain
#
#	exclude parent cell lines:
#		Not Specified
#		Other (see notes)
#

cmd = '''select a._Allele_key, symbol = substring(a.symbol,1,35),
	sooKey = a._Strain_key, alleleStrain = substring(s1.strain,1,25), 
	parentKey = cc._Strain_key, parentStrain = substring(s2.strain,1,25), 
	parentCellLine = substring(cc.cellLine,1,25)
	into #toUpdate
	from ALL_Allele a, ALL_Allele_CellLine mc, ALL_CellLine c, ALL_CellLine cc, ALL_CellLine_Derivation d,
	PRB_Strain s1, PRB_Strain s2
	where a._Allele_key = mc._Allele_key
	and mc._MutantCellLine_key = c._CellLine_key
	and c._Derivation_key = d._Derivation_key
	and d._ParentCellLine_key = cc._CellLine_key
	and a._Strain_key != cc._Strain_key
	and a._Strain_key = s1._Strain_key
	and cc._Strain_key = s2._Strain_key
	and cc.cellLine not in ("Not Specified", "Other (see notes)")
	'''

db.sql(cmd, None)

# run the qc report
qcreport()

# execute the update
doUpdate()

db.useOneConnection(0)

