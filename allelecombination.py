#!/usr/local/bin/python

#
# Program: allelecombination.py
#
# Original Author: Lori Corbani
#
# Purpose:
#
# To create MGI_Note, MGI_NoteChunk objects for Allele Combinations
#
# displayNotes1
# _NoteType_key = 1016
# this is the display that shows up in the EI
# this is = displayNotes2 without the linkout flags
#
# displayNotes2
# _NoteType_key = 1017, 1018
# this is = displayNotes1 with the linkout flags
# displays on the Phenotypic Allele Detail page in the WI
# displays on the Phenotypic Allele Summary page in the WI
#
# Requirements Satisfied by This Program:
#
# Usage:
#
#	allelecombinationByAllele.py alleleObjectKey
#		- process Allele Combinations for given Allele
#
#	allelecombinationByMarker.py markerObjectKey
#		- process Allele Combinations for given Marker
#
# Implementation:
#
#    Modules:
#
# Modification History:
#
# 06/14/2011	lec
#	- TR10404
#	added Homoplasmic, Heterplasmic
#
# 08/25/2010	lec
#	- TR10255
#         process X-linked/Y-linked displays
#	  removed displayNotes3; this was not being used
#	  displayNotes2 is being used for both 1017 & 1018 (detail & summary WI pages)
#
# 12/16/2009	lec
#	- TR9871/by genotype should query by GXD_Genotype; not every Genotype will have an Allele
#	  
# 07/22/2009	lec
#	- TR 7493; allow selection of null marker in def process()
#

import sys 
import os
import getopt
import string
import loadlib
import reportlib
import db

db.setAutoTranslate(False)
db.setAutoTranslateBE(False)

notenewline = '\\n'
mgiTypeKey = 12
userKey = 0
combNoteType1 = 1016
combNoteType2 = 1017
combNoteType3 = 1018

DEBUG = 0

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
    # Purpose: processes all Genotype data
    # Returns:
    # Assumes:
    # Effects:
    # Throws:

    # select all Genotypes

    db.sql('''select a._Object_key as _Genotype_key, a.accID as genotypeID INTO TEMPORARY TABLE toprocess 
	from ACC_Accession a 
	where a._MGIType_key = 12 
	and a._LogicalDB_key = 1 
	and a.prefixPart = 'MGI:' 
	and a.preferred = 1
	''', None)

    db.sql('create index idx1 on toprocess(_Genotype_key)', None)

    process('bcp')

def processByAllele(objectKey):
    # Purpose: processes data for a specific Allele
    # Returns:
    # Assumes:
    # Effects:
    # Throws:

    global DEBUG

    DEBUG = 1

    # select all Genotypes of a specified Allele

    db.sql('''
	select distinct _Genotype_key, null as genotypeID INTO TEMPORARY TABLE toprocess from GXD_AlleleGenotype 
	where _Allele_key = %s
	''' % (objectKey), None)

    db.sql('create index idx1 on toprocess(_Genotype_key)', None)

    process('sql')

def processByMarker(objectKey):
    # Purpose: processes data for a specific Marker
    # Returns:
    # Assumes:
    # Effects:
    # Throws:

    # select all Genotypes of a specified Marker

    db.sql('''select distinct _Genotype_key, null as genotypeID INTO TEMPORARY TABLE toprocess from GXD_AlleleGenotype
	where _Marker_key = %s
	''' % (objectKey), None)

    db.sql('create index idx1 on toprocess(_Genotype_key)', None)

    process('sql')

def processByGenotype(objectKey):
    # Purpose: processes data for a specific Genotype
    # Returns:
    # Assumes:
    # Effects:
    # Throws:

    # select all Genotypes of a specified Genotype

    db.sql('''
	select distinct _Genotype_key, null as genotypeID INTO TEMPORARY TABLE toprocess from GXD_Genotype
	where _Genotype_key = %s
	''' % (objectKey), None)

    db.sql('create index idx1 on toprocess(_Genotype_key)', None)

    process('sql')

