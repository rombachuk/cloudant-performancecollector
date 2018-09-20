create table db_stats (index int , cluster varchar(255),database varchar(255) ,mtime bigint ,mtime_epoch int, doc_count int ,del_doc_count int,disk_size bigint,data_size bigint,shard_count int);

create table view_stats (index int , cluster varchar(255),database varchar(255) ,viewdoc varchar(255),view varchar(255), signature varchar(35),mtime bigint ,mtime_epoch int,
disk_size bigint,data_size bigint, active_size bigint, updates_pending_total int, updates_pending_minimum int, updates_pending_preferred int, shardcount int);

create index db_stats_idx1 on db_stats (cluster,database,mtime_epoch);
create index view_stats_idx1 on view_stats (cluster,database,mtime_epoch);
