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

${PYTHON} -W "ignore::SyntaxWarning" ${ALLCACHELOAD}/allelecombination.py ${PYTHON_CMD} -K0 | tee -a ${LOG}

setenv DATAFILE 	allelecombnotetype1.rpt
setenv NOTETYPE		"Combination Type 1"
${PYTHON} ${NOTELOAD}/mginoteload.py ${PYTHON_CMD} -I${DATAFILE} -M${NOTEMODE} -O${NOTEOBJECTTYPE} -T"${NOTETYPE}" | tee -a ${LOG}

setenv DATAFILE 	allelecombnotetype2.rpt
setenv NOTETYPE		"Combination Type 2"
${PYTHON} ${NOTELOAD}/mginoteload.py ${PYTHON_CMD} -I${DATAFILE} -M${NOTEMODE} -O${NOTEOBJECTTYPE} -T"${NOTETYPE}" | tee -a ${LOG}

setenv DATAFILE 	allelecombnotetype3.rpt
setenv NOTETYPE		"Combination Type 3"
${PYTHON} ${NOTELOAD}/mginoteload.py ${PYTHON_CMD} -I${DATAFILE} -M${NOTEMODE} -O${NOTEOBJECTTYPE} -T"${NOTETYPE}" | tee -a ${LOG}

date >> ${LOG}

