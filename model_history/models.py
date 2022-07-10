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

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models, transaction
from django.db.models.signals import m2m_changed, post_save, pre_delete
from django.utils.translation import gettext, gettext_lazy as _
from rest_framework import serializers

from . import fields as _fields
from .exceptions import HistoryAlreadyRegisteredException


class Callback:
    def __init__(self, exclude=None):
        self.exclude = exclude

    def __call__(self, instance, **kwargs):
        History.objects.log(instance, exclude=self.exclude)


class TimestampModel(models.Model):
    created_at = _fields.CreationDateTimeField(
        verbose_name=_("created"),
    )
    last_modified_at = _fields.ModificationDateTimeField(
        verbose_name=_("modified"),
    )

    class Meta:
        abstract = True


class HistoryQuerySet(models.QuerySet):
    pass


class HistoryManager(models.Manager.from_queryset(HistoryQuerySet)):
    def log(self, instance, exclude=None, serializer_class=None):
        source_type = ContentType.objects.get_for_model(instance)
        source_id = instance.pk
        try:
            history = History.objects.get(source_type=source_type, source_id=source_id)
        except History.DoesNotExist:
            history = History(source_type=source_type, source_id=source_id)
        history.save(exclude=exclude, serializer_class=serializer_class)
        return history


class History(TimestampModel):
    AlreadyRegistered = HistoryAlreadyRegisteredException

    app_label = models.CharField(
        max_length=100,
    )
    model = models.CharField(
        max_length=100,
    )
    source_type = models.ForeignKey(
        ContentType,
        db_index=True,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("source content type"),
    )
    source_id = models.PositiveIntegerField(
        verbose_name=_("source id"),
    )
    source = GenericForeignKey(
        "source_type",
        "source_id",
    )

    objects = HistoryManager()

    class Meta:
        unique_together = ["app_label", "model", "source_id"]
        verbose_name = _("History")
        verbose_name_plural = _("Histories")

    def __str__(self):
        fmt = "{source} [{app_label}.{model} {id}]" if self.source else "{app_label}.{model} {id}"
        return fmt.format(source=self.source, app_label=self.app_label, model=self.model, id=self.source_id)

    @transaction.atomic
    def save(self, fields=None, exclude=None, serializer_class=None, *args, **kwargs):
        """
        History acts as a singleton, cannot be updated other than last_modified_at field
        """
        save_first_time = not self.id
        serializer_class = self.get_serializer_class(fields, exclude) if serializer_class is None else serializer_class

        current_fields = serializer_class(self.source).data

        if save_first_time:
            # save app_label and model
            self.app_label = self.source_type.app_label
            self.model = self.source_type.model
            super().save(*args, **kwargs)

        try:
            prev_fields = self.logs.order_by("created_at").last().fields
        except AttributeError:
            save_first_time, updated_fields = True, {}
        else:
            updated_fields = self.get_updated_fields(prev_fields, current_fields)

        if save_first_time or updated_fields:
            super().save(update_fields=["last_modified_at"])
            log = HistoryLog(
                history=self,
                fields=current_fields,
                updated=updated_fields,
            )
            log.save(*args, **kwargs)

    def get_serializer_class(self, fields_opt=None, exclude_opt=None):
        if not fields_opt and not exclude_opt:
            fields_opt = "__all__"
        model_class = self.source_type.model_class()

        class ModelSerializer(serializers.ModelSerializer):
            class Meta:
                fields = fields_opt
                exclude = exclude_opt
                model = model_class

        return ModelSerializer

    def get_updated_fields(self, old_fields, new_fields):
        """
        get old values for update fields
        """
        updated_fields = {}
        for key, value in old_fields.items():
            if key in new_fields:
                if value != new_fields[key]:
                    updated_fields[key] = value
            else:
                updated_fields[key] = value
        return updated_fields

    _registry = {}

    @classmethod
    def register(cls, sender, *, exclude=None):
        if (callback := cls._registry.get(sender)) is not None:
            raise History.AlreadyRegistered(
                f"Model {sender._meta.app_label}.{sender._meta.model_name} was already registered."
            )

        callback = Callback(exclude=exclude)
        cls._registry[sender] = callback
        post_save.connect(callback, sender=sender)
        pre_delete.connect(callback, sender=sender)
        m2m_changed.connect(callback, sender=sender)

    @classmethod
    def unregister(cls, sender):
        callback = cls._registry.pop(sender, None)
        if callback is None:
            return
        post_save.disconnect(receiver=callback, sender=sender)
        pre_delete.disconnect(receiver=callback, sender=sender)
        m2m_changed.disconnect(receiver=callback, sender=sender)


class HistoryLogQuerySet(models.QuerySet):
    pass


class HistoryLogManager(models.Manager.from_queryset(HistoryQuerySet)):
    pass


class HistoryLog(TimestampModel):
    history = models.ForeignKey(
        History,
        db_index=True,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="logs",
        verbose_name=_("history"),
    )
    fields = _fields.JSONField(
        encoder=DjangoJSONEncoder,
        verbose_name=_("fields"),
    )
    updated = _fields.JSONField(
        encoder=DjangoJSONEncoder,
        verbose_name=_("updated fields"),
    )

    objects = HistoryLogManager()

    class Meta:
        ordering = ["created_at"]
        verbose_name = _("log")
        verbose_name_plural = _("logs")

    def __str__(self):
        return gettext("History for {obj} at {tm}").format(
            obj=self.history.source,
            tm=self.created_at,
        )
