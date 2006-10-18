#!/bin/csh -fx

#
# Usage:  dgenlexknockout.csh
#
# History
#
# lec	11/14/2005
#	- TR 7194
#

cd `dirname $0` && source ./Configuration

setenv MGD_DBNAME mgd_wi2

setenv LOG	${ALLCACHELOGDIR}/`basename $0`.log
rm -rf $LOG
touch $LOG

date | tee -a ${LOG}

# Create the bcp file

./dgenlexknockout.py | tee -a ${LOG}

if ( -z ${DGENLEXBCP} ) then
echo 'BCP File is empty' | tee -a ${LOG}
exit 0
endif

# truncate tables

#${MGD_DBSCHEMADIR}/table/ALL_Knockout_Cache_truncate.object | tee -a ${LOG}

# Drop indexes
#${MGD_DBSCHEMADIR}/index/ALL_Knockout_Cache_drop.object | tee -a ${LOG}

# BCP new data into tables
cat ${MGD_DBPASSWORDFILE} | bcp ${MGD_DBNAME}..ALL_Knockout_Cache in ${DGENLEXBCP} -e ${DGENLEXBCPERR} -c -t${COLDELIM} -S${MGD_DBSERVER} -U${MGD_DBUSER} | tee -a ${LOG}

# Create indexes
#${MGD_DBSCHEMADIR}/index/ALL_Knockout_Cache_create.object | tee -a ${LOG}

date | tee -a ${LOG}
