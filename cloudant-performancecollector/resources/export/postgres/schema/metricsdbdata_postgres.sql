create table db_stats (index int , cluster varchar(255),database varchar(255) ,mtime bigint ,mtime_epoch int, doc_count int ,del_doc_count int,disk_size bigint,data_size bigint);

create table view_stats (index int , cluster varchar(255),database varchar(255) ,viewdoc varchar(255),view varchar(255), signature varchar(35),mtime bigint ,mtime_epoch int,
disk_size bigint,data_size bigint, active_size bigint, updates_pending_total int, updates_pending_minimum int, updates_pending_preferred int);

create table smoosh_stats (index int , cluster varchar(255),host varchar(255) ,channel varchar(255), mtime bigint ,mtime_epoch int, active int, waiting int, starting int);

create table ioq_stats (index int , cluster varchar(255),host varchar(255) ,ioqtype varchar(255), mtime bigint ,mtime_epoch int, requests bigint);

create table host_stats (index int , cluster varchar(255),host varchar(255) , mtime bigint ,mtime_epoch int, doc_writes bigint, doc_inserts bigint,
ioql_max decimal(8,3), ioql_med decimal(8,3), ioql_pctl_90 decimal(8,3), ioql_pctl_99 decimal(8,3), ioql_pctl_999 decimal(8,3));

create index db_stats_idx1 on db_stats (cluster,database,mtime_epoch);
create index view_stats_idx1 on view_stats (cluster,database,mtime_epoch);
create index smoosh_stats_idx1 on smoosh_stats (cluster,host,mtime_epoch);
create index ioq_stats_idx1 on ioq_stats (cluster,host,mtime_epoch);
create index host_stats_idx1 on host_stats (cluster,host,mtime_epoch);