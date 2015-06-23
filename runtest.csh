#!/bin/csh -f

#
# These are tests meant to simulate/test both a sybase version and a postgres version
# of the same code (i.e. flipping)
#
# We are testing both the sybase/postgres SQL counts/return values,
# as well as diffing the BCP files created.
#
# There are instances where the counts/bcp files will not return the same count
# (due primarily to case-insensitivity).  These are noted, if they apply.
#
# see the Configuration file for the DB_TYPE setting.  This setting is first set
# to 'sybase', and then 'postgres'.
#
# Note:  the tests are not perfect.  this is an attempt to automate as much of the
# sybase/postgres flipping test as possible.  
#
# To run:
#	rm -rf runtest.csh.log
#	runtest.csh > runtest.csh.log
#
# 12/15/2014	lec
#	- TR11750/postgres
#

#setenv MGICONFIG /usr/local/mgi/live/mgiconfig
#setenv MGICONFIG /usr/local/mgi/test/mgiconfig
#source ${MGICONFIG}/master.config.csh

cd `dirname $0`

setenv TESTLOG $0.log
rm -rf $TESTLOG
touch $TESTLOG
 
date | tee -a $TESTLOG
 
cat - <<EOSQL | doisql.csh $MGD_DBSERVER $MGD_DBNAME $0 | tee -a $TESTLOG
use $MGD_DBNAME
go

-- allelecombinationByGenotype.py ${PYTHON_CMD} -K58379 : 3 rows 
select * from MGI_Note where MGI_Note._NoteType_key in (1016,1017,1018) and _Object_key = 58379
go

-- allelecombinationByAllele.py ${PYTHON_CMD} -K3144 : 14 rows  : Brca1<tm2Cxd>
select count(n._Note_key) from MGI_Note n, GXD_AlleleGenotype g 
where n._MGIType_key = 12 and n._NoteType_key = 1016 
and g._Allele_key = 3144
and g._Genotype_key = n._Object_key
go

-- allelecombinationByMarker.py ${PYTHON_CMD} -K3144 : 114 rows  : Brac1
select count(n._Note_key) from MGI_Note n, GXD_AlleleGenotype g 
where n._MGIType_key = 12 and n._NoteType_key = 1016 
and g._Marker_key = 24690
and g._Genotype_key = n._Object_key
go

delete from MGI_Note where MGI_Note._NoteType_key in (1016,1017,1018) and _Object_key = 58379
go

-- allelecrecacheByAllele.py ${PYTHON_CMD} -K2232 : 26 rows : MGI:1858007
select count(*) from ALL_Cre_Cache
go
select count(*) from ALL_Cre_Cache where _Allele_key = 2232
go
select count(*) from ALL_Cre_Cache where _Assay_key = 56907
go
delete from ALL_Cre_Cache where _Allele_key = 2232
go
delete from ALL_Cre_Cache where _Assay_key = 56907
go

select distinct _System_key from GXD_Structure
go

checkpoint
go
end
EOSQL

psql -h ${MGD_DBSERVER} -U ${MGD_DBUSER} -d ${MGD_DBNAME} <<EOSQL | tee -a $TESTLOG

-- allelecombinationByGenotype.py ${PYTHON_CMD} -K58379 : 3 rows
select * from MGI_Note where MGI_Note._NoteType_key in (1016,1017,1018) and _Object_key = 58379
;

-- allelecombinationByAllele.py ${PYTHON_CMD} -K3144 : 15 rows : Brca1<tm2Cxd>
select count(n._Note_key) from MGI_Note n, GXD_AlleleGenotype g 
where n._MGIType_key = 12 and n._NoteType_key = 1016 
and g._Allele_key = 3144
and g._Genotype_key = n._Object_key
;

-- allelecombinationByMarker.py ${PYTHON_CMD} -K3144 : 115 rows : Brac1
select count(n._Note_key) from MGI_Note n, GXD_AlleleGenotype g 
where n._MGIType_key = 12 and n._NoteType_key = 1016 
and g._Marker_key = 24690
and g._Genotype_key = n._Object_key
;

