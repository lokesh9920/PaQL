DROP TABLE IF EXISTS tpch cascade;

CREATE TABLE tpch
(
    id                integer,
    sum_base_price    real,
    sum_disc_price    real,
    sum_charge        real,
    avg_qty           real,
    avg_price         real,
    avg_disc          numeric(30),
    sum_qty           integer,
    count_order       integer,
    p_size            integer,
    ps_min_supplycost real,
    revenue           real,
    o_totalprice      real,
    o_shippriority    integer,
    primary key (id)
);

\COPY tpch (id, sum_base_price, sum_disc_price, sum_charge, avg_qty, avg_price, avg_disc, sum_qty, count_order, p_size, ps_min_supplycost, revenue, o_totalprice, o_shippriority) FROM '../data/sample_tpch.csv' WITH (FORMAT CSV, HEADER true);