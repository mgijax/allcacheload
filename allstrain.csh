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

${ALLCACHELOAD}/allstrain.py -S${MGD_DBSERVER} -D${MGD_DBNAME} -U${MGD_DBUSER} -P${MGD_DBPASSWORDFILE} | tee -a ${LOG}

date | tee -a ${LOG}

