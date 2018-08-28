drop if exists index verb_stats_idx1 on verb_stats (database,mtime_epoch);
drop if exists index verb_stats_idx2 on verb_stats (database,mtime_epoch,verb);
drop if exists index verb_stats_idx3 on verb_stats (database);
drop if exists index verb_stats_idx4 on verb_stats (mtime_epoch);

drop if exists index endpoint_stats_idx1 on endpoint_stats (database,mtime_epoch);
drop if exists index endpoint_stats_idx2 on endpoint_stats (database,mtime_epoch,verb,endpoint);

drop if exists index document_stats_idx1 on document_stats (database,mtime_epoch);
drop if exists index document_stats_idx2 on document_stats (database,mtime_epoch,verb,endpoint);

drop if exists index all_stats_idx1 on all_stats (mtime_epoch);

drop if exists table document_stats ;
drop if exists table endpoint_stats ;
drop if exists table verb_stats ;
drop if exists table database_stats ;
drop if exists table all_stats ;