delete from MGI_Note where MGI_Note._NoteType_key in (1016,1017,1018) and _Object_key = 58379
;

-- allelecrecacheByAllele.py ${PYTHON_CMD} -K2232 : 26 rows : MGI:1858007
select count(*) from ALL_Cre_Cache
;
select count(*) from ALL_Cre_Cache where _Allele_key = 2232
;
select count(*) from ALL_Cre_Cache where _Assay_key = 56907
;
delete from ALL_Cre_Cache where _Allele_key = 2232
;
delete from ALL_Cre_Cache where _Assay_key = 56907
;

select distinct _System_key from GXD_Structure
;

EOSQL

#
# run test for sybase
#

sed '/setenv DB_TYPE postgres/s//setenv DB_TYPE sybase/g' < Configuration > Configuration.new
mv Configuration.new Configuration
source ./Configuration

alllabel.csh | tee -a $TESTLOG
cp ${DATALOADSOUTPUT}/mgi/allcacheload/output/ALL_Label.bcp ${DATALOADSOUTPUT}/mgi/allcacheload/output/ALL_Label.bcp.sybase

allelecrecache.csh | tee -a $TESTLOG
cp ${DATALOADSOUTPUT}/mgi/allcacheload/output/ALL_Cre_Cache.bcp ${DATALOADSOUTPUT}/mgi/allcacheload/output/ALL_Cre_Cache.bcp.sybase
allelecrecacheByAllele.py ${PYTHON_CMD} -K2232 | tee -a $TESTLOG
allelecrecacheByAssay.py ${PYTHON_CMD} -K56907 | tee -a $TESTLOG

allstrain.csh | tee -a $TESTLOG

allelecombination.csh | tee -a $TESTLOG
cp ${DATALOADSOUTPUT}/mgi/allcacheload/output/allelecombnotetype1.rpt.MGI_Note.bcp ${DATALOADSOUTPUT}/mgi/allcacheload/output/allelecombnotetype1.rpt.MGI_Note.bcp.sybase
cp ${DATALOADSOUTPUT}/mgi/allcacheload/output/allelecombnotetype1.rpt.MGI_NoteChunk.bcp ${DATALOADSOUTPUT}/mgi/allcacheload/output/allelecombnotetype1.rpt.MGI_NoteChunk.bcp.sybase
cp ${DATALOADSOUTPUT}/mgi/allcacheload/output/allelecombnotetype2.rpt.MGI_Note.bcp ${DATALOADSOUTPUT}/mgi/allcacheload/output/allelecombnotetype2.rpt.MGI_Note.bcp.sybase
cp ${DATALOADSOUTPUT}/mgi/allcacheload/output/allelecombnotetype2.rpt.MGI_NoteChunk.bcp ${DATALOADSOUTPUT}/mgi/allcacheload/output/allelecombnotetype2.rpt.MGI_NoteChunk.bcp.sybase
cp ${DATALOADSOUTPUT}/mgi/allcacheload/output/allelecombnotetype3.rpt.MGI_Note.bcp ${DATALOADSOUTPUT}/mgi/allcacheload/output/allelecombnotetype3.rpt.MGI_Note.bcp.sybase
cp ${DATALOADSOUTPUT}/mgi/allcacheload/output/allelecombnotetype3.rpt.MGI_NoteChunk.bcp ${DATALOADSOUTPUT}/mgi/allcacheload/output/allelecombnotetype3.rpt.MGI_NoteChunk.bcp.sybase

allelecombinationByGenotype.py ${PYTHON_CMD} -K58379 | tee -a $TESTLOG
allelecombinationByAllele.py ${PYTHON_CMD} -K3144 | tee -a $TESTLOG
allelecombinationByMarker.py ${PYTHON_CMD} -K24690 | tee -a $TESTLOG

#
# run test for postgres
#

sed '/setenv DB_TYPE sybase/s//setenv DB_TYPE postgres/g' < Configuration > Configuration.new
mv Configuration.new Configuration
source ./Configuration

