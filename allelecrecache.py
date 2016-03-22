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
# Outputs:
#	${DATALOADSOUTPUT}/mgi/allcacheload/output/ALL_Cre_Cache.bcp
#
# Modification History:
#
# 03/15/2016	lec
#	- TR12223/gxd anatomy II/Cre Systems
#
# 04/18/2013	lec
#	- TR11248/add 'age'
#
# 03/31/2011	lec
#	- TR 10658/added primary key to ALL_Cre_Cache
#
# 10/05/2010	lec
#	- TR 10397/add 'global userKey'
#
# 09/02/2009	lec
#	- TR 9797; new
#

import sys 
import os
import getopt
import string
import loadlib
import mgi_utils
import db

db.setAutoTranslate(False)
db.setAutoTranslateBE(False)

COLDL = "|"
LINEDL = "\n"

userKey = 0
loaddate = loadlib.loaddate

# select Cre alleles that have genotype/structure information
# status = approved, autoload ONLY

querySQL1 = '''
        select distinct
          ag._Allele_key, 
          aa._Allele_Type_key,
          e._EMAPA_Term_key,
          e._Stage_key,
          e._Assay_key,
          aa.symbol,
          aa.name,
	  t1.term as alleleType,
          nc.note,
          t2.term as emapaTerm,
	  e.age,
	  e.ageMin,
	  e.ageMax,
          e.expressed,
	  e.hasImage,
	  a.accID

	INTO TEMPORARY TABLE toprocess1

        from 
          GXD_Expression e, 
          GXD_AlleleGenotype ag, 
          VOC_Term t1,
          VOC_Term t2,
          MGI_Note n,
          MGI_NoteChunk nc,
          ALL_Allele aa,
	  ACC_Accession a

        where e._AssayType_key in (9,10,11)
          and e._GenoType_key = ag._GenoType_key
          and e._Marker_key = ag._Marker_key
          and ag._Allele_key = aa._Allele_key
	  and aa._Allele_Status_key in (847114, 3983021)
          and aa._Allele_Type_key = t1._Term_key
          and e._EMAPA_Term_key = t2._Term_key
          and ag._Allele_key = n._Object_key
          and n._Note_key = nc._Note_key
          and n._NoteType_key = 1034
	  and aa._Allele_key = a._Object_key
	  and a._LogicalDB_key = 1
	  and a._MGIType_key = 11
	  and a.prefixPart = 'MGI:'
	  and a.preferred = 1
	'''

#	  and aa.symbol like 'Acan%'

# select Cre alleles that have no genotype/structure information
# status = approved, autoload ONLY

querySQL2 = '''
	select distinct aa._Allele_key, aa._Allele_Type_key, aa.symbol, aa.name, 
		t1.term as alleleType, nc.note, a.accID, null as cresystemlabel
	INTO TEMPORARY TABLE toprocess2
	from ALL_Allele aa, VOC_Term t1, MGI_Note n, MGI_NoteChunk nc, ACC_Accession a
	where aa._Allele_Status_key in (847114, 3983021)
	and aa._Allele_Type_key = t1._Term_key
	and aa._Allele_key = n._Object_key
      	and n._NoteType_key = 1034
    	and n._Note_key = nc._Note_key
	and aa._Allele_key = a._Object_key
	and a._LogicalDB_key = 1
	and a._MGIType_key = 11
	and a.preferred = 1
	and a.private = 0
	and not exists (select 1 from toprocess1 t where aa._Allele_key = t._Allele_key)
	'''

#is there a query 2?  default = true (1)
isQuerySQL2 = 1

deleteSQL = ''
deleteSQLAllele = 'delete from ALL_Cre_Cache where _Allele_key = %s'
deleteSQLAssay = 'delete from ALL_Cre_Cache where _Assay_key = %s'

insertSQL1 = '''insert into ALL_Cre_Cache 
	values (%s,%s,%s,%s,%s,%s,'%s','%s','%s','%s','%s','%s','%s',%s,%s,%s,%s,%s,%s,now(),now())
	'''