def processNote(objectKey, notes, noteTypeKey):
    # Purpose: generate string for MGI Note insertion
    # Returns: noteCmd, a string that contains the insert commands
    # Assumes:
    # Effects:
    # Throws:

    noteCmd = '''insert into MGI_Note values ((select * from noteKeyMax), %s, %s, %s, %s, %s, now(), now());\n
	      ''' % (objectKey, mgiTypeKey, noteTypeKey, userKey, userKey)

    noteCmd = noteCmd + \
        '''insert into MGI_NoteChunk values ((select * from noteKeyMax), 1, '%s', %s, %s, now(), now());\n
	''' % (notes, userKey, userKey)

    # increment the MGI_Note._Note_key

    noteCmd = noteCmd + 'update noteKeyMax set noteKey = noteKey + 1;\n'

    return noteCmd

def process(mode):
    # Purpose: process data using either 'sql' or 'bcp' mode
    # Returns:
    # Assumes:
    # Effects:
    # Throws:

    global notenewline

    if mode == 'bcp':
	fp1 = reportlib.init('allelecombnotetype1', printHeading = None)
	fp2 = reportlib.init('allelecombnotetype2', printHeading = None)
	fp3 = reportlib.init('allelecombnotetype3', printHeading = None)
    else:
	notenewline = '\n'

    # delete existiing Allele Combination notes for Genotypes we're processing

    if DEBUG:
        print '\ndeleting existing allele combination\n'
	sys.stdout.flush()

    db.sql('''delete from MGI_Note 
	using toprocess p 
	where p._Genotype_key = MGI_Note._Object_key 
	and MGI_Note._MGIType_key = %s 
	and MGI_Note._NoteType_key in (%s,%s,%s)
	''' % (mgiTypeKey, combNoteType1, combNoteType2, combNoteType3), None)

    if DEBUG:
        print 'finished deleting existing allele combination\n'
	sys.stdout.flush()

    # read in appropriate records

    if DEBUG:
        print '\nselecting existing allele combination\n'
	sys.stdout.flush()

    cmd = '''(
	    select p._Genotype_key,
	    p.genotypeID,
	    t1.term as alleleState, 
	    t2.term as compound, 
	    a1.symbol as allele1, 
	    a2.symbol as allele2, 
	    a1.isWildType as allele1WildType, 
	    a2.isWildType as allele2WildType, 
	    c1.accID as mgiID1, 
	    c2.accID as mgiID2, 
	    g.sequenceNum, m.chromosome 
	    from toprocess p, 
	    GXD_AllelePair g LEFT OUTER JOIN MRK_Marker m on (g._Marker_key = m._Marker_key),
	    VOC_Term t1, VOC_Term t2, ALL_Allele a1, ALL_Allele a2, 
	    ACC_Accession c1, ACC_Accession c2
	    where p._Genotype_key = g._Genotype_key 
	    and g._PairState_key = t1._Term_key 
	    and g._Compound_key = t2._Term_key 
	    and g._Allele_key_1 = a1._Allele_key 
	    and g._Allele_key_2 = a2._Allele_key 
	    and g._Allele_key_1 = c1._Object_key 
	    and c1._MGIType_key = 11 
	    and c1._LogicalDB_key = 1 
	    and c1.prefixPart = 'MGI:' 
	    and c1.preferred = 1 
	    and g._Allele_key_2 = c2._Object_key 
	    and c2._MGIType_key = 11 
	    and c2._LogicalDB_key = 1 
	    and c2.prefixPart = 'MGI:' 
	    and c2.preferred = 1 
	    union 
	    select p._Genotype_key,
	    p.genotypeID,
	    t1.term as alleleState, 
	    t2.term as compound, 
	    a1.symbol as allele1,
	    null as allele2, 
	    a1.isWildType as allele1WildType, 
	    0 as allele2WildType, 
	    c1.accID as mgiID1, 
	    null as mgiID2, 
	    g.sequenceNum, m.chromosome 
	    from toprocess p, 
	    GXD_AllelePair g LEFT OUTER JOIN MRK_Marker m on (g._Marker_key = m._Marker_key),
	    VOC_Term t1, VOC_Term t2, ALL_Allele a1, ACC_Accession c1
	    where p._Genotype_key = g._Genotype_key 
	    and g._PairState_key = t1._Term_key 
	    and g._Compound_key = t2._Term_key 
	    and g._Allele_key_1 = a1._Allele_key 
	    and g._Allele_key_2 is null 
	    and g._Allele_key_1 = c1._Object_key 
	    and c1._MGIType_key = 11 
	    and c1._LogicalDB_key = 1 
	    and c1.prefixPart = 'MGI:' 
	    and c1.preferred = 1 
	    )
	    order by _Genotype_key, sequenceNum;\n'''

    results = db.sql(cmd, 'auto')

    if DEBUG:
        print 'finished selecting existing allele combination\n'
	print str(results)
	sys.stdout.flush()

    if DEBUG:
        print '\nputting existing allele combination into a list\n'
	sys.stdout.flush()

    genotypes = {}
    for r in results:
        key = r['_Genotype_key']
        value = r

        if not genotypes.has_key(key):
	    genotypes[key] = []
        genotypes[key].append(r)

    if DEBUG:
        print 'finished putting existing allele combination into a list\n'
	sys.stdout.flush()

    for g in genotypes.keys():

	if DEBUG:
        	print '\nrunning allele combination for genotype\n', genotypes[g]
		sys.stdout.flush()

        foundTop = 0
        foundBottom = 0

        displayNotes1 = ''
        displayNotes2 = ''

        topType1 = ''
        topType2 = ''
        topType3 = ''

        bottomType1 = ''
        bottomType2 = ''
        bottomType3 = ''

	# if alleleStatue = 'Hemizygous X-linked' or 'Hemizygous Y-linked'
	# appears more than once in a given genotype
	# then set isCollapse = 1

	isCollapseX = 0
	isCollapseY = 0
	xcounter = 0
	ycounter = 0

        for r in genotypes[g]:
            alleleState = r['alleleState']

            if alleleState == 'Hemizygous X-linked':
		xcounter = xcounter + 1

            if alleleState == 'Hemizygous Y-linked':
		ycounter = ycounter + 1

	if xcounter > 1:
	    isCollapseX = 1
	if ycounter > 1:
	    isCollapseY = 1

	#
	# iterate thru each allele pair for this genotype
	#

        for r in genotypes[g]:

            compound = r['compound']
            alleleState = r['alleleState']
	    chr = r['chromosome']

            allele1 = r['allele1']
            allele1WildType = r['allele1WildType']
            mgiID1 = r['mgiID1']

            allele2 = r['allele2']
            allele2WildType = r['allele2WildType']
            mgiID2 = r['mgiID2']

            if alleleState in ['Homoplasmic', 'Heteroplasmic'] and compound == 'Not Applicable':
	        separatorTopBottom = ''
		separatorBottom = ''
            elif alleleState in ['Homoplasmic', 'Heteroplasmic']:
	        separatorTopBottom = ', '
		separatorBottom = ', '
	    else:
	        separatorTopBottom = '/'
		separatorBottom = ' '

	    #
	    # topType3, bottomType3 = "master" link-out text
	    # the type2 display is created by attaching the appropriate type3 "master"
	    #
	    # type2 = ''
	    # type2 = previous type2 + type3 (master)
	    #

            # only used for compound = 'Not Applicable'
	    if allele1WildType == 1:
	        topType3 = '\AlleleSymbol(' + mgiID1 + '|0)'
	    else:
	        topType3 = '\Allele(' + mgiID1 + '|' + allele1 + '|)'

            if alleleState in ['Homozygous', 'Heterozygous']:
                if allele2WildType == 1:
	            bottomType3 = '\AlleleSymbol(' + mgiID2 + '|0)'
                else:
	            bottomType3 = '\Allele(' + mgiID2 + '|' + allele2 + '|)'

            elif alleleState == 'Hemizygous X-linked':
                bottomType3 = 'Y'

            elif alleleState == 'Hemizygous Insertion':
                bottomType3 = '0'

            elif alleleState == 'Hemizygous Deletion':
                bottomType3 = '-'

            elif alleleState == 'Indeterminate':
                bottomType3 = '?'

            elif alleleState in ['Homoplasmic', 'Heteroplasmic']:
                bottomType3 = ''

            elif (alleleState == 'Hemizygous Y-linked') or (alleleState == 'Hemizygous Insertion' and chr == 'Y'):
	        if allele1WildType == 1:
	            bottomType3 = '\AlleleSymbol(' + mgiID1 + '|0)'
	        else:
	            bottomType3 = '\Allele(' + mgiID1 + '|' + allele1 + '|)'
                topType3 = 'X'

	    # if Allele Pair does not have a compound attribute

            if alleleState == 'Hemizygous X-linked' and isCollapseX:

		#
		# collapse the row into one display
		#
		# MGI:3511894
		# Maoa    Maoa<K284stop>  Hemizygous X-linked
		# Maob    Maob<tm1Shih>   Hemizygous X-linked
		#
		# Display:
		#
		# Maoa<K284stop> Maob<tm1Shih>/Y
		#

                if foundTop >= 1:
                    topType1 = topType1 + ' ' + allele1
                    topType2 = topType2 + topType3
                else:
		    topType1 = allele1
                    topType2 = topType3

                bottomType1 = bottomType2 = bottomType3
		topType3 = topType2
		foundTop = foundTop + 1
		foundBottom = foundBottom + 1

            elif alleleState == 'Hemizygous Y-linked' and isCollapseY:

		#
		# collapse the row into one display
		#
		# MGI:3043585
		# Del(Y)1Psb    Del(Y)1Psb	Hemizygous Y-linked
		# Sry     	Sry<dl1Rlb>	Hemizygous Y-linked
		# Tg(Sry)2Ei	Tg(Sry)2Ei	Hemizygous Insertion
		#
		# Display:
		#
		# X/Del(Y)1Psb Sry<dl1Rlb>
		# Tg(Sry)2Ei/0
		#

                if foundBottom >= 1:
                    bottomType1 = bottomType1 + ' ' + allele1
                    bottomType2 = bottomType2 + bottomType3
                else:
		    bottomType1 = allele1
	            bottomType2 = bottomType3

                topType1 = topType2 = topType3
		foundTop = foundTop + 1
		foundBottom = foundBottom + 1

            elif compound == 'Not Applicable':

		#
		# there is one display line per row
		# each row gets its own unique display
		#
		# MGI:3776480
		# Il2rg   Il2rg<tm1Cgn>   Hemizygous X-linked
		# Rag2    Rag2<tm1Fwa>    Homozygous
		#
		# Display:
		#
		# Il2rg<tm1Cgn>/Y
		# Rag2<tm1Fwa>/Rag2<tm1Fwa>
		#

                if foundTop >= 1 and foundBottom >= 1:
                    displayNotes1 = displayNotes1 + topType1 + separatorTopBottom + bottomType1 + notenewline
                    displayNotes2 = displayNotes2 + topType2 + separatorTopBottom + bottomType2 + notenewline
                    topType1 = ''
                    topType2 = ''
                    bottomType1 = ''
                    bottomType2 = ''
                    foundTop = 0
                    foundBottom = 0

                topType1 = allele1
                topType2 = topType3
                bottomType2 = bottomType3

                if alleleState in ['Homozygous', 'Heterozygous']:
                    bottomType1 = allele2

                elif (alleleState == 'Hemizygous Y-linked') or (alleleState == 'Hemizygous Insertion' and chr == 'Y'):
                    topType1 = 'X'
                    bottomType1 = allele1
                    topType2 = topType3
                    bottomType2 = bottomType3

                else:
                    bottomType1 = bottomType3

                displayNotes1 = displayNotes1 + topType1 + separatorTopBottom + bottomType1 + notenewline
                displayNotes2 = displayNotes2 + topType2 + separatorTopBottom + bottomType2 + notenewline

            elif compound == 'Top':

                # new top, new group: process old group

                if foundBottom >= 1:
                    displayNotes1 = displayNotes1 + topType1 + separatorTopBottom + bottomType1 + notenewline
                    displayNotes2 = displayNotes2 + topType2 + separatorTopBottom + bottomType2 + notenewline
                    topType1 = ''
                    topType2 = ''
                    bottomType1 = ''
                    bottomType2 = ''
                    foundTop = 0
                    foundBottom = 0

                # new top, same group: need space to separate tops + existing information

                if foundTop >= 1:
                    topType1 = topType1 + separatorBottom + allele1
                    topType2 = topType2 + ' \Allele(' + mgiID1 + '|' + allele1 + '|)'

		# if there is no top, then copy in existing information

		else:
                    topType1 = allele1
                    topType2 = '\Allele(' + mgiID1 + '|' + allele1 + '|)'

                foundTop = foundTop + 1

            elif compound == 'Bottom':

                # new bottom, same group: need space to separate bottoms + existing information

                if foundBottom >= 1:
                    bottomType1 = bottomType1 + separatorBottom + allele1
		    bottomType2 = bottomType2 + separatorBottom

		    if allele1WildType == 1:
			bottomType2 = bottomType2 + '\AlleleSymbol(' + mgiID1 + '|0)'
                    else:
			bottomType2 = bottomType2 + '\Allele(' + mgiID1 + '|' + allele1 + '|)'

		# if there is no bottom, then copy in existing information

		else:
                    bottomType1 = allele1

		    if allele1WildType == 1:
			bottomType2 = '\AlleleSymbol(' + mgiID1 + '|0)'
                    else:
			bottomType2 = '\Allele(' + mgiID1 + '|' + allele1 + '|)'

                foundBottom = foundBottom + 1

        if foundTop >= 1 and foundBottom >= 1:
            displayNotes1 = displayNotes1 + topType1 + separatorTopBottom + bottomType1 + notenewline
            displayNotes2 = displayNotes2 + topType2 + separatorTopBottom + bottomType2 + notenewline
	    #print displayNotes1
	    #print displayNotes2

	if mode == 'sql':
	    #
	    # initialize the MGI_Note._Note_key primary key
	    #

	    cmd = 'begin transaction;\n'
	    cmd = cmd + 'create temp table noteKeyMax on commit drop as select max(_Note_key) + 1 as noteKey from MGI_Note;\n'
	    cmd = cmd + processNote(g, displayNotes1, combNoteType1) 
	    cmd = cmd + processNote(g, displayNotes2, combNoteType2)
	    cmd = cmd + processNote(g, displayNotes2, combNoteType3)

	    print processNote(g, displayNotes1, combNoteType1)
	    print processNote(g, displayNotes1, combNoteType2)
	    print processNote(g, displayNotes1, combNoteType3)
	    #print cmd

	    cmd = cmd + "commit transaction;\n"

	    db.sql(cmd, None)
        else:
            fp1.write(r['genotypeID'] + reportlib.TAB + displayNotes1 + reportlib.CRT)
            fp2.write(r['genotypeID'] + reportlib.TAB + displayNotes2 + reportlib.CRT)
            fp3.write(r['genotypeID'] + reportlib.TAB + displayNotes2 + reportlib.CRT)

	if DEBUG:
       	    print 'finished with genotype\n'
	    sys.stdout.flush()

    if DEBUG:
        print '\nfinished running allele combination\n'
        sys.stdout.flush()

    if mode == 'bcp':
        reportlib.finish_nonps(fp1)     # non-postscript file
        reportlib.finish_nonps(fp2)     # non-postscript file
        reportlib.finish_nonps(fp3)     # non-postscript file

    db.commit()

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

# all of these invocations will only affect a certain subset of data


if scriptName == 'allelecombination.py':
    processAll()

elif scriptName == 'allelecombinationByAllele.py':
    processByAllele(objectKey)

elif scriptName == 'allelecombinationByMarker.py':
    processByMarker(objectKey)

elif scriptName == 'allelecombinationByGenotype.py':
    processByGenotype(objectKey)
    
db.commit()
db.useOneConnection(0)

