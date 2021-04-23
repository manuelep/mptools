# -*- coding: utf-8 -*-

import os, json
import logging

logger = logging.getLogger(__name__)

YES = ['yes', 'true', 't', 'y', '1']
NO = ['no', 'false', 'f', 'n', '0', '']

def guess(text, default=None, **helpers):

    # 1-st guess
    if text is None:
        return False
    elif not isinstance(text, str):
        return not not text

    # 2-nd guess: interpret as json
    try:
        value = json.loads(text)
    except ValueError:
        value = text
    else:
        if isinstance(value, bool):
            return value
        elif value is None:
            return False

    # 3-rd guess
    yes = set(YES)
    no = set(NO)

    for k,v in helpers.items():
        if not v:
            no.add(k.lower())
        else:
            yes.add(k.lower())

    if value.lower() in yes:
        return True
    elif value.lower() in no:
        return False
    elif not default is None:
        return not not default
    else:
        raise ValueError("Sorry! I'm not so good in guessing.")

def smartbytes(num):
    """ Courtesy of: https://stackoverflow.com/a/39988702/1039510
    this function will convert bytes to MiB.... GiB... etc
    """
    for x in ['bytes', 'KiB', 'MiB', 'GiB', 'TiB']:
        if num < 1024.0:
            return f"{num:3.1f} {x}"
        num /= 1024.0


class fileOmeter(object):
    """ """

    def __init__(self, path):
        super(fileOmeter, self).__init__()
        self.path = path
        self.partials = {}
        self.tot = 0

    @classmethod
    def new(cls, path, **kw):
        with cls(path) as cnt:
            for ff, path in cnt:
                cnt.count(ff, path, **kw)

    def __iter__(self):
        """ """
        for path, dirs, files in os.walk(self.path):
            for ff in files:
                yield ff, path

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ """
        for path, dim in sorted(self.partials.items(), key=lambda c: c[1]):
            logger.info("{} - {}".format(path, smartbytes(dim)))
        logger.info("Total length: {}".format(smartbytes(self.tot)))

    def count(self, name, path=None, flt=lambda f, p: True):
        file_path = os.path.join(path, name)
        if os.path.isfile(file_path):
            if flt(name, path):
                file_info = os.stat(file_path)
                file_size = file_info.st_size
                self.tot += file_size

                logger.info("{} - {}".format(name, smartbytes(file_size)))

                if not path is None:
                    try:
                        self.partials[path]
                    except KeyError as err:
                        self.partials[path] = file_size
                    else:
                        self.partials[path] += file_size
