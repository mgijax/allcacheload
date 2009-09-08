#!/usr/local/bin/python

#
# Program: allelecrecache.py
#
# Original Author: Lori Corbani
#
# Purpose:
#
# To load the Allele Cre Cache table (ALL_Cre_Cache)
# Cre alleles are those alleles that contain Driver Notes
#	(MGI_Note._NoteType_key = 1034)
# It is assumed that the Driver Note will NOT exceed 255 characters
#
# Requirements Satisfied by This Program:
#
# Usage:
#
#	allelecrecache.py
#	-S${MGD_DBSERVER} 
#	-D${MGD_DBNAME} 
#	-U${MGD_DBUSER} 
#	-P${MGD_DBPASSWORDFILE} 
#	-K${OBJECTKEY}
#
#	allelecrecache.py
#		-K${OBJECTKEY} = 0
#		process ALL Cre alleles
#
#	allelecrecacheByAllele
#		-K${OBJECTKEY} = _Allele_key (example "6080")
#		process for given allele
#
#	allelecrecacheByAssay
#		-K${OBJECTKEY} = _Assay_key (example "35989")
#		process for given assay
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
# 09/02/2009	lec
#	- TR 9797; new
#

import sys 
import os
import getopt
import string
import db
import loadlib
import reportlib
import mgi_utils

COLDL = os.environ['COLDELIM']
LINEDL = '\n'
outputDir = os.environ['ALLCACHEBCPDIR']

userKey = 0
loaddate = loadlib.loaddate

# select Cre alleles that have genotypes/structures information

querySQL1 = '''
        select distinct
          ag._Allele_key, 
          aa._Allele_Type_key,
          e._Structure_key,
          s._System_key,
          e._Assay_key,
          aa.symbol,
          aa.name,
          nc.note,
          sn.structure,
          vt.term,
          e.expressed
	into #toprocess1
        from 
          GXD_Expression e, 
          GXD_AlleleGenotype ag, 
          GXD_Structure s, 
          GXD_StructureName sn, 
          VOC_Term vt,
          MGI_Note n,
          MGI_NoteChunk nc,
          ALL_Allele aa
        where e._AssayType_key in (9,10,11)
          and e._GenoType_key = ag._GenoType_key
          and e._Marker_key = ag._Marker_key
          and ag._Allele_key = aa._Allele_key
          and e._Structure_key = s._Structure_key
          and s._StructureName_key = sn._StructureName_key
          and s._System_key = vt._Term_key
          and ag._Allele_key = n._Object_key
          and n._Note_key = nc._Note_key
          and n._NoteType_key = 1034
	'''

# select those Cre alleles that have no structure information

querySQL2 = '''
	select distinct aa._Allele_key, aa._Allele_Type_key, aa.symbol, aa.name, nc.note
	into #toprocess2
	from ALL_Allele aa, MGI_Note n, MGI_NoteChunk nc
	where aa._Allele_key = n._Object_key
      	and n._NoteType_key = 1034
    	and n._Note_key = nc._Note_key
	and not exists (select 1 from #toprocess1 t where aa._Allele_key = t._Allele_key)
	'''

#is there a query 2?  default = true (1)
isQuerySQL2 = 1
deleteSQL = ''
deleteSQLAllele = 'delete from ALL_Cre_Cache where _Allele_key = %s'
deleteSQLAssay = 'delete from ALL_Cre_Cache where _Assay_key = %s'

insertSQL1 = 'insert into ALL_Cre_Cache values (%s,%s,%s,%s,%s,"%s","%s","%s","%s","%s",%s,%s,%s,getdate(),getdate())'
insertSQL2 = 'insert into ALL_Cre_Cache values (%s,%s,null,null,null,"%s","%s","%s",null,null,null,%s,%s,getdate(),getdate())'

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
		'-P password file\n' + \
		'-K object key\n'

	sys.stderr.write(usage)
	sys.exit(1)
 
def bailOut(s):

    sys.stderr.write('Error:  ' + s + '\n')
    sys.exit(1)

def processAll():
    # Purpose: processes all Cre data
    # Returns:
    # Assumes:
    # Effects:
    # Throws:

    db.sql(querySQL1, None)
    db.sql(querySQL2, None)
    process('bcp')

def processByAllele(objectKey):
    # Purpose: processes data for a specific Allele
    # Returns:
    # Assumes:
    # Effects:
    # Throws:


    global deleteSQL

    db.sql(querySQL1 + " and aa._Allele_key = " + objectKey, None)
    db.sql(querySQL2 + " and aa._Allele_key = " + objectKey, None)
    deleteSQL = deleteSQLAllele % (objectKey)
    process('sql')

def processByAssay(objectKey):
    # Purpose: processes data for a specific Allele
    # Returns:
    # Assumes:
    # Effects:
    # Throws:

    global deleteSQL

    db.sql(querySQL1 + " and e._Assay_key = " + objectKey, None)
    db.sql(querySQL2 + " and 0 = 1", None)
    deleteSQL = deleteSQLAssay % (objectKey)
    isQuerySQL2 = 0
    process('sql')

