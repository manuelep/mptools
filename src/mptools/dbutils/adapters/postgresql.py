# -*- coding: utf-8 -*-

import psycopg2, logging
logger = logging.getLogger(__name__)

# .-"-.tools.-"-.     .-"-.     .-"-.     .-"-.     .-"-.     .-"-.     .-"-.
# start"-.-"     "-.-"     "-.-"     "-.-"     "-.-"     "-.-"     "-.-"     "-.

def _curs_exec_(curs, _sql, **kw):
    sql = _sql if not kw else _sql.format(**kw)
    logger.debug("Running sql command:")
    logger.debug(sql)
    curs.execute(sql)

# .-"-.tools.-"-.     .-"-.     .-"-.     .-"-.     .-"-.     .-"-.     .-"-.
#  end "-.-"     "-.-"     "-.-"     "-.-"     "-.-"     "-.-"     "-.-"     "-.

def pgsetup(hostname, port, puser, ppass, uris, extensions, **__):
    """
    hostname @string :
    port     @string :
    puser    @string :
    ppass    @string :
    uris   @iterable : A set of complete connection strings for the connection;
    extensions @dict : {'<uri>': ['<ext>', ...]}
    """

    with psycopg2.connect(
        dbname = "postgres",
        user = puser,
        password = ppass,
        host = hostname,
        port= port
    ) as conn:
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as curs:
            for uri, username in uris:
                # uri = urinfo["uri"]
                dbname = uri.split("/")[-1]

                assert input("Database {dbname} will be DROPPED and re-created. Continue?: (NO/yes)".format(**vars())) in ('yes', 'Y', 'Yes', 'y',)

                _curs_exec_(curs, """SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = '{dbname}'
AND pid <> pg_backend_pid();""", dbname=dbname)
                _curs_exec_(curs, "DROP DATABASE IF EXISTS {dbname};", dbname=dbname)
                _curs_exec_(curs, "CREATE DATABASE {dbname} WITH OWNER {user};",
                    dbname = dbname,
                    user = username
                )
                _curs_exec_(curs, "GRANT ALL PRIVILEGES ON DATABASE {dbname} to {user};",
                    dbname = dbname,
                    user = username
                )

    for uri, username in uris:
        with psycopg2.connect(
            dbname = uri.split("/")[-1],
            user = puser,
            password = ppass,
            host = hostname,
            port= port
        ) as conn:
            with conn.cursor() as curs:
                if uri in extensions:
                    for ext in extensions[uri]:
                        _curs_exec_(curs, "CREATE EXTENSION {};".format(ext))


def pgteardown(hostname, port, puser, ppass, uris, **__):
    """ """

    with psycopg2.connect(
        dbname = "postgres",
        user = puser,
        password = ppass,
        host = hostname,
        port = port
    ) as conn:
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as curs:
            for uri, _ in uris:
                dbname = uri.split("/")[-1]

                assert input("Database {dbname} will be DROPPED. Continue?: (NO/yes) ".format(**vars())) in ('yes', 'Y', 'Yes', 'y',)

                _curs_exec_(curs, """SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = '{dbname}'
  AND pid <> pg_backend_pid();""", dbname=dbname)
                _curs_exec_(curs, "DROP DATABASE IF EXISTS {dbname};", dbname=dbname)

        conn.commit()
