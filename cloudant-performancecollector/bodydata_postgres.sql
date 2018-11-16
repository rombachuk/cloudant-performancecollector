
create table body_endpoint_stats (index int ,cluster varchar(255), loghost varchar(255), client varchar(255) ,database varchar(1024), verb varchar(25) , endpoint varchar(1024), body varchar(2048),mtime bigint ,mtime_epoch int, tqmin int ,tqavg decimal,tqmax int,tqcount int,tqsum int,trmin int,travg decimal,trmax int,trcount int,trsum bigint,ttmin int ,ttavg decimal ,ttmax int,ttcount int,ttsum bigint,ttrmin int,ttravg decimal,ttrmax int,ttrcount int,ttrsum bigint,szmin int,szavg decimal,szmax int,szcount int,szsum bigint,st2count int,st3count int,st4count int,st5count int,stfailpct int);


create table body_endpoint_stats_s (index int ,cluster varchar(255), loghost varchar(255), client varchar(255) ,database varchar(1024), verb varchar(25) , endpoint varchar(1024), body varchar(2048),mtime bigint ,mtime_epoch int, tqmin int ,tqavg decimal,tqmax int,tqcount int,tqsum int,trmin int,travg decimal,trmax int,trcount int,trsum bigint,ttmin int ,ttavg decimal ,ttmax int,ttcount int,ttsum bigint,ttrmin int,ttravg decimal,ttrmax int,ttrcount int,ttrsum bigint,szmin int,szavg decimal,szmax int,szcount int,szsum bigint,st2count int,st3count int,st4count int,st5count int,stfailpct int);





create index body_endpoint_stats_idx1 on body_endpoint_stats (client,mtime_epoch);
create index body_endpoint_stats_idx2 on body_endpoint_stats (client,mtime_epoch,database,verb,endpoint);
create index body_endpoint_stats_idx3 on body_endpoint_stats (cluster,client,mtime_epoch,database,verb,endpoint,body);
create index body_endpoint_stats_idx4 on body_endpoint_stats (client);
create index body_endpoint_stats_idx5 on body_endpoint_stats (mtime_epoch);
create index body_endpoint_stats_idx6 on body_endpoint_stats (cluster);
create index body_endpoint_stats_idx7 on body_endpoint_stats (endpoint);
create index body_endpoint_stats_idx8 on body_endpoint_stats (database);

create index body_endpoint_stats_s_idx1 on body_endpoint_stats_s (client,mtime_epoch);
create index body_endpoint_stats_s_idx2 on body_endpoint_stats_s (client,mtime_epoch,database,verb,endpoint);
create index body_endpoint_stats_s_idx3 on body_endpoint_stats_s (cluster,client,mtime_epoch,database,verb,endpoint,body);
create index body_endpoint_stats_s_idx4 on body_endpoint_stats_s (client);
create index body_endpoint_stats_s_idx5 on body_endpoint_stats_s (mtime_epoch);
create index body_endpoint_stats_s_idx6 on body_endpoint_stats_s (cluster);
create index body_endpoint_stats_s_idx7 on body_endpoint_stats_s (endpoint);
create index body_endpoint_stats_s_idx8 on body_endpoint_stats_s (database);