insertSQL2 = '''insert into ALL_Cre_Cache 
	values (%s,%s,%s,null,null,null,'%s','%s','%s','%s','%s','%s',null,null,null,null,null,%s,now(),now())
	'''
# for cre systems 
embryoLabel = ''
mouseLabel = ''
creSystemsDict = {}

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
 
def processAll():
    # Purpose: processes all Cre data

    db.sql(querySQL1, None)
    db.sql(querySQL2, None)
    process('bcp')

def processByAllele(objectKey):
    # Purpose: processes data for a specific Allele

    global deleteSQL

    db.sql(querySQL1 + " and aa._Allele_key = " + objectKey, None)
    db.sql(querySQL2 + " and aa._Allele_key = " + objectKey, None)
    deleteSQL = deleteSQLAllele % (objectKey)
    process('sql')

def processByAssay(objectKey):
    # Purpose: processes data for a specific Allele

    global deleteSQL

    db.sql(querySQL1 + " and e._Assay_key = " + objectKey, None)
    db.sql(querySQL2 + " and 0 = 1", None)
    deleteSQL = deleteSQLAssay % (objectKey)
    isQuerySQL2 = 0
    process('sql')

def initCreSystems():
    # Purpose: initialize Cre System lookups
    #

    global embryoLabel, mouseLabel
    global creSystemsDict

    #
    # embryo and mouse cre-labels
    #

    embryoLabel = db.sql('''select s.label 
	    from VOC_Term v, MGI_SetMember s 
	    where v._Vocab_key= 90
	    and v.term = 'embryo'
	    and v._Term_key = s._Object_key
	    and s._Set_key = 1047''', 'auto')[0]['label']

    mouseLabel = db.sql('''select s.label 
	    from VOC_Term v, MGI_SetMember s 
	    where v._Vocab_key= 90
	    and v.term = 'mouse'
	    and v._Term_key = s._Object_key
	    and s._Set_key = 1047''', 'auto')[0]['label']

    #
    # translates EMAPA term to Cre System
    # use EMAPA/DAG
    #

    results = db.sql('''
        (
        -- expression term is descendent of cre system term
	select distinct e._EMAPA_Term_key, e._Stage_key, v2.term, s.label
	from GXD_Expression e, DAG_Closure c, 
	        VOC_Term v1, VOC_Term v2,
		MGI_SetMember s
	where e._AssayType_key in (9,10,11)
	and e._EMAPA_Term_key = v1._Term_key
	and v1._Term_key = c._DescendentObject_key
	and c._MGIType_key = 13
	and c._AncestorObject_key = v2._Term_key
	and v2._Term_key = s._Object_key
	and s._Set_key = 1047
        union
        -- expression term equals cre system term
        select distinct e._EMAPA_Term_key, e._Stage_key, null, s.label
        from GXD_Expression e, MGI_SetMember s
        where e._AssayType_key in (9,10,11)
        and e._EMAPA_Term_key = s._Object_key
        and s._Set_key = 1047
        )
        order by _EMAPA_Term_key, _Stage_key
	''', 'auto')

    for r in results:
        key = r['_EMAPA_Term_key']
        value = r 
        if not creSystemsDict.has_key(key):
            creSystemsDict[key] = []
        creSystemsDict[key].append(r)

