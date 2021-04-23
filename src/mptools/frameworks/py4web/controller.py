# -*- coding: utf-8 -*-

from py4web.core import Fixture, HTTP
from py4web import request, response
from inspect import signature, _empty
import json
import pandas as pd
from io import BytesIO


def unjson(value):
    try:
        return json.loads(value)
    except (json.decoder.JSONDecodeError, TypeError,):
        return value

def check_key_in_params(key):
    try:
        return (key in request.params)
    except KeyError:
        return False

def webio(func, **defaults):
    kwargs = {}
    sign = signature(func).parameters
    for key,parameter in sign.items():
        if parameter.default==_empty:
            if key in request.query:
                kwargs[key] = unjson(request.query[key])
            elif request.json and (key in request.json):
                kwargs[key] = request.json[key]
            elif check_key_in_params(key):
                kwargs[key] = unjson(request.params[key])
            elif key in defaults:
                kwargs[key] = defaults[key]

        elif key in request.query:
            kwargs[key] = unjson(request.query[key])
        elif request.json and (key in request.json):
            kwargs[key] = request.json[key]
        elif check_key_in_params(key):
            kwargs[key] = unjson(request.params[key])
        elif key in defaults:
            kwargs[key] = defaults[key]
        else:
            kwargs[key] =  parameter.default

    if not request.query is None:
        kwargs.update({k: unjson(v) for k,v in request.query.items() if not k in sign})
    elif not request.json is None:
        kwargs.update({k: v for k,v in request.json.items() if not k in sign})
    kwargs.update({k: v for k,v in defaults.items() if not k in sign})

    return kwargs

class WebWrapper(Fixture):
    """docstring for WebWrapper."""

    def __init__(self, **defaults):
        super(WebWrapper, self).__init__()
        self.defaults = defaults
        self.update = self.defaults.update
        self.__setitem__ = self.defaults.__setitem__

    def parse_request(self, func, **defaults):
        self.update(defaults)
        return webio(func, **self.defaults)

    def __call__(self, func, **defaults):
        self.update(defaults)
        def wrapper():
            return func(**webio(func, **self.defaults))
        return wrapper


def brap(**defaults):
    """ web wrapper
    Variables declared in function signature will be taken from request and
    decoded as they were json string before being passed to the function.

    defaults : Default values that will overwrite the ones defined in signature.
    """
    def decorator(func):
        def wrapper():
            kwargs = {}
            sign = signature(func).parameters
            for key,parameter in sign.items():
                if parameter.default==_empty:
                    if key in request.query:
                        kwargs[key] = unjson(request.query[key])
                    elif request.json and (key in request.json):
                        kwargs[key] = request.json[key]
                    elif key in defaults:
                        kwargs[key] = defaults[key]

                elif key in request.query:
                    kwargs[key] = unjson(request.query[key])
                elif request.json and (key in request.json):
                    kwargs[key] = request.json[key]
                elif key in defaults:
                    kwargs[key] = defaults[key]
                else:
                    kwargs[key] =  parameter.default

            if not request.query is None:
                kwargs.update({k: unjson(v) for k,v in request.query.items() if not k in sign})
            elif not request.json is None:
                kwargs.update({k: v for k,v in request.json.items() if not k in sign})
            kwargs.update({k: v for k,v in defaults.items() if not k in sign})

            return func(**kwargs)
        return wrapper
    return decorator

class LocalsOnly(Fixture):
    """docstring for LocalsOnly."""

    def __init__(self):
        super(LocalsOnly, self).__init__()
        # self.request = request

    def on_request(self):
        if not request.urlparts.netloc.startswith('localhost'):
            raise HTTP(403)


class CORS(Fixture):
    """ Fixture helper for sharing web service avoiding cross origin resource sharing problems """

    def __init__(self, age=86400, origin="*", headers="*", methods="*"):
        super(CORS, self).__init__()
        self.age = age
        self.origin = origin
        self.headers = headers
        self.methods = methods

    def on_request(self):
        response.headers["Access-Control-Allow-Origin"] = self.origin
        response.headers["Access-Control-Max-Age"] = self.age
        response.headers["Access-Control-Allow-Headers"] = self.headers
        response.headers["Access-Control-Allow-Methods"] = self.methods
        response.headers["Access-Control-Allow-Credentials"] = "true"

class AsXlsx(Fixture):
    """ Export the output to excel format """

    def __init__(self, filename='export', columns=None, index=False):
        """
        filename @string : Name of the downloading file
        columns @list : Sorted list of the column names to export
        """
        self.filename = filename
        self.columns = columns
        self.index = index

    def on_success(self, status):
        # called when a request is successful
        if status==200:
            response.headers["Content-Type"] = "application/vnd.ms-excel"
            response.headers["Content-Disposition"] = f'inline; filename="{self.filename}.xlsx"'

    def transform(self, output, shared_data=None):
        """
        output @dict : The decorated controller must returns a dictionary with
            the data to export divided by worksheet.
        Doc:
            Courtesy of:
                * https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.ExcelWriter.html
                * https://xlsxwriter.readthedocs.io/example_pandas_multiple.html
        """
        stream = BytesIO()
        with pd.ExcelWriter(stream, engine='xlsxwriter') as writer:
            for sensor, data in output.items():
                df = pd.DataFrame(data)
                df.to_excel(writer, sheet_name=sensor, columns=self.columns, index=self.index)

        stream.seek(0)
        return stream.read()