def process(mode):
    # Purpose: process data using either 'sql' or 'bcp' mode
    # Returns:
    # Assumes:
    # Effects:
    # Throws:

    db.sql('create index idx1 on #toprocess1(_Allele_key)', None)
    db.sql('create index idx1 on #toprocess2(_Allele_key)', None)

    if mode == 'bcp':
       outBCP = open(outputDir + '/ALL_Cre_Cache.bcp', 'w')
    else:
	db.sql(deleteSQL, None)

    results = db.sql('select * from #toprocess1', 'auto')
    for r in results:

	if mode == 'sql':
	   db.sql(insertSQL1 % (r['_Allele_key'],
                               r['_Allele_Type_key'],
		               r['_Structure_key'],
		               r['_System_key'],
		               r['_Assay_key'],
		               r['symbol'],
		               r['name'],
		               r['note'],
		               r['structure'],
		               r['term'],
		               r['expressed'],
		               userKey, userKey), None)
        else:
            outBCP.write(mgi_utils.prvalue(r['_Allele_key']) + COLDL +
                     mgi_utils.prvalue(r['_Allele_Type_key']) + COLDL +
		     mgi_utils.prvalue(r['_Structure_key']) + COLDL +
		     mgi_utils.prvalue(r['_System_key']) + COLDL +
		     mgi_utils.prvalue(r['_Assay_key']) + COLDL +
		     mgi_utils.prvalue(r['symbol']) + COLDL +
		     mgi_utils.prvalue(r['name']) + COLDL +
		     mgi_utils.prvalue(r['note']) + COLDL +
		     mgi_utils.prvalue(r['structure']) + COLDL +
		     mgi_utils.prvalue(r['term']) + COLDL +
		     mgi_utils.prvalue(r['expressed']) + COLDL +
		     mgi_utils.prvalue(userKey) + COLDL + mgi_utils.prvalue(userKey) + COLDL + 
		     loaddate + COLDL + loaddate + LINEDL)

    #
    # select the remaining Cre data (those alleles without genotypes/structures)
    #

    if isQuerySQL2 == 1:

        results = db.sql('select * from #toprocess2', 'auto')
        for r in results:

	    if mode == 'sql':
	       db.sql(insertSQL2 % (r['_Allele_key'],
                                   r['_Allele_Type_key'],
		                   r['symbol'],
		                   r['name'],
		                   r['note'],
		                   userKey, userKey), None)
            else:
                outBCP.write(mgi_utils.prvalue(r['_Allele_key']) + COLDL +
                         mgi_utils.prvalue(r['_Allele_Type_key']) + COLDL +
		         mgi_utils.prvalue('') + COLDL +
		         mgi_utils.prvalue('') + COLDL +
		         mgi_utils.prvalue('') + COLDL +
		         mgi_utils.prvalue(r['symbol']) + COLDL +
		         mgi_utils.prvalue(r['name']) + COLDL +
		         mgi_utils.prvalue(r['note']) + COLDL +
		         mgi_utils.prvalue('') + COLDL +
		         mgi_utils.prvalue('') + COLDL +
		         mgi_utils.prvalue('') + COLDL +
		         mgi_utils.prvalue(userKey) + COLDL + mgi_utils.prvalue(userKey) + COLDL + 
		         loaddate + COLDL + loaddate + LINEDL)

    if mode == 'bcp':
       outBCP.close()

#
# Main Routine
#

def main():

    try:
	    optlist, args = getopt.getopt(sys.argv[1:], 'S:D:U:P:K:')
    except:
	    showUsage()

    server = None
    database = None
    user = None
    password = None
    objectKey = None

    for opt in optlist:
	    if opt[0] == '-S':
		    server = opt[1]
	    elif opt[0] == '-D':
		    database = opt[1]
	    elif opt[0] == '-U':
		    user = opt[1]
	    elif opt[0] == '-P':
		    password = string.strip(open(opt[1], 'r').readline())
	    elif opt[0] == '-K':
		    objectKey = opt[1]
	    else:
		        showUsage()

    if server is None or \
       database is None or \
       user is None or \
       password is None or \
       objectKey is None:
	    showUsage()

    db.set_sqlLogin(user, password, server, database)
    db.useOneConnection(1)
    db.set_sqlLogFunction(db.sqlLogAll)

    userKey = loadlib.verifyUser(user, 0, None)

    # call functions based on the way the program is invoked

    scriptName = os.path.basename(sys.argv[0])

    # all of these invocations will only affect a certain subset of data

    try:
        if scriptName == 'allelecrecache.py':
            processAll()
    
        elif scriptName == 'allelecrecacheByAllele.py':
            processByAllele(objectKey)
    
        elif scriptName == 'allelecrecacheByAssay.py':
            processByAssay(objectKey)

    except:
	bailOut('problem finding/running an invocation')

    db.useOneConnection(0)

    return

if __name__ == '__main__':
    main()
