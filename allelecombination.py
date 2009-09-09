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
# 07/22/2009	lec
#	- TR 7493; allow selection of null marker in def process()
#

import sys 
import os
import getopt
import string
import db
import loadlib
import reportlib

bcpnewline = '\\n'
sqlnewline = '\n'
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

    db.sql('select _Genotype_key = a._Object_key, genotypeID = a.accID into #toprocess ' + \
	'from ACC_Accession a ' + \
	'where a._MGIType_key = 12 ' + \
	'and a._LogicalDB_key = 1 ' + \
	'and a.prefixPart = "MGI:" ' + \
	'and a.preferred = 1', None)
    db.sql('create index idx1 on #toprocess(_Genotype_key)', None)

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

    cmd = 'select distinct _Genotype_key into #toprocess ' + \
	'from GXD_AlleleGenotype ' + \
	'where _Allele_key = %s' % (objectKey)

    db.sql(cmd, None)
    db.sql('create index idx1 on #toprocess(_Genotype_key)', None)

    process('sql')

def processByMarker(objectKey):
    # Purpose: processes data for a specific Marker
    # Returns:
    # Assumes:
    # Effects:
    # Throws:

    # select all Genotypes of a specified Marker

    db.sql('select distinct _Genotype_key into #toprocess ' + \
	'from GXD_AlleleGenotype ' + \
	'where _Marker_key = %s' % (objectKey), None)

    db.sql('create index idx1 on #toprocess(_Genotype_key)', None)

    process('sql')

def processByGenotype(objectKey):
    # Purpose: processes data for a specific Genotype
    # Returns:
    # Assumes:
    # Effects:
    # Throws:

    # select all Genotypes of a specified Genotype

    db.sql('select distinct _Genotype_key into #toprocess ' + \
	'from GXD_AlleleGenotype ' + \
	'where _Genotype_key = %s' % (objectKey), None)

    db.sql('create index idx1 on #toprocess(_Genotype_key)', None)

    process('sql')

def processNote(objectKey, notes, noteTypeKey):
    # Purpose: generate string for MGI Note insertion
    # Returns: noteCmd, a string that contains the insert commands
    # Assumes:
    # Effects:
    # Throws:

    noteCmd = 'insert into MGI_Note' + \
              ' values (@noteKey, %s, %s, %s, %s, %s, getdate(), getdate())\n' % (objectKey, mgiTypeKey, noteTypeKey, userKey, userKey)

    seqNum = 1

    while len(notes) > 255:
	noteCmd = noteCmd + 'insert into MGI_NoteChunk' + \
		' values (@noteKey, %d, "%s", %s, %s, getdate(), getdate())\n' % (seqNum, notes[:255], userKey, userKey)
	notes = notes[255:]
	seqNum = seqNum + 1

    if len(notes) > 0:
	noteCmd = noteCmd + 'insert into MGI_NoteChunk' + \
		' values (@noteKey, %d, "%s", %s, %s, getdate(), getdate())\n' % (seqNum, notes, userKey, userKey)

    # increment the MGI_Note._Note_key

    noteCmd = noteCmd + 'select @noteKey = @noteKey + 1\n'

    return noteCmd

