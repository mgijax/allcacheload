#!/bin/csh -f

#
# Wrapper script to run the Allele SOO/Parent Cell Line Strain update
#
# Usage:  allstrain.csh
#

cd `dirname $0` && source ./Configuration && source ${QCRPTS}/Configuration

setenv LOG	${ALLCACHELOGDIR}/`basename $0`.log
rm -rf $LOG
touch $LOG

date | tee -a ${LOG}

echo 'running version...' ${DB_TYPE} >> $LOG

if ( ${DB_TYPE} == "postgres" ) then

${ALLCACHELOAD}/allstrain.py -S${PG_DBSERVER} -D${PG_DBNAME} -U${PG_DBUSER} -P${PG_1LINE_PASSFILE} | tee -a ${LOG}

else

${ALLCACHELOAD}/allstrain.py -S${MGD_DBSERVER} -D${MGD_DBNAME} -U${MGD_DBUSER} -P${MGD_DBPASSWORDFILE} | tee -a ${LOG}

endif

date | tee -a ${LOG}

