create table document_stats (index int ,cluster varchar(255), loghost varchar(255), database varchar(255) ,verb varchar(25) , endpoint varchar(255), document varchar(1024), mtime bigint ,mtime_epoch int, tqmin int ,tqavg decimal,tqmax int,tqcount int,tqsum int,trmin int,travg decimal,trmax int,trcount int,trsum bigint,ttmin int ,ttavg decimal ,ttmax int,ttcount int,ttsum bigint,ttrmin int,ttravg decimal,ttrmax int,ttrcount int,ttrsum bigint,szmin int,szavg decimal,szmax int,szcount int,szsum bigint,st2count int,st3count int,st4count int,st5count int,stfailpct int);

create table endpoint_stats (index int ,cluster varchar(255), loghost varchar(255), database varchar(255) ,verb varchar(25) , endpoint varchar(255), mtime bigint ,mtime_epoch int, tqmin int ,tqavg decimal,tqmax int,tqcount int,tqsum int,trmin int,travg decimal,trmax int,trcount int,trsum bigint,ttmin int ,ttavg decimal ,ttmax int,ttcount int,ttsum bigint,ttrmin int,ttravg decimal,ttrmax int,ttrcount int,ttrsum bigint,szmin int,szavg decimal,szmax int,szcount int,szsum bigint,st2count int,st3count int,st4count int,st5count int,stfailpct int);

create table verb_stats (index int ,cluster varchar(255), loghost varchar(255), database varchar(255) ,verb varchar(25) , mtime bigint ,mtime_epoch int, tqmin int ,tqavg decimal,tqmax int,tqcount int,tqsum int,trmin int,travg decimal,trmax int,trcount int,trsum bigint,ttmin int ,ttavg decimal ,ttmax int,ttcount int,ttsum bigint,ttrmin int,ttravg decimal,ttrmax int,ttrcount int,ttrsum bigint,szmin int,szavg decimal,szmax int,szcount int,szsum bigint,st2count int,st3count int,st4count int,st5count int,stfailpct int);

create table database_stats (index int ,cluster varchar(255), loghost varchar(255), database varchar(255) , mtime bigint ,mtime_epoch int, tqmin int ,tqavg decimal,tqmax int,tqcount int,tqsum int,trmin int,travg decimal,trmax int,trcount int,trsum bigint,ttmin int ,ttavg decimal ,ttmax int,ttcount int,ttsum bigint,ttrmin int,ttravg decimal,ttrmax int,ttrcount int,ttrsum bigint,szmin int,szavg decimal,szmax int,szcount int,szsum bigint,st2count int,st3count int,st4count int,st5count int,stfailpct int);

create table all_stats (index int ,cluster varchar(255), loghost varchar(255), mtime bigint ,mtime_epoch int, tqmin int ,tqavg decimal,tqmax int,tqcount int,tqsum int,trmin int,travg decimal,trmax int,trcount int,trsum bigint,ttmin int ,ttavg decimal ,ttmax int,ttcount int,ttsum bigint,ttrmin int,ttravg decimal,ttrmax int,ttrcount int,ttrsum bigint,szmin int,szavg decimal,szmax int,szcount int,szsum bigint,st2count int,st3count int,st4count int,st5count int,stfailpct int);

create index verb_stats_idx1 on verb_stats (database,mtime_epoch);
create index verb_stats_idx2 on verb_stats (database,mtime_epoch,verb);
create index verb_stats_idx3 on verb_stats (database);
create index verb_stats_idx4 on verb_stats (mtime_epoch);
create index verb_stats_idx5 on verb_stats (cluster,database,mtime_epoch,verb);
create index verb_stats_idx6 on verb_stats (cluster);

create index endpoint_stats_idx1 on endpoint_stats (database,mtime_epoch);
create index endpoint_stats_idx2 on endpoint_stats (database,mtime_epoch,verb,endpoint);
create index endpoint_stats_idx3 on endpoint_stats (cluster,database,mtime_epoch,verb,endpoint);
create index endpoint_stats_idx4 on endpoint_stats (database);
create index endpoint_stats_idx5 on endpoint_stats (mtime_epoch);
create index endpoint_stats_idx6 on endpoint_stats (cluster);
create index endpoint_stats_idx7 on endpoint_stats (endpoint);

create index document_stats_idx1 on document_stats (database,mtime_epoch);
create index document_stats_idx2 on document_stats (database,mtime_epoch,verb,endpoint);

create index all_stats_idx1 on all_stats (mtime_epoch);
