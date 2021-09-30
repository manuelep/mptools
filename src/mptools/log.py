# -*- coding: utf-8 -*-

import datetime
from .timeformat import prettydate

class timeLoggerDecorator(object):
    """ Helper decorator for inspetting time spent for generic function execution.

    Usage example:

    @timeLoggerDecorator()
    def your_function(*a, **kw):
        ''' Does something and returns stuff '''
        # ... do something and return stuff
        return stuff

    """

    def __init__(self, custom_logger, name='N.P.'):
        super(timeLoggerDecorator, self).__init__()
        self.name = name
        self.logger = custom_logger

    def __call__(self, func):
        def wrapper(*a, **kw):
            t0 = datetime.datetime.now()
            result = func(*a, **kw)
            delta = prettydate(t0, use_suffix=False)

            _msg = """
  Method: {method}
  Help: {help}
  Elapsed time: {time}
            """
            msg = _msg.format(
                method = func.__name__,
                time = delta,
                help = func.__doc__
            )

            logging.warning(msg)

            return result
        return wrapper

    def __exit__(self, exc_type, exc_value, traceback):
        """ """
        delta = prettydate(self.start, use_suffix=False)

        msg = """
  Action: {name}
  Elapsed time: {time}
        """.format(
            name = self.name,
            time = delta,
            # help = func.__doc__
        )
        print(msg)
        self.logger.debug(msg)

    def __enter__(self):
        """ """
        self.start = datetime.datetime.now()
        return self
