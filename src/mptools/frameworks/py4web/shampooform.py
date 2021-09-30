# -*- coding: utf-8 -*-

from pydal.validators import Validator
from collections import OrderedDict

def field2dict(field):
    """
    field : A pydal Field instanced object.
    """
    fieldkeys = ['required', 'comment', 'default', 'label', 'length', 'fieldname',
        'notnull', 'type', 'options']

    filter_fields = lambda kw: {k: kw[k] for k in fieldkeys if k in kw and not kw[k] is None}
    out = field.as_dict()
    requires = out.pop('requires')

    if isinstance(requires, Validator):
        if callable(getattr(requires, 'options', None)):
            out['options'] = requires.options()
    elif isinstance(requires, list):
        # TODO: Consider that 'requires' parameter cam be a list of Validators
        for validator in requires:
            if hasattr(validator, 'options'):
                out['options'] = validator.options()

    return field.name, filter_fields(out)

def form2dict(form):
    out = dict(
        form_name = form.form_name,
        errors = form.errors,
        accepted = form.accepted,
        formkey = form.formkey
    )
    if not form.accepted and not form.errors:
        out['form_fields'] = OrderedDict(map(
            field2dict,
            filter(lambda f: f.type!='id', form.table)
        ))

    return out

# class ShampooForm(object):
#     """ It's not SOAP... it's Shampoo
#     A web2py SQLFORM helper wrapper freely inspired to the SOAP messaging protocol.
#     Just like SOAP it tries to provide support for exchanging structured information
#     in the implementation of web services but it uses JSON like structures for
#     its message format.
#     """
#
#     def __init__(self, table, **attributes):
#         """
#         table : a DAL table or a list of fields
#         """
#         super(ShampooForm, self).__init__()
#         self.form = Form(table, **attributes)
#         if self.form.accepted:
#             self.attributes = {
#                 'formname': self.form.formname,
#                 'formerrors': self.form.errors,
#                 'formvalidate': True,
#             }
#
#
#     __getattr__ = lambda self, name: getattr(self.form, name)
