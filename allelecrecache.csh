#!/bin/csh -f

#
# Usage:  allelecrecache.csh
#
# History
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

#
# ad system loader
#   . this product re-sets the GXD_Structure._System_key 
#     for structures where inheritSystem = 1 (true)
#   . it is important to keep these field set correctly for the Cre cache
#
# depending on the modification activity of the 
# EI:Anat. Dictionary module/Anatomical System terms (AST) for high-level structures
# (those where inheritSystem = 0 (false))
# we should either turn this off or on
#
# Turn this OFF if:
#   .  no or low activity
#   .  the EI:AD module:"Refresh AD System Terms" is run AFTER an AST modification
#
# Turn this ON if:
#   . high activity
#   . the EI:AD module:"Refresh AD System Terms" is NOT being run AFTER an AST modification
#
# for the iniital TR9797/TR9163, we are setting this to ON
#

# temporary turn off for testing
#${ADSYSTEMLOAD}/adsystemload.py ${PYTHON_CMD} | tee -a ${LOG}

# Create the bcp file

./allelecrecache.py ${PYTHON_CMD} -K${OBJECTKEY} | tee -a ${LOG}

if ( -z ${ALLCACHEBCPDIR}/${TABLE}.bcp ) then
echo 'BCP File is empty' | tee -a ${LOG}
exit 0
endif

# truncate table
${SCHEMADIR}/table/${TABLE}_truncate.object | tee -a ${LOG}

# Drop indexes
${SCHEMADIR}/index/${TABLE}_drop.object | tee -a ${LOG}

# BCP new data into tables
${BCP_CMD} ${TABLE} ${ALLCACHEBCPDIR} ${TABLE}.bcp ${COLDELIM} ${LINEDELIM} ${SCHEMADIR} | tee -a ${LOG}

# Create indexes
${SCHEMADIR}/index/${TABLE}_create.object | tee -a ${LOG}

date | tee -a ${LOG}
