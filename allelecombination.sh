#!/bin/csh -fx

#
# Wrapper script to create & load Allele Combination Notes into MGI_Note
#
# Usage:  allelecombination.sh
#

cd `dirname $0` && source ./Configuration

setenv LOG	${ALLCACHELOGDIR}/`basename $0`.log
rm -rf $LOG
touch $LOG

date | tee -a ${LOG}

setenv LOG `basename $0`.log

rm -rf ${LOG}
touch ${LOG}
 
date >> ${LOG}

cd ${ALLCACHEBCPDIR}

${ALLCACHEINSTALLDIR}/allelecombination.py -S${DBSERVER} -D${DBNAME} -U${DBUSER} -P${DBPASSWORDFILE} -K0 | tee -a ${LOG}

setenv DATAFILE 	allelecombnotetype1.rpt
setenv NOTETYPE		"Combination Type 1"
${NOTELOAD}/mginoteload.py -S${DBSERVER} -D${DBNAME} -U${DBUSER} -P${DBPASSWORDFILE} -I${DATAFILE} -M${NOTEMODE} -O${NOTEOBJECTTYPE} -T"${NOTETYPE}" | tee -a ${LOG}

setenv DATAFILE 	allelecombnotetype2.rpt
setenv NOTETYPE		"Combination Type 2"
${NOTELOAD}/mginoteload.py -S${DBSERVER} -D${DBNAME} -U${DBUSER} -P${DBPASSWORDFILE} -I${DATAFILE} -M${NOTEMODE} -O${NOTEOBJECTTYPE} -T"${NOTETYPE}" | tee -a ${LOG}

setenv DATAFILE 	allelecombnotetype3.rpt
setenv NOTETYPE		"Combination Type 3"
${NOTELOAD}/mginoteload.py -S${DBSERVER} -D${DBNAME} -U${DBUSER} -P${DBPASSWORDFILE} -I${DATAFILE} -M${NOTEMODE} -O${NOTEOBJECTTYPE} -T"${NOTETYPE}" | tee -a ${LOG}

date >> ${LOG}
