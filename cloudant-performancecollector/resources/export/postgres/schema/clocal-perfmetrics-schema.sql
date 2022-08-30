-- Table: public.all_stats

-- DROP TABLE IF EXISTS public.all_stats;

CREATE TABLE IF NOT EXISTS public.all_stats
(
    index integer,
    cluster character varying(255) COLLATE pg_catalog."default",
    loghost character varying(255) COLLATE pg_catalog."default",
    mtime bigint,
    mtime_epoch integer,
    tqmin integer,
    tqavg numeric,
    tqmax integer,
    tqcount integer,
    tqsum integer,
    tcmin integer,
    tcavg numeric,
    tcmax integer,
    tccount integer,
    tcsum integer,
    trmin integer,
    travg numeric,
    trmax integer,
    trcount integer,
    trsum bigint,
    ttmin integer,
    ttavg numeric,
    ttmax integer,
    ttcount integer,
    ttsum bigint,
    ttrmin integer,
    ttravg numeric,
    ttrmax integer,
    ttrcount integer,
    ttrsum bigint,
    szmin integer,
    szavg numeric,
    szmax integer,
    szcount integer,
    szsum bigint,
    femin integer,
    feavg numeric,
    femax integer,
    fecount integer,
    fesum bigint,
    bemin integer,
    beavg numeric,
    bemax integer,
    becount integer,
    besum bigint,
    st2count integer,
    st3count integer,
    st4count integer,
    st5count integer,
    stfailpct integer
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.all_stats
    OWNER to postgres;
-- Index: all_stats_idx1

-- DROP INDEX IF EXISTS public.all_stats_idx1;

CREATE INDEX IF NOT EXISTS all_stats_idx1
    ON public.all_stats USING btree
    (mtime_epoch ASC NULLS LAST)
    TABLESPACE pg_default;

-- Table: public.body_endpoint_stats

-- DROP TABLE IF EXISTS public.body_endpoint_stats;

CREATE TABLE IF NOT EXISTS public.body_endpoint_stats
(
    index integer,
    cluster character varying(255) COLLATE pg_catalog."default",
    loghost character varying(255) COLLATE pg_catalog."default",
    client character varying(255) COLLATE pg_catalog."default",
    database character varying(255) COLLATE pg_catalog."default",
    verb character varying(25) COLLATE pg_catalog."default",
    endpoint character varying(255) COLLATE pg_catalog."default",
    body character varying(1024) COLLATE pg_catalog."default",
    mtime bigint,
    mtime_epoch integer,
    tqmin integer,
    tqavg numeric,
    tqmax integer,
    tqcount integer,
    tqsum integer,
    tcmin integer,
    tcavg numeric,
    tcmax integer,
    tccount integer,
    tcsum integer,
    trmin integer,
    travg numeric,
    trmax integer,
    trcount integer,
    trsum bigint,
    ttmin integer,
    ttavg numeric,
    ttmax integer,
    ttcount integer,
    ttsum bigint,
    ttrmin integer,
    ttravg numeric,
    ttrmax integer,
    ttrcount integer,
    ttrsum bigint,
    szmin integer,
    szavg numeric,
    szmax integer,
    szcount integer,
    szsum bigint,
    femin integer,
    feavg numeric,
    femax integer,
    fecount integer,
    fesum bigint,
    bemin integer,
    beavg numeric,
    bemax integer,
    becount integer,
    besum bigint,
    st2count integer,
    st3count integer,
    st4count integer,
    st5count integer,
    stfailpct integer
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.body_endpoint_stats
    OWNER to postgres;

-- Table: public.body_endpoint_stats_s

-- DROP TABLE IF EXISTS public.body_endpoint_stats_s;

CREATE TABLE IF NOT EXISTS public.body_endpoint_stats_s
(
    index integer,
    cluster character varying(255) COLLATE pg_catalog."default",
    loghost character varying(255) COLLATE pg_catalog."default",
    client character varying(255) COLLATE pg_catalog."default",
    database character varying(255) COLLATE pg_catalog."default",
    verb character varying(25) COLLATE pg_catalog."default",
    endpoint character varying(255) COLLATE pg_catalog."default",
    body character varying(1024) COLLATE pg_catalog."default",
    mtime bigint,
    mtime_epoch integer,
    tqmin integer,
    tqavg numeric,
    tqmax integer,
    tqcount integer,
    tqsum integer,
    tcmin integer,
    tcavg numeric,
    tcmax integer,
    tccount integer,
    tcsum integer,
    trmin integer,
    travg numeric,
    trmax integer,
    trcount integer,
    trsum bigint,
    ttmin integer,
    ttavg numeric,
    ttmax integer,
    ttcount integer,
    ttsum bigint,
    ttrmin integer,
    ttravg numeric,
    ttrmax integer,
    ttrcount integer,
    ttrsum bigint,
    szmin integer,
    szavg numeric,
    szmax integer,
    szcount integer,
    szsum bigint,
    femin integer,
    feavg numeric,
    femax integer,
    fecount integer,
    fesum bigint,
    bemin integer,
    beavg numeric,
    bemax integer,
    becount integer,
    besum bigint,
    st2count integer,
    st3count integer,
    st4count integer,
    st5count integer,
    stfailpct integer
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.body_endpoint_stats_s
    OWNER to postgres;
-- Index: bdy_enpoint_stats_s_idx2

-- DROP INDEX IF EXISTS public.bdy_enpoint_stats_s_idx2;

CREATE INDEX IF NOT EXISTS bdy_enpoint_stats_s_idx2
    ON public.body_endpoint_stats_s USING btree
    (cluster COLLATE pg_catalog."default" ASC NULLS LAST, loghost COLLATE pg_catalog."default" ASC NULLS LAST, verb COLLATE pg_catalog."default" ASC NULLS LAST, endpoint COLLATE pg_catalog."default" ASC NULLS LAST, mtime_epoch ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: bdy_enpoint_stats_s_idx3

-- DROP INDEX IF EXISTS public.bdy_enpoint_stats_s_idx3;

CREATE INDEX IF NOT EXISTS bdy_enpoint_stats_s_idx3
    ON public.body_endpoint_stats_s USING btree
    (mtime_epoch ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: bdy_enpoint_stats_s_idx4

-- DROP INDEX IF EXISTS public.bdy_enpoint_stats_s_idx4;

CREATE INDEX IF NOT EXISTS bdy_enpoint_stats_s_idx4
    ON public.body_endpoint_stats_s USING btree
    (mtime ASC NULLS LAST)
    TABLESPACE pg_default;

-- Table: public.client_endpoint_stats

-- DROP TABLE IF EXISTS public.client_endpoint_stats;

CREATE TABLE IF NOT EXISTS public.client_endpoint_stats
(
    index integer,
    cluster character varying(255) COLLATE pg_catalog."default",
    loghost character varying(255) COLLATE pg_catalog."default",
    client character varying(255) COLLATE pg_catalog."default",
    verb character varying(25) COLLATE pg_catalog."default",
    endpoint character varying(255) COLLATE pg_catalog."default",
    mtime bigint,
    mtime_epoch integer,
    tqmin integer,
    tqavg numeric,
    tqmax integer,
    tqcount integer,
    tqsum integer,
    tcmin integer,
    tcavg numeric,
    tcmax integer,
    tccount integer,
    tcsum integer,
    trmin integer,
    travg numeric,
    trmax integer,
    trcount integer,
    trsum bigint,
    ttmin integer,
    ttavg numeric,
    ttmax integer,
    ttcount integer,
    ttsum bigint,
    ttrmin integer,
    ttravg numeric,
    ttrmax integer,
    ttrcount integer,
    ttrsum bigint,
    szmin integer,
    szavg numeric,
    szmax integer,
    szcount integer,
    szsum bigint,
    femin integer,
    feavg numeric,
    femax integer,
    fecount integer,
    fesum bigint,
    bemin integer,
    beavg numeric,
    bemax integer,
    becount integer,
    besum bigint,
    st2count integer,
    st3count integer,
    st4count integer,
    st5count integer,
    stfailpct integer
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.client_endpoint_stats
    OWNER to postgres;
-- Index: client_endpoint_stats_idx1

-- DROP INDEX IF EXISTS public.client_endpoint_stats_idx1;

CREATE INDEX IF NOT EXISTS client_endpoint_stats_idx1
    ON public.client_endpoint_stats USING btree
    (client COLLATE pg_catalog."default" ASC NULLS LAST, mtime_epoch ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: client_endpoint_stats_idx2

-- DROP INDEX IF EXISTS public.client_endpoint_stats_idx2;

CREATE INDEX IF NOT EXISTS client_endpoint_stats_idx2
    ON public.client_endpoint_stats USING btree
    (client COLLATE pg_catalog."default" ASC NULLS LAST, mtime_epoch ASC NULLS LAST, verb COLLATE pg_catalog."default" ASC NULLS LAST, endpoint COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: client_endpoint_stats_idx3

-- DROP INDEX IF EXISTS public.client_endpoint_stats_idx3;

CREATE INDEX IF NOT EXISTS client_endpoint_stats_idx3
    ON public.client_endpoint_stats USING btree
    (cluster COLLATE pg_catalog."default" ASC NULLS LAST, client COLLATE pg_catalog."default" ASC NULLS LAST, mtime_epoch ASC NULLS LAST, verb COLLATE pg_catalog."default" ASC NULLS LAST, endpoint COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: client_endpoint_stats_idx4

-- DROP INDEX IF EXISTS public.client_endpoint_stats_idx4;

CREATE INDEX IF NOT EXISTS client_endpoint_stats_idx4
    ON public.client_endpoint_stats USING btree
    (client COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: client_endpoint_stats_idx5

-- DROP INDEX IF EXISTS public.client_endpoint_stats_idx5;

CREATE INDEX IF NOT EXISTS client_endpoint_stats_idx5
    ON public.client_endpoint_stats USING btree
    (mtime_epoch ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: client_endpoint_stats_idx6

-- DROP INDEX IF EXISTS public.client_endpoint_stats_idx6;

CREATE INDEX IF NOT EXISTS client_endpoint_stats_idx6
    ON public.client_endpoint_stats USING btree
    (cluster COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: client_endpoint_stats_idx7

-- DROP INDEX IF EXISTS public.client_endpoint_stats_idx7;

CREATE INDEX IF NOT EXISTS client_endpoint_stats_idx7
    ON public.client_endpoint_stats USING btree
    (endpoint COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;

-- Table: public.client_verb_stats

-- DROP TABLE IF EXISTS public.client_verb_stats;

CREATE TABLE IF NOT EXISTS public.client_verb_stats
(
    index integer,
    cluster character varying(255) COLLATE pg_catalog."default",
    loghost character varying(255) COLLATE pg_catalog."default",
    client character varying(255) COLLATE pg_catalog."default",
    verb character varying(25) COLLATE pg_catalog."default",
    mtime bigint,
    mtime_epoch integer,
    tqmin integer,
    tqavg numeric,
    tqmax integer,
    tqcount integer,
    tqsum integer,
    tcmin integer,
    tcavg numeric,
    tcmax integer,
    tccount integer,
    tcsum integer,
    trmin integer,
    travg numeric,
    trmax integer,
    trcount integer,
    trsum bigint,
    ttmin integer,
    ttavg numeric,
    ttmax integer,
    ttcount integer,
    ttsum bigint,
    ttrmin integer,
    ttravg numeric,
    ttrmax integer,
    ttrcount integer,
    ttrsum bigint,
    szmin integer,
    szavg numeric,
    szmax integer,
    szcount integer,
    szsum bigint,
    femin integer,
    feavg numeric,
    femax integer,
    fecount integer,
    fesum bigint,
    bemin integer,
    beavg numeric,
    bemax integer,
    becount integer,
    besum bigint,
    st2count integer,
    st3count integer,
    st4count integer,
    st5count integer,
    stfailpct integer
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.client_verb_stats
    OWNER to postgres;
-- Index: client_verb_stats_idx1

-- DROP INDEX IF EXISTS public.client_verb_stats_idx1;

CREATE INDEX IF NOT EXISTS client_verb_stats_idx1
    ON public.client_verb_stats USING btree
    (client COLLATE pg_catalog."default" ASC NULLS LAST, mtime_epoch ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: client_verb_stats_idx2

-- DROP INDEX IF EXISTS public.client_verb_stats_idx2;

CREATE INDEX IF NOT EXISTS client_verb_stats_idx2
    ON public.client_verb_stats USING btree
    (client COLLATE pg_catalog."default" ASC NULLS LAST, mtime_epoch ASC NULLS LAST, verb COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: client_verb_stats_idx3

-- DROP INDEX IF EXISTS public.client_verb_stats_idx3;

CREATE INDEX IF NOT EXISTS client_verb_stats_idx3
    ON public.client_verb_stats USING btree
    (client COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: client_verb_stats_idx4

-- DROP INDEX IF EXISTS public.client_verb_stats_idx4;

CREATE INDEX IF NOT EXISTS client_verb_stats_idx4
    ON public.client_verb_stats USING btree
    (mtime_epoch ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: client_verb_stats_idx5

-- DROP INDEX IF EXISTS public.client_verb_stats_idx5;

CREATE INDEX IF NOT EXISTS client_verb_stats_idx5
    ON public.client_verb_stats USING btree
    (cluster COLLATE pg_catalog."default" ASC NULLS LAST, client COLLATE pg_catalog."default" ASC NULLS LAST, mtime_epoch ASC NULLS LAST, verb COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: client_verb_stats_idx6

-- DROP INDEX IF EXISTS public.client_verb_stats_idx6;

CREATE INDEX IF NOT EXISTS client_verb_stats_idx6
    ON public.client_verb_stats USING btree
    (cluster COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;

-- Table: public.collector_stats

-- DROP TABLE IF EXISTS public.collector_stats;

CREATE TABLE IF NOT EXISTS public.collector_stats
(
    cluster character varying(60) COLLATE pg_catalog."default",
    node character varying(60) COLLATE pg_catalog."default",
    mtime_epoch integer,
    measure character varying(128) COLLATE pg_catalog."default",
    value numeric(18,2),
    counterseq bigint,
    mtime_epoch_full bigint
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.collector_stats
    OWNER to postgres;
-- Index: collector_stats_idx1

-- DROP INDEX IF EXISTS public.collector_stats_idx1;

CREATE INDEX IF NOT EXISTS collector_stats_idx1
    ON public.collector_stats USING btree
    (cluster COLLATE pg_catalog."default" ASC NULLS LAST, node COLLATE pg_catalog."default" ASC NULLS LAST, measure COLLATE pg_catalog."default" ASC NULLS LAST, mtime_epoch ASC NULLS LAST)
    TABLESPACE pg_default;

-- Table: public.database_stats

-- DROP TABLE IF EXISTS public.database_stats;

CREATE TABLE IF NOT EXISTS public.database_stats
(
    index integer,
    cluster character varying(255) COLLATE pg_catalog."default",
    loghost character varying(255) COLLATE pg_catalog."default",
    database character varying(255) COLLATE pg_catalog."default",
    mtime bigint,
    mtime_epoch integer,
    tqmin integer,
    tqavg numeric,
    tqmax integer,
    tqcount integer,
    tqsum integer,
    tcmin integer,
    tcavg numeric,
    tcmax integer,
    tccount integer,
    tcsum integer,
    trmin integer,
    travg numeric,
    trmax integer,
    trcount integer,
    trsum bigint,
    ttmin integer,
    ttavg numeric,
    ttmax integer,
    ttcount integer,
    ttsum bigint,
    ttrmin integer,
    ttravg numeric,
    ttrmax integer,
    ttrcount integer,
    ttrsum bigint,
    szmin integer,
    szavg numeric,
    szmax integer,
    szcount integer,
    szsum bigint,
    femin integer,
    feavg numeric,
    femax integer,
    fecount integer,
    fesum bigint,
    bemin integer,
    beavg numeric,
    bemax integer,
    becount integer,
    besum bigint,
    st2count integer,
    st3count integer,
    st4count integer,
    st5count integer,
    stfailpct integer
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.database_stats
    OWNER to postgres;

-- Table: public.db_stats

-- DROP TABLE IF EXISTS public.db_stats;

CREATE TABLE IF NOT EXISTS public.db_stats
(
    index integer,
    cluster character varying(255) COLLATE pg_catalog."default",
    database character varying(255) COLLATE pg_catalog."default",
    mtime bigint,
    mtime_epoch integer,
    doc_count integer,
    del_doc_count integer,
    disk_size bigint,
    data_size bigint,
    shard_count integer
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.db_stats
    OWNER to postgres;
-- Index: db_stats_idx1

-- DROP INDEX IF EXISTS public.db_stats_idx1;

CREATE INDEX IF NOT EXISTS db_stats_idx1
    ON public.db_stats USING btree
    (cluster COLLATE pg_catalog."default" ASC NULLS LAST, database COLLATE pg_catalog."default" ASC NULLS LAST, mtime_epoch ASC NULLS LAST)
    TABLESPACE pg_default;

-- Table: public.document_stats

-- DROP TABLE IF EXISTS public.document_stats;

CREATE TABLE IF NOT EXISTS public.document_stats
(
    index integer,
    cluster character varying(255) COLLATE pg_catalog."default",
    loghost character varying(255) COLLATE pg_catalog."default",
    database character varying(255) COLLATE pg_catalog."default",
    verb character varying(25) COLLATE pg_catalog."default",
    endpoint character varying(255) COLLATE pg_catalog."default",
    document character varying(1024) COLLATE pg_catalog."default",
    mtime bigint,
    mtime_epoch integer,
    tqmin integer,
    tqavg numeric,
    tqmax integer,
    tqcount integer,
    tqsum integer,
    tcmin integer,
    tcavg numeric,
    tcmax integer,
    tccount integer,
    tcsum integer,
    trmin integer,
    travg numeric,
    trmax integer,
    trcount integer,
    trsum bigint,
    ttmin integer,
    ttavg numeric,
    ttmax integer,
    ttcount integer,
    ttsum bigint,
    ttrmin integer,
    ttravg numeric,
    ttrmax integer,
    ttrcount integer,
    ttrsum bigint,
    szmin integer,
    szavg numeric,
    szmax integer,
    szcount integer,
    szsum bigint,
    femin integer,
    feavg numeric,
    femax integer,
    fecount integer,
    fesum bigint,
    bemin integer,
    beavg numeric,
    bemax integer,
    becount integer,
    besum bigint,
    st2count integer,
    st3count integer,
    st4count integer,
    st5count integer,
    stfailpct integer
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.document_stats
    OWNER to postgres;
-- Index: document_stats_idx1

-- DROP INDEX IF EXISTS public.document_stats_idx1;

CREATE INDEX IF NOT EXISTS document_stats_idx1
    ON public.document_stats USING btree
    (database COLLATE pg_catalog."default" ASC NULLS LAST, mtime_epoch ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: document_stats_idx2

-- DROP INDEX IF EXISTS public.document_stats_idx2;

CREATE INDEX IF NOT EXISTS document_stats_idx2
    ON public.document_stats USING btree
    (database COLLATE pg_catalog."default" ASC NULLS LAST, mtime_epoch ASC NULLS LAST, verb COLLATE pg_catalog."default" ASC NULLS LAST, endpoint COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;

-- Table: public.endpoint_stats

-- DROP TABLE IF EXISTS public.endpoint_stats;

CREATE TABLE IF NOT EXISTS public.endpoint_stats
(
    index integer,
    cluster character varying(255) COLLATE pg_catalog."default",
    loghost character varying(255) COLLATE pg_catalog."default",
    database character varying(255) COLLATE pg_catalog."default",
    verb character varying(25) COLLATE pg_catalog."default",
    endpoint character varying(255) COLLATE pg_catalog."default",
    mtime bigint,
    mtime_epoch integer,
    tqmin integer,
    tqavg numeric,
    tqmax integer,
    tqcount integer,
    tqsum integer,
    tcmin integer,
    tcavg numeric,
    tcmax integer,
    tccount integer,
    tcsum integer,
    trmin integer,
    travg numeric,
    trmax integer,
    trcount integer,
    trsum bigint,
    ttmin integer,
    ttavg numeric,
    ttmax integer,
    ttcount integer,
    ttsum bigint,
    ttrmin integer,
    ttravg numeric,
    ttrmax integer,
    ttrcount integer,
    ttrsum bigint,
    szmin integer,
    szavg numeric,
    szmax integer,
    szcount integer,
    szsum bigint,
    femin integer,
    feavg numeric,
    femax integer,
    fecount integer,
    fesum bigint,
    bemin integer,
    beavg numeric,
    bemax integer,
    becount integer,
    besum bigint,
    st2count integer,
    st3count integer,
    st4count integer,
    st5count integer,
    stfailpct integer
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.endpoint_stats
    OWNER to postgres;
-- Index: endpoint_stats_idx1

-- DROP INDEX IF EXISTS public.endpoint_stats_idx1;

CREATE INDEX IF NOT EXISTS endpoint_stats_idx1
    ON public.endpoint_stats USING btree
    (database COLLATE pg_catalog."default" ASC NULLS LAST, mtime_epoch ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: endpoint_stats_idx2

-- DROP INDEX IF EXISTS public.endpoint_stats_idx2;

CREATE INDEX IF NOT EXISTS endpoint_stats_idx2
    ON public.endpoint_stats USING btree
    (database COLLATE pg_catalog."default" ASC NULLS LAST, mtime_epoch ASC NULLS LAST, verb COLLATE pg_catalog."default" ASC NULLS LAST, endpoint COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: endpoint_stats_idx3

-- DROP INDEX IF EXISTS public.endpoint_stats_idx3;

CREATE INDEX IF NOT EXISTS endpoint_stats_idx3
    ON public.endpoint_stats USING btree
    (cluster COLLATE pg_catalog."default" ASC NULLS LAST, database COLLATE pg_catalog."default" ASC NULLS LAST, mtime_epoch ASC NULLS LAST, verb COLLATE pg_catalog."default" ASC NULLS LAST, endpoint COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: endpoint_stats_idx4

-- DROP INDEX IF EXISTS public.endpoint_stats_idx4;

CREATE INDEX IF NOT EXISTS endpoint_stats_idx4
    ON public.endpoint_stats USING btree
    (database COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: endpoint_stats_idx5

-- DROP INDEX IF EXISTS public.endpoint_stats_idx5;

CREATE INDEX IF NOT EXISTS endpoint_stats_idx5
    ON public.endpoint_stats USING btree
    (mtime_epoch ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: endpoint_stats_idx6

-- DROP INDEX IF EXISTS public.endpoint_stats_idx6;

CREATE INDEX IF NOT EXISTS endpoint_stats_idx6
    ON public.endpoint_stats USING btree
    (cluster COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: endpoint_stats_idx7

-- DROP INDEX IF EXISTS public.endpoint_stats_idx7;

CREATE INDEX IF NOT EXISTS endpoint_stats_idx7
    ON public.endpoint_stats USING btree
    (endpoint COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;

-- Table: public.host_stats

-- DROP TABLE IF EXISTS public.host_stats;

CREATE TABLE IF NOT EXISTS public.host_stats
(
    index integer,
    cluster character varying(255) COLLATE pg_catalog."default",
    host character varying(255) COLLATE pg_catalog."default",
    mtime bigint,
    mtime_epoch integer,
    doc_writes bigint,
    doc_inserts bigint,
    ioql_max numeric(8,3),
    ioql_med numeric(8,3),
    ioql_pctl_90 numeric(8,3),
    ioql_pctl_99 numeric(8,3),
    ioql_pctl_999 numeric(8,3)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.host_stats
    OWNER to postgres;
-- Index: host_stats_idx1

-- DROP INDEX IF EXISTS public.host_stats_idx1;

CREATE INDEX IF NOT EXISTS host_stats_idx1
    ON public.host_stats USING btree
    (cluster COLLATE pg_catalog."default" ASC NULLS LAST, host COLLATE pg_catalog."default" ASC NULLS LAST, mtime_epoch ASC NULLS LAST)
    TABLESPACE pg_default;

-- Table: public.ioq_stats

-- DROP TABLE IF EXISTS public.ioq_stats;

CREATE TABLE IF NOT EXISTS public.ioq_stats
(
    index integer,
    cluster character varying(255) COLLATE pg_catalog."default",
    host character varying(255) COLLATE pg_catalog."default",
    ioqtype character varying(255) COLLATE pg_catalog."default",
    mtime bigint,
    mtime_epoch integer,
    requests bigint
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.ioq_stats
    OWNER to postgres;
-- Index: ioq_stats_idx1

-- DROP INDEX IF EXISTS public.ioq_stats_idx1;

CREATE INDEX IF NOT EXISTS ioq_stats_idx1
    ON public.ioq_stats USING btree
    (cluster COLLATE pg_catalog."default" ASC NULLS LAST, host COLLATE pg_catalog."default" ASC NULLS LAST, mtime_epoch ASC NULLS LAST)
    TABLESPACE pg_default;

-- Table: public.smoosh_stats

-- DROP TABLE IF EXISTS public.smoosh_stats;

CREATE TABLE IF NOT EXISTS public.smoosh_stats
(
    index integer,
    cluster character varying(255) COLLATE pg_catalog."default",
    host character varying(255) COLLATE pg_catalog."default",
    channel character varying(255) COLLATE pg_catalog."default",
    mtime bigint,
    mtime_epoch integer,
    active integer,
    waiting integer,
    starting integer
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.smoosh_stats
    OWNER to postgres;
-- Index: smoosh_stats_idx1

-- DROP INDEX IF EXISTS public.smoosh_stats_idx1;

CREATE INDEX IF NOT EXISTS smoosh_stats_idx1
    ON public.smoosh_stats USING btree
    (cluster COLLATE pg_catalog."default" ASC NULLS LAST, host COLLATE pg_catalog."default" ASC NULLS LAST, mtime_epoch ASC NULLS LAST)
    TABLESPACE pg_default;

-- Table: public.verb_stats

-- DROP TABLE IF EXISTS public.verb_stats;

CREATE TABLE IF NOT EXISTS public.verb_stats
(
    index integer,
    cluster character varying(255) COLLATE pg_catalog."default",
    loghost character varying(255) COLLATE pg_catalog."default",
    database character varying(255) COLLATE pg_catalog."default",
    verb character varying(25) COLLATE pg_catalog."default",
    mtime bigint,
    mtime_epoch integer,
    tqmin integer,
    tqavg numeric,
    tqmax integer,
    tqcount integer,
    tqsum integer,
    tcmin integer,
    tcavg numeric,
    tcmax integer,
    tccount integer,
    tcsum integer,
    trmin integer,
    travg numeric,
    trmax integer,
    trcount integer,
    trsum bigint,
    ttmin integer,
    ttavg numeric,
    ttmax integer,
    ttcount integer,
    ttsum bigint,
    ttrmin integer,
    ttravg numeric,
    ttrmax integer,
    ttrcount integer,
    ttrsum bigint,
    szmin integer,
    szavg numeric,
    szmax integer,
    szcount integer,
    szsum bigint,
    femin integer,
    feavg numeric,
    femax integer,
    fecount integer,
    fesum bigint,
    bemin integer,
    beavg numeric,
    bemax integer,
    becount integer,
    besum bigint,
    st2count integer,
    st3count integer,
    st4count integer,
    st5count integer,
    stfailpct integer
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.verb_stats
    OWNER to postgres;
-- Index: verb_stats_idx1

-- DROP INDEX IF EXISTS public.verb_stats_idx1;

CREATE INDEX IF NOT EXISTS verb_stats_idx1
    ON public.verb_stats USING btree
    (database COLLATE pg_catalog."default" ASC NULLS LAST, mtime_epoch ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: verb_stats_idx2

-- DROP INDEX IF EXISTS public.verb_stats_idx2;

CREATE INDEX IF NOT EXISTS verb_stats_idx2
    ON public.verb_stats USING btree
    (database COLLATE pg_catalog."default" ASC NULLS LAST, mtime_epoch ASC NULLS LAST, verb COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: verb_stats_idx3

-- DROP INDEX IF EXISTS public.verb_stats_idx3;

CREATE INDEX IF NOT EXISTS verb_stats_idx3
    ON public.verb_stats USING btree
    (database COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: verb_stats_idx4

-- DROP INDEX IF EXISTS public.verb_stats_idx4;

CREATE INDEX IF NOT EXISTS verb_stats_idx4
    ON public.verb_stats USING btree
    (mtime_epoch ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: verb_stats_idx5

-- DROP INDEX IF EXISTS public.verb_stats_idx5;

CREATE INDEX IF NOT EXISTS verb_stats_idx5
    ON public.verb_stats USING btree
    (cluster COLLATE pg_catalog."default" ASC NULLS LAST, database COLLATE pg_catalog."default" ASC NULLS LAST, mtime_epoch ASC NULLS LAST, verb COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: verb_stats_idx6

-- DROP INDEX IF EXISTS public.verb_stats_idx6;

CREATE INDEX IF NOT EXISTS verb_stats_idx6
    ON public.verb_stats USING btree
    (cluster COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;

-- Table: public.view_stats

-- DROP TABLE IF EXISTS public.view_stats;

CREATE TABLE IF NOT EXISTS public.view_stats
(
    index integer,
    cluster character varying(255) COLLATE pg_catalog."default",
    database character varying(255) COLLATE pg_catalog."default",
    viewdoc character varying(255) COLLATE pg_catalog."default",
    view character varying(255) COLLATE pg_catalog."default",
    signature character varying(35) COLLATE pg_catalog."default",
    mtime bigint,
    mtime_epoch integer,
    disk_size bigint,
    data_size bigint,
    active_size bigint,
    updates_pending_total integer,
    updates_pending_minimum integer,
    updates_pending_preferred integer,
    shard_count integer
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.view_stats
    OWNER to postgres;
-- Index: view_stats_idx1

-- DROP INDEX IF EXISTS public.view_stats_idx1;

CREATE INDEX IF NOT EXISTS view_stats_idx1
    ON public.view_stats USING btree
    (cluster COLLATE pg_catalog."default" ASC NULLS LAST, database COLLATE pg_catalog."default" ASC NULLS LAST, mtime_epoch ASC NULLS LAST)
    TABLESPACE pg_default;