alllabel.csh | tee -a $TESTLOG
cp ${DATALOADSOUTPUT}/mgi/allcacheload/output/ALL_Label.bcp ${DATALOADSOUTPUT}/mgi/allcacheload/output/ALL_Label.bcp.postgres

allelecrecache.csh | tee -a $TESTLOG
cp ${DATALOADSOUTPUT}/mgi/allcacheload/output/ALL_Cre_Cache.bcp ${DATALOADSOUTPUT}/mgi/allcacheload/output/ALL_Cre_Cache.bcp.postgres
allelecrecacheByAllele.py ${PYTHON_CMD} -K2232 | tee -a ${TESTLOG}
allelecrecacheByAssay.py ${PYTHON_CMD} -K56907 | tee -a ${TESTLOG}

allstrain.csh | tee -a $TESTLOG

allelecombination.csh | tee -a $TESTLOG
cp ${DATALOADSOUTPUT}/mgi/allcacheload/output/allelecombnotetype1.rpt.MGI_Note.bcp ${DATALOADSOUTPUT}/mgi/allcacheload/output/allelecombnotetype1.rpt.MGI_Note.bcp.postgres
cp ${DATALOADSOUTPUT}/mgi/allcacheload/output/allelecombnotetype1.rpt.MGI_NoteChunk.bcp ${DATALOADSOUTPUT}/mgi/allcacheload/output/allelecombnotetype1.rpt.MGI_NoteChunk.bcp.postgres
cp ${DATALOADSOUTPUT}/mgi/allcacheload/output/allelecombnotetype2.rpt.MGI_Note.bcp ${DATALOADSOUTPUT}/mgi/allcacheload/output/allelecombnotetype2.rpt.MGI_Note.bcp.postgres
cp ${DATALOADSOUTPUT}/mgi/allcacheload/output/allelecombnotetype2.rpt.MGI_NoteChunk.bcp ${DATALOADSOUTPUT}/mgi/allcacheload/output/allelecombnotetype2.rpt.MGI_NoteChunk.bcp.postgres
cp ${DATALOADSOUTPUT}/mgi/allcacheload/output/allelecombnotetype3.rpt.MGI_Note.bcp ${DATALOADSOUTPUT}/mgi/allcacheload/output/allelecombnotetype3.rpt.MGI_Note.bcp.postgres
cp ${DATALOADSOUTPUT}/mgi/allcacheload/output/allelecombnotetype3.rpt.MGI_NoteChunk.bcp ${DATALOADSOUTPUT}/mgi/allcacheload/output/allelecombnotetype3.rpt.MGI_NoteChunk.bcp.postgres

allelecombinationByGenotype.py ${PYTHON_CMD} -K58379 | tee -a ${TESTLOG}
allelecombinationByAllele.py ${PYTHON_CMD} -K3144 | tee -a ${TESTLOG}
allelecombinationByMarker.py ${PYTHON_CMD} -K24690 | tee -a ${TESTLOG}

# make sure counts are the same

