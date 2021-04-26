SELECT
    nc.rowid,
    nc.textcontent,
    nd.source
FROM
    newscontent nc,
    newsdata nd,
    (SELECT
        nc.rowid
        , nd.published_utc
    FROM
        newscontent nc
        , newsdata nd
    WHERE
        nc.rowid = nd.rowid
        AND nc.textcontent match '"covid"
                                  OR "covid19"
                                  OR "covid-19"
                                  OR "coronavirus"
                                  OR "corona virus"
                                  OR "2019-ncov"
                                  OR "hcov-19"
                                  OR "sars-cov-2"
                                  OR "chinese virus"
                                  OR "chinese coronavirus"
                                  OR "wuhan virus"
                                  OR "chinese flu"
                                  OR "wuhan flu"
                                  OR "kung flu"
                                  OR "british virus"
                                  OR "chinese communist party virus"
                                  '
    UNION
    SELECT
        nc.rowid
        , nd.published_utc
    FROM
        newscontent nc
        , newsdata nd
    WHERE
        nc.rowid = nd.rowid
        AND nc.title match '"covid"
                            OR "covid19"
                            OR "covid-19"
                            OR "coronavirus"
                            OR "corona virus"
                            OR "2019-ncov"
                            OR "hcov-19"
                            OR "sars-cov-2"
                            OR "chinese virus"
                            OR "chinese coronavirus"
                            OR "wuhan virus"
                            OR "chinese flu"
                            OR "wuhan flu"
                            OR "kung flu"
                            OR "british virus"
                            OR "chinese communist party virus"
                            ') as r
WHERE
    nc.rowid = r.rowid
    AND nc.rowid = nd.rowid
    AND datetime(r.published_utc, 'unixepoch') >= '2020-01-01'
    AND datetime(r.published_utc, 'unixepoch') < '2021-02-01'
--    ORDER BY RANDOM()
--    LIMIT 10000
    ;
