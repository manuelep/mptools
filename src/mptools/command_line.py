# -*- coding: utf-8 -*-

from .dbutils.wiz import Wiz as ConnCollector
import argparse
import os
import sys
import importlib
import getpass

def hello():
    print("Hello world!")


def dbgenie_(DB_FOLDER, DB_URI, *extensions):
    dbcollector = ConnCollector(
        path = DB_FOLDER,
        cache = None
    )
    dbcollector.collect(DB_URI, *extensions)
    dbcollector.setup()


def dbgenie():

    parser = argparse.ArgumentParser(
        description = """This helper command takes care of creating PostgreSQL
database for your py4web/web2py appliation with all required extensions,
if they are available in the PostgreSQL environment.
WARNING: It will prompt for PostgreSQL power user credentials, that you must know.
""",
        formatter_class = argparse.RawTextHelpFormatter
    )

    # parser.add_argument("settings",
    #     help = 'Path for application settings file containing at least DB_FOLDER and DB_URI variables',
    #     required = True
    # )

    parser.add_argument("DB_FOLDER",
        help = "DB_FOLDER. Path to 'databases' folder of your py4web/web2py application will be fine.",
    )
    parser.add_argument("DB_URI",
        help = '''DB_URI. Try something like: 'postgres://yourUsername:{password}@localhost/yourDatabaseName'
NOTE: For security reason the string '{password}' can be provided instead
of the real password of the specified user, in this case the script will
prompt for the real user password to use.
NOTE: The given user will be created if does not exists. If the database
already exist it will be dropped and recreated and all preveleges will be
granted to the previous user, but first it will be prompted for your
agreement confirtmation.''',
    )

    parser.add_argument("-e", "--extensions", nargs="*", default=[],
        help = "Database extensions to load. Required extensions must be available."
    )

    args = parser.parse_args()

    # Courtesy of: https://stackoverflow.com/a/55892361/1039510
    # pathname, filename = os.path.split(args.settings)
    # sys.path.append(os.path.abspath(pathname))
    # modname = os.path.splitext(filename)[0]
    # settings = importlib.import_module(modname)

    if '{password}' in args.DB_URI:
        DB_URI = args.DB_URI.format(password=getpass.getpass("Provide password for specified dbatabase user: "))
    else:
        DB_URI = args.DB_URI

    dbgenie_(args.DB_FOLDER, DB_URI, *args.extensions)
