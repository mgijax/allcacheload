#!/bin/csh -f

#
# Template
#


if ( ${?MGICONFIG} == 0 ) then
        setenv MGICONFIG /usr/local/mgi/live/mgiconfig
endif

source ${MGICONFIG}/master.config.csh

cd `dirname $0`

setenv LOG $0.log
rm -rf $LOG
touch $LOG
 
date | tee -a $LOG
 
./allelecrecache.csh

cat - <<EOSQL | ${PG_DBUTILS}/bin/doisql.csh $0 | tee -a $LOG
select distinct symbol, emapaterm as expression_term, cresystemlabel as cre_system, _stage_key
from ALL_Cre_Cache 
where 
(
(
symbol like 'Lhx1%' 
or symbol like 'Cfap126%' 
or symbol like 'Krt19%' 
or symbol = 'Tg(Ella-cre)C5379Lmgd'
or 
symbol in ('Tg(Emx1-cre)3Ito',
	   'Tg(Sox2-cre)1Amc', 
           'Tg(Cdx1-cre)23Kem', 
	   'Tg(Col2a1-cre)1Asz',
	   'Tg(Col2a1-cre)1Bhr',
	   'Tg(EIIa-cre)C5379Lmgd',
	   'Calb2<tm1(cre)Zjh>'
	   )
)
and emapaterm in ('embryo ectoderm', 
	          'embryo endoderm', 
		  'mesoderm', 
		  'node',
		  'primitive streak', 
		  'primitive endoderm',
		  'cartilage',
		  'abdomen',
		  'trunk',
		  'embryo',
		  'epiblast',
		  'alimentary system'
	)
)
or symbol like 'Acan%'
order by symbol, emapaterm, _stage_key
;

select count(*) from all_cre_cache where cresystemlabel is null
;

select distinct symbol, _allele_key, emapaterm as expression_term, cresystemlabel as cre_system, _stage_key
from ALL_Cre_Cache 
where cresystemlabel is null
order by symbol, emapaterm, _stage_key
;

EOSQL

date |tee -a $LOG