def process(mode):
    # Purpose: process data using either 'sql' or 'bcp' mode
    # Returns:
    # Assumes:
    # Effects:
    # Throws:

    if mode == 'bcp':
	fp1 = reportlib.init('allelecombnotetype1', printHeading = None)
	fp2 = reportlib.init('allelecombnotetype2', printHeading = None)
	fp3 = reportlib.init('allelecombnotetype3', printHeading = None)
	newline = bcpnewline
    else:
	newline = sqlnewline

    # delete existiing Allele Combination notes for Genotypes we're processing

    if DEBUG:
        print '\ndeleting existing allele combination\n'
	sys.stdout.flush()

    db.sql('delete MGI_Note from #toprocess p, MGI_Note n ' + \
	'where p._Genotype_key = n._Object_key ' + \
	'and n._MGIType_key = %s ' % (mgiTypeKey) + \
	'and n._NoteType_key in (%s,%s,%s)' % (combNoteType1, combNoteType2, combNoteType3), None)

    if DEBUG:
        print 'finished deleting existing allele combination\n'
	sys.stdout.flush()

    # read in appropriate records

    if DEBUG:
        print '\nselecting existing allele combination\n'
	sys.stdout.flush()

    cmd = '''select p.*, alleleState = t1.term, compound = t2.term, allele1 = a1.symbol, allele2 = a2.symbol, 
	    allele1WildType = a1.isWildType, allele2WildType = a2.isWildType, 
	    mgiID1 = c1.accID, mgiID2 = c2.accID, g.sequenceNum, m.chromosome 
	    from #toprocess p, GXD_AllelePair g, VOC_Term t1, VOC_Term t2, ALL_Allele a1, ALL_Allele a2, 
	    ACC_Accession c1, ACC_Accession c2, MRK_Marker m 
	    where p._Genotype_key = g._Genotype_key 
	    and g._PairState_key = t1._Term_key 
	    and g._Compound_key = t2._Term_key 
	    and g._Allele_key_1 = a1._Allele_key 
	    and g._Allele_key_2 = a2._Allele_key 
	    and g._Allele_key_1 = c1._Object_key 
	    and c1._MGIType_key = 11 
	    and c1._LogicalDB_key = 1 
	    and c1.prefixPart = "MGI:" 
	    and c1.preferred = 1 
	    and g._Allele_key_2 = c2._Object_key 
	    and c2._MGIType_key = 11 
	    and c2._LogicalDB_key = 1 
	    and c2.prefixPart = "MGI:" 
	    and c2.preferred = 1 
	    and g._Marker_key *= m._Marker_key 
	    union 
	    select p.*, alleleState = t1.term, compound = t2.term, allele1 = a1.symbol, allele2 = null, 
	    allele1WildType = a1.isWildType, allele2WildType = 0, 
	    mgiID1 = c1.accID, mgiID2 = null, g.sequenceNum, m.chromosome 
	    from #toprocess p, GXD_AllelePair g, VOC_Term t1, VOC_Term t2, ALL_Allele a1, 
	    ACC_Accession c1, MRK_Marker m 
	    where p._Genotype_key = g._Genotype_key 
	    and g._PairState_key = t1._Term_key 
	    and g._Compound_key = t2._Term_key 
	    and g._Allele_key_1 = a1._Allele_key 
	    and g._Allele_key_2 is null 
	    and g._Allele_key_1 = c1._Object_key 
	    and c1._MGIType_key = 11 
	    and c1._LogicalDB_key = 1 
	    and c1.prefixPart = "MGI:" 
	    and c1.preferred = 1 
	    and g._Marker_key *= m._Marker_key
	    order by p._Genotype_key, g.sequenceNum'''

    results = db.sql(cmd, 'auto')

    if DEBUG:
        print 'finished selecting existing allele combination\n'
	#print str(results)
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
        displayNotes3 = ''

        topType1 = ''
        topType2 = ''
        topType3 = ''

        bottomType1 = ''
        bottomType2 = ''
        bottomType3 = ''

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

            elif (alleleState == 'Hemizygous Y-linked') or (alleleState == 'Hemizygous Insertion' and chr == 'Y'):
	        if allele1WildType == 1:
	            bottomType3 = '\AlleleSymbol(' + mgiID1 + '|0)'
	        else:
	            bottomType3 = '\Allele(' + mgiID1 + '|' + allele1 + '|)'
                topType3 = 'X'

            displayNotes3 = displayNotes3 + topType3 + '/' + bottomType3 + newline

	    # if Allele Pair does not have a compound attribute

            if compound == 'Not Applicable':

                if foundTop >= 1 and foundBottom >= 1:
                    displayNotes1 = displayNotes1 + topType1 + '/' + bottomType1 + newline
                    displayNotes2 = displayNotes2 + topType2 + '/' + bottomType2 + newline
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

                displayNotes1 = displayNotes1 + topType1 + '/' + bottomType1 + newline
                displayNotes2 = displayNotes2 + topType2 + '/' + bottomType2 + newline

            elif compound == 'Top':

                # new top, new group: process old group

                if foundBottom >= 1:
                    displayNotes1 = displayNotes1 + topType1 + '/' + bottomType1 + newline
                    displayNotes2 = displayNotes2 + topType2 + '/' + bottomType2 + newline
                    topType1 = ''
                    topType2 = ''
                    bottomType1 = ''
                    bottomType2 = ''
                    foundTop = 0
                    foundBottom = 0

                # new top, same group: need space to separate tops + existing information

                if foundTop >= 1:
                    topType1 = topType1 + ' ' + allele1
                    topType2 = topType2 + ' \Allele(' + mgiID1 + '|' + allele1 + '|)'

		# if there is no top, then copy in existing information

		else:
                    topType1 = allele1
                    topType2 = '\Allele(' + mgiID1 + '|' + allele1 + '|)'

                foundTop = foundTop + 1

            elif compound == 'Bottom':

                # new bottom, same group: need space to separate bottoms + existing information

                if foundBottom >= 1:
                    bottomType1 = bottomType1 + ' ' + allele1
                    bottomType2 = bottomType2 + ' '

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

        if foundTop >=1 and foundBottom >= 1:
            displayNotes1 = displayNotes1 + topType1 + '/' + bottomType1 + newline
            displayNotes2 = displayNotes2 + topType2 + '/' + bottomType2 + newline

	if mode == 'sql':
	    #
	    # initialize the MGI_Note._Note_key primary key
	    #

            cmd = 'declare @noteKey integer\n'
            cmd = cmd + 'select @noteKey = max(_Note_key + 1) from MGI_Note\n'

	    cmd = cmd + processNote(g, displayNotes1, combNoteType1) 
	    cmd = cmd + processNote(g, displayNotes2, combNoteType2)
	    cmd = cmd + processNote(g, displayNotes3, combNoteType3)
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
#db.set_sqlLogFunction(db.sqlLogAll)

userKey = loadlib.verifyUser(user, 0, None)

# call functions based on the way the program is invoked

scriptName = os.path.basename(sys.argv[0])

# all of these invocations will only affect a certain subset of data

try:

    if scriptName == 'allelecombination.py':
        processAll()

    elif scriptName == 'allelecombinationByAllele.py':
        processByAllele(objectKey)

    elif scriptName == 'allelecombinationByMarker.py':
        processByMarker(objectKey)

    elif scriptName == 'allelecombinationByGenotype.py':
        processByGenotype(objectKey)

except:

    print 'finished deleting existing allele combination\n'
    sys.stdout.flush()
    
db.useOneConnection(0)

