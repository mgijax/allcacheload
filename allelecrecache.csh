#!/bin/csh -f

#
# Usage:  allelecrecache.csh
#
# History
#
# lec	01/08/2016
# 	- TR12223/gxd anatomy II
#
# lec	09/01/2009
#	- TR9164/cre
#

cd `dirname $0` && source ./Configuration

setenv TABLE ALL_Cre_Cache
setenv OBJECTKEY 0

setenv LOG	${ALLCACHELOGDIR}/`basename $0 .csh`.log
rm -rf $LOG
touch $LOG

date | tee -a ${LOG}

# Create the bcp file

${PYTHON} ./allelecrecache.py ${PYTHON_CMD} -K${OBJECTKEY} | tee -a ${LOG}

if ( -z ${ALLCACHEBCPDIR}/${TABLE}.bcp ) then
echo 'BCP File is empty' | tee -a ${LOG}
exit 0
endif

# truncate table
${SCHEMADIR}/table/${TABLE}_truncate.object | tee -a ${LOG}

# Drop indexes
${SCHEMADIR}/index/${TABLE}_drop.object | tee -a ${LOG}

# BCP new data into tables
${BCP_CMD} ${TABLE} ${ALLCACHEBCPDIR} ${TABLE}.bcp ${COLDELIM} ${LINEDELIM} ${PG_DB_SCHEMA} | tee -a ${LOG}

# Create indexes
${SCHEMADIR}/index/${TABLE}_create.object | tee -a ${LOG}

date | tee -a ${LOG}
