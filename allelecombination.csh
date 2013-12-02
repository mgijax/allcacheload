#!/bin/csh -f

#
# Wrapper script to create & load Allele Combination Notes into MGI_Note
#
# Usage:  allelecombination.sh
#

cd `dirname $0` && source ./Configuration

setenv LOG	${ALLCACHELOGDIR}/`basename $0`.log
rm -rf $LOG
touch $LOG

date >> ${LOG}

cd ${ALLCACHEBCPDIR}

${ALLCACHELOAD}/allelecombination.py -S${MGD_DBSERVER} -D${MGD_DBNAME} -U${MGD_DBUSER} -P${MGD_DBPASSWORDFILE} -K0 | tee -a ${LOG}

setenv DATAFILE 	allelecombnotetype1.rpt
setenv NOTETYPE		"Combination Type 1"
${NOTELOAD}/mginoteload.py -S${MGD_DBSERVER} -D${MGD_DBNAME} -U${MGD_DBUSER} -P${MGD_DBPASSWORDFILE} -I${DATAFILE} -M${NOTEMODE} -O${NOTEOBJECTTYPE} -T"${NOTETYPE}" | tee -a ${LOG}

setenv DATAFILE 	allelecombnotetype2.rpt
setenv NOTETYPE		"Combination Type 2"
${NOTELOAD}/mginoteload.py -S${MGD_DBSERVER} -D${MGD_DBNAME} -U${MGD_DBUSER} -P${MGD_DBPASSWORDFILE} -I${DATAFILE} -M${NOTEMODE} -O${NOTEOBJECTTYPE} -T"${NOTETYPE}" | tee -a ${LOG}

setenv DATAFILE 	allelecombnotetype3.rpt
setenv NOTETYPE		"Combination Type 3"
${NOTELOAD}/mginoteload.py -S${MGD_DBSERVER} -D${MGD_DBNAME} -U${MGD_DBUSER} -P${MGD_DBPASSWORDFILE} -I${DATAFILE} -M${NOTEMODE} -O${NOTEOBJECTTYPE} -T"${NOTETYPE}" | tee -a ${LOG}

date >> ${LOG}

