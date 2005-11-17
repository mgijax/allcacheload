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
import regsub
import db
import mgi_utils
import loadlib

#globals

TAB = '\t'		# tab
DL = os.environ['FIELDDELIM']

inFile = ''	# file descriptor
bcpFile = ''	# file descriptor

inputFileName = os.environ['DGENLEXINPUT']
bcpFileName = os.environ['DGENLEXBCP']
userKey = os.environ['CREATEDBY']

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
    global inFile, bcpFile
 
    db.useOneConnection(1)

    try:
        inFile = open(inputFileName, 'r')
    except:
        exit(1, 'Could not open file %s\n' % inputFileName)

    try:
        bcpFile = open(bcpFileName, 'w')
    except:
        exit(1, 'Could not open file %s\n' % bcpFileName)

    return

# Purpose:  processes data
# Returns:  nothing
# Assumes:  nothing
# Effects:  writes data to output files
# Throws:   nothing

def parseKOlines():

    knockoutKey = 1

    # For each line in the input file

    lineNum = 0

    for line in inFile.readlines():

	# skip header

	if lineNum == 0:
	    lineNum = lineNum + 1
	    continue

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
parseKOlines()
exit(0)

