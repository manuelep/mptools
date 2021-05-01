# -*- coding: utf-8 -*-

from urllib.parse import urlparse
import getpass
from .adapters.postgresql import pgsetup, pgteardown
from .adapters.sqlite import liteteardown
import re, os

from diskcache import Cache

def nothingtodo(*a, **k):
    """ """

def replace(string, *removals, **_substitutions):
    """ Courtesy of: https://gist.github.com/carlsmith/b2e6ba538ca6f58689b4c18f46fef11c
    """
    substitutions = dict({k: "" for k in removals}, **_substitutions)
    substrings = sorted(substitutions, key=len, reverse=True)
    regex = re.compile('|'.join(map(re.escape, substrings)))
    return regex.sub(lambda match: substitutions[match.group(0)], string)

drivers_available = "psycopg2", "pymysql", "imaplib", "sqlite3", "pg8000", "pyodbc",

clean_uri = lambda uri: replace(uri, *map(lambda drv: drv+":", drivers_available))

adapters = {
    'postgres': {'setup': pgsetup, 'teardown': pgteardown},
    'sqlite': {'setup': nothingtodo, 'teardown': liteteardown},
}

class Wiz(object):
    """docstring for ConnCollectort."""

    def __init__(self, path, cache=None, time_expire=86400):
        """
        path @string : Path to databases folder;
        """
        super(Wiz, self).__init__()
        self.path = path
        self.connections = {}
        self.cache = cache
        self.time_expire = time_expire

    def __puser(self, key, msg):
        main = lambda: input(msg)
        if self.cache is None:
            return main()
        elif isinstance(self.cache, str):
            cache = Cache(self.cache, disk_pickle_protocol=3)
            return cache.memoize(expire=self.time_expire, tag=key)(main)()
        else:
            return self.cache.disk(key, main, time_expire=self.time_expire)

    def __ppass(self, key, msg):
        main = lambda: getpass.getpass(msg)
        if self.cache is None:
            return main()
        elif isinstance(self.cache, str):
            cache = Cache(self.cache, disk_pickle_protocol=3)
            return cache.memoize(expire=self.time_expire, tag=key)(main)()
        else:
            return self.cache.disk(key, main, time_expire=self.time_expire)

    def collect(self, _uri, *extensions):
        """ """
        battrs = ('scheme', 'hostname', 'port',)
        uri = clean_uri(_uri)
        cinfo = urlparse(_uri)
        # infos = {k: getattr(uri, k) for k in battrs}
        shp = tuple(getattr(cinfo, k) for k in battrs)

        try:
            self.connections[shp]
        except KeyError:
            cidt = "{}@{}".format(cinfo.scheme, cinfo.hostname)

            _key = lambda k: '-'.join(list(map(lambda x: '' if not x else str(object=x), shp))+[k])

            self.connections[shp] = {
                'puser': self.__puser(_key('puser'), cidt+" power user: "), # raw_input(cidt+" power user: "),
                'ppass': self.__ppass(_key('ppass'), cidt+" power user password: "), # getpass.getpass(cidt+" power user password: "),
                'uris': {(uri, cinfo.username)},
                'extensions': {uri: set(extensions)}
            }
        else:
            self.connections[shp]['uris'].add((uri, cinfo.username))
            if uri in self.connections[shp]['extensions']:
                self.connections[shp]['extensions'][uri].update(extensions)

    def __run(self, _method='setup'):
        """ """
        for shp, info in self.connections.items():
            scheme, hostname, port = shp
            method = adapters[scheme][_method]
            method(hostname=hostname, port=port, path=self.path, **info)

    def setup(self):
        self.__run()

    def __enter__(self):
        self.__run()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.__run('teardown')

    def destroy(self):
        self.__run('teardown')