def processCreSystems(emapaKey, emapaTerm, stageKey):
    # Purpose: determine which Cre Systems are to be included in the Cre cache
    #
    # for each EMAPA used in the given Assay...
    # using the EMAPA/DAG (moving up the DAG tree)
    #
    # if Assay contains Cre Systems other than 'embryo' or 'mouse', then use those Cre Systems
    #
    # else if 'embryo' and stage < 27, then use 'embryo'
    #
    # else use 'mouse' and stage >= 27, then use 'mouse'
    #
    # example:
    #	EMAPA term = 'sacral vertebral cartilage condensation' 
    #   in DAG/parent, translates to 'skeletal system', 'mesanchyme', 'embryo', 'mouse'
    #   in Cre System, these translate to 'skeletal system', 'mesenchyme', 'embryo-other', 'postnatal-other'
    #   what gets included in cache table : 'skeletal system', 'mesenchyme'
    #
    #   EMAPA term = 'cartilage'
    #   in DAG/parent, translates to 'embryo', stage 23
    #   what gets included in cache table : 'embryo-other'
    #
    #   EMAPA term = 'cartilage'
    #   in DAG/parent, translates to 'embryo', stage 27
    #   what gets included in cache table : 'mouse-other'
    #

    creSystemsList = []
    isEmbryo = 0
    isMouse = 0

    for c in creSystemsDict[emapaKey]:

	# if cre-system label is empty, use the emapa term
        if c['label'] == None:
            creLabel = c['term']
	# else use the cre-system label (mgi_setmember.label)
        else:
            creLabel = c['label']

        if c['term'] == 'embryo' and stageKey < 27:
	    isEmbryo = 1

        elif c['term'] == 'embryo' and stageKey >= 27:
	    isMouse = 1

        elif c['term'] == 'mouse':
	    isMouse = 1

	# or any other system (no duplicates)
        elif creLabel not in creSystemsList:
            creSystemsList.append(creLabel)

    #
    # after all expression results for given Assay have been looked at...
    #

    # embryo
    if len(creSystemsList) == 0 and isEmbryo:
        creSystemsList.append(embryoLabel)

    # mouse
    elif len(creSystemsList) == 0 and isMouse:
        creSystemsList.append(mouseLabel)

    # else if no other systems involved in the Assay, use mouse
    elif len(creSystemsList) == 0:
        creSystemsList.append(mouseLabel);

    return(creSystemsList)

