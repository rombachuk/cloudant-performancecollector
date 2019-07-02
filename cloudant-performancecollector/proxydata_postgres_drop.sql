drop index if exists verb_stats_idx1 ;
drop index if exists verb_stats_idx2 ;
drop index if exists verb_stats_idx3 ;
drop index if exists verb_stats_idx4 ;

drop index if exists endpoint_stats_idx1 ;
drop index if exists endpoint_stats_idx2 ;

drop index if exists document_stats_idx1 ;
drop index if exists document_stats_idx2 ;

drop index if exists all_stats_idx1 ; 

drop table if exists document_stats ;
drop table if exists endpoint_stats ;
drop table if exists verb_stats ;
drop table if exists database_stats ;
drop table if exists all_stats ;