wc -l ${DATALOADSOUTPUT}/mgi/allcacheload/output/*.bcp.* | tee -a $TESTLOG
wc -l ${DATALOADSOUTPUT}/mgi/allcacheload/output/*.rpt | tee -a $TESTLOG

cat - <<EOSQL | doisql.csh $MGD_DBSERVER $MGD_DBNAME $0 | tee -a $TESTLOG
use $MGD_DBNAME
go
select count(*) from ALL_Label
go
--select distinct _Strain_key from ALL_Allele
--go
select count(*) from ALL_CellLine
go
select count(*) from MGI_Note where _MGIType_key = 12 and _NoteType_key = 1016
go
select count(*) from MGI_Note where _MGIType_key = 12 and _NoteType_key = 1017
go
select count(*) from MGI_Note where _MGIType_key = 12 and _NoteType_key = 1018
go
select count(c._Note_key) from MGI_Note n, MGI_NoteChunk c where n._MGIType_key = 12 and n._NoteType_key = 1016 and n._Note_key = c._Note_key
go
select count(c._Note_key) from MGI_Note n, MGI_NoteChunk c where n._MGIType_key = 12 and n._NoteType_key = 1017 and n._Note_key = c._Note_key
go
select count(c._Note_key) from MGI_Note n, MGI_NoteChunk c where n._MGIType_key = 12 and n._NoteType_key = 1018 and n._Note_key = c._Note_key
go

-- allelecombinationByGenotype.py ${PYTHON_CMD} -K58379 : 3 rows 
select * from MGI_Note where MGI_Note._NoteType_key in (1016,1017,1018) and _Object_key = 58379
go

-- allelecombinationByAllele.py ${PYTHON_CMD} -K3144 : 14 rows  : Brca1<tm2Cxd>
select count(n._Note_key) from MGI_Note n, GXD_AlleleGenotype g 
where n._MGIType_key = 12 and n._NoteType_key = 1016 
and g._Allele_key = 3144
and g._Genotype_key = n._Object_key
go

-- allelecombinationByMarker.py ${PYTHON_CMD} -K3144 : 114 rows  : Brac1
select count(n._Note_key) from MGI_Note n, GXD_AlleleGenotype g 
where n._MGIType_key = 12 and n._NoteType_key = 1016 
and g._Marker_key = 24690
and g._Genotype_key = n._Object_key
go

-- allelecrecacheByAllele.py ${PYTHON_CMD} -K2232 : 26 rows : MGI:1858007
select count(*) from ALL_Cre_Cache
go
select count(*) from ALL_Cre_Cache where _Allele_key = 2232
go
select count(*) from ALL_Cre_Cache where _Assay_key = 56907
go

-- adsystemload : 34
select distinct _System_key from GXD_Structure
go

checkpoint
go
end
EOSQL

psql -h ${MGD_DBSERVER} -U ${MGD_DBUSER} -d ${MGD_DBNAME} <<EOSQL | tee -a $TESTLOG
select count(*) from ALL_Label;
--select distinct _Strain_key from ALL_Allele;
select count(*) from ALL_CellLine;
select count(*) from MGI_Note where _MGIType_key = 12 and _NoteType_key = 1016;
select count(*) from MGI_Note where _MGIType_key = 12 and _NoteType_key = 1017;
select count(*) from MGI_Note where _MGIType_key = 12 and _NoteType_key = 1018;
select count(c._Note_key) from MGI_Note n, MGI_NoteChunk c where n._MGIType_key = 12 and n._NoteType_key = 1016 and n._Note_key = c._Note_key;
select count(c._Note_key) from MGI_Note n, MGI_NoteChunk c where n._MGIType_key = 12 and n._NoteType_key = 1017 and n._Note_key = c._Note_key;
select count(c._Note_key) from MGI_Note n, MGI_NoteChunk c where n._MGIType_key = 12 and n._NoteType_key = 1018 and n._Note_key = c._Note_key;

-- allelecombinationByGenotype.py ${PYTHON_CMD} -K58379 : 3 rows 
select * from MGI_Note where MGI_Note._NoteType_key in (1016,1017,1018) and _Object_key = 58379
;

-- allelecombinationByAllele.py ${PYTHON_CMD} -K3144 : 15 rows : Brca1<tm2Cxd>
select count(n._Note_key) from MGI_Note n, GXD_AlleleGenotype g 
where n._MGIType_key = 12 and n._NoteType_key = 1016 
and g._Allele_key = 3144
and g._Genotype_key = n._Object_key
;

-- allelecombinationByMarker.py ${PYTHON_CMD} -K3144 : 115 rows : Brac1
select count(n._Note_key) from MGI_Note n, GXD_AlleleGenotype g 
where n._MGIType_key = 12 and n._NoteType_key = 1016 
and g._Marker_key = 24690
and g._Genotype_key = n._Object_key
;

-- allelecrecacheByAllele.py ${PYTHON_CMD} -K2232 : 26 rows : MGI:1858007
select count(*) from ALL_Cre_Cache
;
select count(*) from ALL_Cre_Cache where _Allele_key = 2232
;
select count(*) from ALL_Cre_Cache where _Assay_key = 56907
;

-- adsystemload : 34
select distinct _System_key from GXD_Structure
;

EOSQL

date | tee -a $TESTLOG

