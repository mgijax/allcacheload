#!/bin/csh -f

#
# Usage:  alllabel.sh
#
# History
#
# lec	05/17/2000
#

cd `dirname $0` && source ./Configuration

setenv LOG	${ALLCACHELOGDIR}/`basename $0`.log
rm -rf $LOG
touch $LOG

setenv TABLE ALL_Label

date | tee -a ${LOG}

# Create the bcp file

${PYTHON} ./alllabel.py | tee -a ${LOG}

# Exit if bcp file is empty

if ( -z ${ALLCACHEBCPDIR}/ALL_Label.bcp ) then
echo 'BCP File is empty' >>& $LOG
exit 0
endif

# Allow bcp into database and truncate tables

# truncate table
${SCHEMADIR}/table/${TABLE}_truncate.object | tee -a ${LOG}

# Drop indexes
${SCHEMADIR}/index/${TABLE}_drop.object | tee -a ${LOG}

# BCP new data into tables
${BCP_CMD} ${TABLE} ${ALLCACHEBCPDIR} ${TABLE}.bcp ${COLDELIM} ${LINEDELIM} ${PG_DB_SCHEMA} | tee -a ${LOG}

# Create indexes
${SCHEMADIR}/index/${TABLE}_create.object | tee -a ${LOG}

date | tee -a ${LOG}
