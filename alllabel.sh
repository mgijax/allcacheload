#!/bin/csh -fx

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

date | tee -a ${LOG}

# Create the bcp file

./alllabel.py | tee -a ${LOG}

# Exit if bcp file is empty

if ( -z ${ALLCACHEBCPDIR}/ALL_Label.bcp ) then
echo 'BCP File is empty' >>& $LOG
exit 0
endif

# Allow bcp into database and truncate tables

${DBUTILSBINDIR}/turnonbulkcopy.csh ${DBSERVER} ${DBNAME} | tee -a ${LOG}
${MGD_DBSCHEMADIR}/table/ALL_Label_truncate.object | tee -a ${LOG}

# Drop indexes
${MGD_DBSCHEMADIR}/index/ALL_Label_drop.object | tee -a ${LOG}

# BCP new data into tables
cat ${DBPASSWORDFILE} | bcp ${DBNAME}..ALL_Label in ${ALLCACHEBCPDIR}/ALL_Label.bcp -c -t\| -S${DBSERVER} -U${DBUSER} | tee -a ${LOG}

# Create indexes
${MGD_DBSCHEMADIR}/index/ALL_Label_create.object | tee -a ${LOG}

date | tee -a ${LOG}
