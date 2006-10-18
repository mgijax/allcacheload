#!/usr/local/bin/python

#
# Program: dgenlexknockout.py
#
# Original Author: Lori Corbani
#
# Purpose:
#
#	To translate inFile_wIDs.txt and Lexicon input files
#	into input file for MGI_Knockout table
#
# Requirements Satisfied by This Program:
#
# Usage:
#
#	dgenlexknockout.py
#
# Envvars:
#
# Inputs:
#
#       A tab-delimited file in the format:
#		field 1: Gene Name
#		field 2: Gene Symbol
#		field 3: MGI ID
#		field 4: Allele Symbol
#		field 5: Allele ID
#		field 6: Holder
#		field 7: Destination Repository (old)
#		field 8: Destination Repository (new)
#		field 9: JRS ID
#		field 10: NIH ID
#		field 11: Company ID
#		field 12: Seq ID
#		field 13: JTE notes
#
#	Lexicon index.html, an html file
#
# Outputs:
#
#	MGI_Knockout.bcp
#		field 1: Knockout key
#		field 2: MGI Marker key
#		field 3: MGI Allele key
#		field 4: Data Provider (Lexicon or Deltagen)
#		field 5: Repository
#		field 6: Company ID
#		field 7: NIH ID
#		field 8: JRS ID
#
# Exit Codes:
#
# Assumes:
#
# Bugs:
#
# Implementation:
#

import sys
import os
import string
import db
import mgi_utils
import loadlib

#globals

TAB = '\t'		# tab
DL = os.environ['COLDELIM']

inFile = ''	# file descriptor
lexindexFile = ''	# file descriptor
bcpFile = ''	# file descriptor

inputFileName = os.environ['DGENLEXINPUT']
lexindexFileName = os.environ['LEXINDEXFILE']
bcpFileName = os.environ['DGENLEXBCP']
userKey = os.environ['CREATEDBY']

lexIndex = {}

loaddate = loadlib.loaddate

# Purpose: prints error message and exits
# Returns: nothing
# Assumes: nothing
# Effects: exits with exit status
# Throws: nothing

def exit(
    status,          # numeric exit status (integer)
    message = None   # exit message (string)
    ):

    if message is not None:
        sys.stderr.write('\n' + str(message) + '\n')
 
    db.useOneConnection(0)
    sys.exit(status)
 
# Purpose: initialize
# Returns: nothing
# Assumes: nothing
# Effects: initializes global variables
#          exits if files cannot be opened
# Throws: nothing

def init():
    global inFile, lexindexFile, bcpFile
 
    db.useOneConnection(1)

    try:
        inFile = open(inputFileName, 'r')
    except:
        exit(1, 'Could not open file %s\n' % inputFileName)

#    try:
#        lexindexFile = open(lexindexFileName, 'r')
#    except:
#        exit(1, 'Could not open file %s\n' % lexindexFileName)

    try:
        bcpFile = open(bcpFileName, 'w')
    except:
        exit(1, 'Could not open file %s\n' % bcpFileName)

    return

def parseLexIndex():
#
#	parse the Lexicon/index.html file to map the NIH ID to the correct projectid
#

    global lexIndex

# <tr class="searchAltrow2"><TD nowrap valign="top"><a href="2/lexjac1.lexgen.com_3a8080/nih/analysis/treeframe.jsp@projectid=3361
# .htm" target="_blank">NIH-0386</TD><TD valign="top">SEC</TD><TD valign="top">NM_013756</TD><TD valign="top">ACCESSION:NM_013756 NID:7304
# 996 Mus musculus Mus musculus defensin beta 3 (Defb3), mRNA. mouse_refseq</TD></tr>

    for line in lexindexFile.readlines():

	if string.find(line, '<tr class="searchAltrow') < 0:
	    continue

	i = string.find(line, 'projectid')
	j = string.find(line, '.htm')

	if line[i + 9] == '=':
	    value = line[i + 10:j]
	else:
	    value = line[i + 9:j]

	k = string.find(line, 'NIH-')
	l = k + 8
	id = line[k:l]

	lexIndex[id] = value

    lexindexFile.close()

# Purpose:  processes data
# Returns:  nothing
# Assumes:  nothing
# Effects:  writes data to output files
# Throws:   nothing

def parseKOlines():

    global lexIndex

    knockoutKey = 1

    result = db.sql('select max(_Knockout_key) + 1 from ALL_Knockout_Cache', 'auto')
    if result[0][''] != None:
	knockoutKey = result[0]['']

    # For each line in the input file

    lineNum = 0

    for line in inFile.readlines():

	# skip header

#	if lineNum == 0:
#	    lineNum = lineNum + 1
#	    continue

        # Split the line into tokens
        tokens = string.split(line[:-1], TAB)

	# process an actual data line

        try:
	    markerID = tokens[2]
	    alleleID = tokens[4]
	    holder = tokens[5]
	    repository = tokens[7]
	    jrsID = tokens[8]
	    nihID = tokens[9]
	    companyID = tokens[10]

        except:
            print 'Invalid Line (%d): %s\n' % (lineNum, line)

	lineNum = lineNum + 1

	markerKey = loadlib.verifyMarker(markerID, lineNum, None)
	alleleKey = loadlib.verifyObject(alleleID, 11, None, lineNum, None)

	if holder == 'Lexicon':
	    try:
	        companyID = lexIndex[nihID]
            except:
		print 'Could not find %s in Lexicon index file.\n' % (nihID)

	    print companyID

	bcpFile.write('%s' % (knockoutKey) + DL + \
		      '%s' % (markerKey) + DL + \
		      '%s' % (alleleKey) + DL + \
		      '%s' % (holder) + DL + \
		      '%s' % (repository) + DL + \
		      '%s' % (companyID) + DL + \
		      '%s' % (nihID) + DL + \
		      '%s' % (jrsID) + DL + \
		      '%s' % (userKey) + DL + \
		      '%s' % (userKey) + DL + \
		      '%s' % (loaddate) + DL + \
		      '%s\n' % (loaddate))

	knockoutKey = knockoutKey + 1

    inFile.close()
    bcpFile.close()

#
# Main
#

init()
#parseLexIndex()
parseKOlines()
exit(0)

