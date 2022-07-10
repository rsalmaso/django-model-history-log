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

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

__all__ = (
    'CreationDateTimeField', 'ModificationDateTimeField', 'TimestampModel',
    'DjangoJSONEncoder',
)


try:
    from fluo.db.models import CreationDateTimeField, ModificationDateTimeField, TimestampModel
except ImportError:
    class CreationDateTimeField(models.DateTimeField):
        def __init__(self, *args, **kwargs):
            kwargs.setdefault('editable', False)
            kwargs.setdefault('blank', True)
            kwargs.setdefault('default', timezone.now)
            super().__init__(*args, **kwargs)

        def get_internal_type(self):
            return "DateTimeField"

    class ModificationDateTimeField(CreationDateTimeField):
        def pre_save(self, model, add):
            value = timezone.now()
            setattr(model, self.attname, value)
            return value

        def get_internal_type(self):
            return "DateTimeField"

    class TimestampModel(models.Model):
        created_at = CreationDateTimeField(
            verbose_name=_('created'),
        )
        last_modified_at = ModificationDateTimeField(
            verbose_name=_('modified'),
        )

        class Meta:
            abstract = True


try:
    from fluo.utils.json import JSONEncoder as DjangoJSONEncoder
except ImportError:
    from django.core.serializers.json import DjangoJSONEncoder
