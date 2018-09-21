
create table client_endpoint_stats (index int ,cluster varchar(255), loghost varchar(255), client varchar(255) ,verb varchar(25) , endpoint varchar(255), mtime bigint ,mtime_epoch int, tqmin int ,tqavg decimal,tqmax int,tqcount int,tqsum int,trmin int,travg decimal,trmax int,trcount int,trsum bigint,ttmin int ,ttavg decimal ,ttmax int,ttcount int,ttsum bigint,ttrmin int,ttravg decimal,ttrmax int,ttrcount int,ttrsum bigint,szmin int,szavg decimal,szmax int,szcount int,szsum bigint,st2count int,st3count int,st4count int,st5count int,stfailpct int);

create table client_verb_stats (index int ,cluster varchar(255), loghost varchar(255), client varchar(255) ,verb varchar(25) , mtime bigint ,mtime_epoch int, tqmin int ,tqavg decimal,tqmax int,tqcount int,tqsum int,trmin int,travg decimal,trmax int,trcount int,trsum bigint,ttmin int ,ttavg decimal ,ttmax int,ttcount int,ttsum bigint,ttrmin int,ttravg decimal,ttrmax int,ttrcount int,ttrsum bigint,szmin int,szavg decimal,szmax int,szcount int,szsum bigint,st2count int,st3count int,st4count int,st5count int,stfailpct int);

create table client_stats (index int ,cluster varchar(255), loghost varchar(255), client varchar(255) , mtime bigint ,mtime_epoch int, tqmin int ,tqavg decimal,tqmax int,tqcount int,tqsum int,trmin int,travg decimal,trmax int,trcount int,trsum bigint,ttmin int ,ttavg decimal ,ttmax int,ttcount int,ttsum bigint,ttrmin int,ttravg decimal,ttrmax int,ttrcount int,ttrsum bigint,szmin int,szavg decimal,szmax int,szcount int,szsum bigint,st2count int,st3count int,st4count int,st5count int,stfailpct int);

create table client_all_stats (index int ,cluster varchar(255), loghost varchar(255), mtime bigint ,mtime_epoch int, tqmin int ,tqavg decimal,tqmax int,tqcount int,tqsum int,trmin int,travg decimal,trmax int,trcount int,trsum bigint,ttmin int ,ttavg decimal ,ttmax int,ttcount int,ttsum bigint,ttrmin int,ttravg decimal,ttrmax int,ttrcount int,ttrsum bigint,szmin int,szavg decimal,szmax int,szcount int,szsum bigint,st2count int,st3count int,st4count int,st5count int,stfailpct int);

create index client_verb_stats_idx1 on client_verb_stats (client,mtime_epoch);
create index client_verb_stats_idx2 on client_verb_stats (client,mtime_epoch,verb);
create index client_verb_stats_idx3 on client_verb_stats (client);
create index client_verb_stats_idx4 on client_verb_stats (mtime_epoch);
create index client_verb_stats_idx5 on client_verb_stats (cluster,client,mtime_epoch,verb);
create index client_verb_stats_idx6 on client_verb_stats (cluster);

create index client_endpoint_stats_idx1 on client_endpoint_stats (database,mtime_epoch);
create index client_endpoint_stats_idx2 on client_endpoint_stats (database,mtime_epoch,verb,endpoint);
create index client_endpoint_stats_idx3 on client_endpoint_stats (cluster,client,mtime_epoch,verb,endpoint);
create index client_endpoint_stats_idx4 on client_endpoint_stats (client);
create index client_endpoint_stats_idx5 on client_endpoint_stats (mtime_epoch);
create index client_endpoint_stats_idx6 on client_endpoint_stats (cluster);
create index client_endpoint_stats_idx7 on client_endpoint_stats (endpoint);

create index client_all_stats_idx1 on client_all_stats (mtime_epoch);