def process(mode):
    # Purpose: process data using either 'sql' or 'bcp' mode

    db.sql('create index idx1 on toprocess1(_Allele_key)', None)
    db.sql('create index idx2 on toprocess2(_Allele_key)', None)

    if mode == 'bcp':
       outBCP = open(os.environ['ALLCACHEBCPDIR'] + '/ALL_Cre_Cache.bcp', 'w')
    else:
	db.sql(deleteSQL, None)
	db.commit()

    #
    # next available primary key
    #
    
    if mode == 'sql':
        results = db.sql('select max(_Cache_key) as cacheKey from ALL_Cre_Cache', 'auto')
        for r in results:
	    nextMaxKey = r['cacheKey']

        if nextMaxKey == None:
            nextMaxKey = 0
    else:
	nextMaxKey = 0

    nextMaxKey = nextMaxKey + 1
    results = db.sql('select * from toprocess1', 'auto')
    for r in results:

        creSystemsList = processCreSystems(r['_EMAPA_Term_key'], r['emapaTerm'], r['_Stage_key']) 

	if mode == 'sql':
	    for printCreLabel in creSystemsList:
	        db.sql(insertSQL1 % (str(nextMaxKey),
			       r['_Allele_key'],
                               r['_Allele_Type_key'],
		               r['_EMAPA_Term_key'],
		               r['_Stage_key'],
		               r['_Assay_key'],
		               r['accID'],
		               r['symbol'],
		               r['name'],
		               r['alleleType'],
		               r['note'],
		               r['emapaTerm'],
		               r['age'],
		               r['ageMin'],
		               r['ageMax'],
		               r['expressed'],
		               r['hasImage'],
		               printCreLabel,
		               userKey, userKey), None)
                nextMaxKey = nextMaxKey + 1

        else:
            r['note'] = r['note'].replace('\n','\\n')
	    for printCreLabel in creSystemsList:
                outBCP.write(str(nextMaxKey) + COLDL +
		     mgi_utils.prvalue(r['_Allele_key']) + COLDL +
                     mgi_utils.prvalue(r['_Allele_Type_key']) + COLDL +
		     mgi_utils.prvalue(r['_EMAPA_Term_key']) + COLDL +
		     mgi_utils.prvalue(r['_Stage_key']) + COLDL +
		     mgi_utils.prvalue(r['_Assay_key']) + COLDL +
		     mgi_utils.prvalue(r['accID']) + COLDL +
		     mgi_utils.prvalue(r['symbol']) + COLDL +
		     mgi_utils.prvalue(r['name']) + COLDL +
		     mgi_utils.prvalue(r['alleleType']) + COLDL +
		     mgi_utils.prvalue(r['note']) + COLDL +
		     mgi_utils.prvalue(r['emapaTerm']) + COLDL +
		     mgi_utils.prvalue(r['age']) + COLDL +
		     mgi_utils.prvalue(r['ageMin']) + COLDL +
		     mgi_utils.prvalue(r['ageMax']) + COLDL +
		     mgi_utils.prvalue(r['expressed']) + COLDL +
		     mgi_utils.prvalue(r['hasImage']) + COLDL +
		     mgi_utils.prvalue(printCreLabel) + COLDL +
		     mgi_utils.prvalue(userKey) + COLDL + mgi_utils.prvalue(userKey) + COLDL + 
		     loaddate + COLDL + loaddate + LINEDL)
                nextMaxKey = nextMaxKey + 1

    #
    # select the remaining Cre data (those alleles without genotypes/structures)
    # cre-system is always empty (null)
    #

    if isQuerySQL2 == 1:

        results = db.sql('select * from toprocess2', 'auto')
        for r in results:

            nextMaxKey = nextMaxKey + 1
	    if mode == 'sql':
	        db.sql(insertSQL2 % (str(nextMaxKey) ,
				   r['_Allele_key'],
                                   r['_Allele_Type_key'],
		                   r['accID'],
		                   r['symbol'],
		                   r['name'],
		                   r['alleleType'],
		                   r['note'],
		                   userKey, userKey), None)
            else:
                r['note'] = r['note'].replace('\n','\\n')
                outBCP.write(str(nextMaxKey) + COLDL +
			 mgi_utils.prvalue(r['_Allele_key']) + COLDL +
                         mgi_utils.prvalue(r['_Allele_Type_key']) + COLDL +
		         mgi_utils.prvalue('') + COLDL +
		         mgi_utils.prvalue('') + COLDL +
		         mgi_utils.prvalue('') + COLDL +
		         mgi_utils.prvalue(r['accID']) + COLDL +
		         mgi_utils.prvalue(r['symbol']) + COLDL +
		         mgi_utils.prvalue(r['name']) + COLDL +
		         mgi_utils.prvalue(r['alleleType']) + COLDL +
		         mgi_utils.prvalue(r['note']) + COLDL +
		         mgi_utils.prvalue('') + COLDL +
		         mgi_utils.prvalue('') + COLDL +
		         mgi_utils.prvalue('') + COLDL +
		         mgi_utils.prvalue('') + COLDL +
		         mgi_utils.prvalue('') + COLDL +
		         mgi_utils.prvalue('') + COLDL +
		         mgi_utils.prvalue('') + COLDL +
		         mgi_utils.prvalue(userKey) + COLDL + mgi_utils.prvalue(userKey) + COLDL + 
		         loaddate + COLDL + loaddate + LINEDL)

    if mode == 'bcp':
       outBCP.close()

# Main Routine
#

def main():
    global userKey

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

    userKey = loadlib.verifyUser(user, 0, None)

    # call functions based on the way the program is invoked

    scriptName = os.path.basename(sys.argv[0])

    # initialize the cre-system lookups
    initCreSystems()

    # all of these invocations will only affect a certain subset of data

    if scriptName == 'allelecrecache.py':
        processAll()
    
    elif scriptName == 'allelecrecacheByAllele.py':
        processByAllele(objectKey)
    
    elif scriptName == 'allelecrecacheByAssay.py':
        processByAssay(objectKey)

    db.commit()
    db.useOneConnection(0)

    return

if __name__ == '__main__':
    main()

