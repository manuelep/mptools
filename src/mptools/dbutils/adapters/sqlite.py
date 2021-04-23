# -*- coding: utf-8 -*-

import os
import logging

logger = logging.getLogger(__name__)

def liteteardown(path, uris, **__):
    for uri, _ in uris:
        dbname = uri.split("/")[-1]
        fp = os.path.join(path, dbname)
        for filepath in (fp, fp+'-journal',):
            try:
                os.remove(filepath)
            except OSError:
                logger.warning("Trouble removing: {}".format(filepath))
            else:
                logger.debug("File '{0}' removed".format(filepath))
