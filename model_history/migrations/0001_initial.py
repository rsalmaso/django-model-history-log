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

import django.core.serializers.json
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models

import model_history.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="History",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "created_at",
                    model_history.fields.CreationDateTimeField(
                        blank=True, default=django.utils.timezone.now, editable=False, verbose_name="created"
                    ),
                ),
                (
                    "last_modified_at",
                    model_history.fields.ModificationDateTimeField(
                        blank=True, default=django.utils.timezone.now, editable=False, verbose_name="modified"
                    ),
                ),
                ("app_label", models.CharField(max_length=100)),
                ("model", models.CharField(max_length=100)),
                ("source_id", models.PositiveIntegerField(verbose_name="source id")),
                (
                    "source_type",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="contenttypes.contenttype",
                        verbose_name="source content type",
                    ),
                ),
            ],
            options={
                "verbose_name": "History",
                "verbose_name_plural": "Histories",
                "unique_together": {("app_label", "model", "source_id")},
            },
        ),
        migrations.CreateModel(
            name="HistoryLog",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "created_at",
                    model_history.fields.CreationDateTimeField(
                        blank=True, default=django.utils.timezone.now, editable=False, verbose_name="created"
                    ),
                ),
                (
                    "last_modified_at",
                    model_history.fields.ModificationDateTimeField(
                        blank=True, default=django.utils.timezone.now, editable=False, verbose_name="modified"
                    ),
                ),
                (
                    "fields",
                    model_history.fields.JSONField(
                        default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder, verbose_name="fields"
                    ),
                ),
                (
                    "updated",
                    model_history.fields.JSONField(
                        default=dict,
                        encoder=django.core.serializers.json.DjangoJSONEncoder,
                        verbose_name="updated fields",
                    ),
                ),
                (
                    "history",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="logs",
                        to="model_history.history",
                        verbose_name="history",
                    ),
                ),
            ],
            options={
                "verbose_name": "log",
                "verbose_name_plural": "logs",
                "ordering": ["created_at"],
            },
        ),
    ]
