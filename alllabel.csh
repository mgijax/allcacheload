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

date | tee -a ${LOG}

# Create the bcp file

./alllabel.py | tee -a ${LOG}

# Exit if bcp file is empty

if ( -z ${ALLCACHEBCPDIR}/ALL_Label.bcp ) then
echo 'BCP File is empty' >>& $LOG
exit 0
endif

# Allow bcp into database and truncate tables

${MGD_DBSCHEMADIR}/table/ALL_Label_truncate.object | tee -a ${LOG}

# Drop indexes
${MGD_DBSCHEMADIR}/index/ALL_Label_drop.object | tee -a ${LOG}

# BCP new data into tables
${MGI_DBUTILS}/bin/bcpin.csh ${MGD_DBSERVER} ${MGD_DBNAME} ALL_Label ${ALLCACHEBCPDIR} ALL_Label.bcp ${COLDELIM} ${LINEDELIM} | tee -a ${LOG}

# Create indexes
${MGD_DBSCHEMADIR}/index/ALL_Label_create.object | tee -a ${LOG}

date | tee -a ${LOG}
