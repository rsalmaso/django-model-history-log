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

from __future__ import annotations

import json

from django import forms
from django.contrib import admin
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import History, HistoryLog


class HistoryLogForm(forms.ModelForm):
    class Meta:
        exclude = ["created_at", "last_modified_at", "fields", "updated"]


class HistoryLogInline(admin.TabularInline):
    extra = 0
    form = HistoryLogForm
    model = HistoryLog
    ordering = ["-created_at"]
    readonly_fields = ["label", "_fields", "_updated"]

    def _pretty(self, data):
        pretty_data = json.dumps(data, sort_keys=True, indent=2, cls=DjangoJSONEncoder)
        return mark_safe(f"""<pre style="white-space: pre-wrap;">{pretty_data}</pre>""")

    @admin.display(description=_("fields"))
    def _fields(self, obj):
        return self._pretty(obj.fields)

    @admin.display(description=_("updated fields"))
    def _updated(self, obj):
        return self._pretty(obj.updated)


class HistoryForm(forms.ModelForm):
    class Meta:
        exclude = ["source_type"]


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    form = HistoryForm
    inlines = [HistoryLogInline]
    list_filter = ["app_label", "model"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "label", "last_modified_at", "app_label", "model", "source_id"]
    search_fields = ["source_type", "source_id"]
