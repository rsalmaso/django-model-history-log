# Copyright (C) 2017-2022, Raffaele Salmaso <raffaele@salmaso.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import json

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import smart_text

from .compat import DjangoJSONEncoder


class JSONField(models.TextField):
    """
    Field that stores python structures as JSON strings on database.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('default', {})
        self.encoder = kwargs.pop('encoder', DjangoJSONEncoder)
        self.options = kwargs.pop('options', None)
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection, context):
        return self.to_python(value)

    def to_python(self, value):
        """
        Convert the input JSON value into python structures, raises
        django.core.exceptions.ValidationError if the data can't be converted.
        """
        if self.blank and not value:
            return {}
        value = value or '{}'
        if isinstance(value, bytes):
            value = str(value, 'utf-8')
        if isinstance(value, str):
            try:
                return json.loads(value)
            except Exception as err:
                raise ValidationError(str(err))
        else:
            return value

    def validate(self, value, model_instance):
        """
        Check value is a valid JSON string, raise ValidationError on error.
        """
        if isinstance(value, str):
            super().validate(value, model_instance)
            try:
                json.loads(value)
            except Exception as err:
                raise ValidationError(str(err))

    def get_prep_value(self, value):
        """Convert value to JSON string before save"""
        try:
            options = {'cls': self.encoder} if self.encoder else {}
            if self.options:
                options.update(self.options)
            return json.dumps(value, **options)
        except Exception as err:
            raise ValidationError(str(err))

    def value_to_string(self, obj):
        """Return value from object converted to string properly"""
        return smart_text(self.get_prep_value(self._get_val_from_obj(obj)))

    def value_from_object(self, obj):
        """Return value dumped to string."""
        return self.get_prep_value(self._get_val_from_obj(obj))
