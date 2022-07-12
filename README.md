# django-model-history-log

Register fields updates.


## Install

Add `model_history.apps.ModelHistoryConfig` into your `INSTALLED_APPS`

```python
#!python
INSTALLED_APPS = [
    ...
    "model_history.apps.ModelHistoryConfig",
    ...
]
```
and then run

```python
./manage.py migrate
```

## Configure

### Register a model at startup

You can register a model for logging at startup using `History.register` helper:

```python
class MyAppConfig(AppConfig):
    name = "myapp"

    def ready(self):
        from model_history.models import History
        from django.contrib.auth import get_user_model

        History.register(get_user_model(), exclude=["password"])
```

You can register all models with a snippet like this

```python
class MyAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "myapp"
    verbose_name = _("My Website")

    def ready(self):
        from django.contrib.admin.models import LogEntry
        from django.contrib.auth import get_user_model
        from django.contrib.sessions.models import Session
        from model_history.models import History, HistoryLog

        User = get_user_model()
        History.register(User, exclude=["password"])
        for model in apps.get_models():
            if model not in [LogEntry, History, HistoryLog, Session, User]:
                History.register(model)
```

## Usage

### Log a single instance

You can log a single instance changes with the `HistoryManager.log()` method:

```python
instance = MyInstance.objects.get(...)
...
History.objects.log(instance)
```

###### Params

* `instance`: `models.Model` = instance to log
* `exclude`: `list[str] | None` = exclude these fields from logging
* `serializer_class`: `rest_framework.serializers.Serializer | None` = use this serializer instance


### Query a log

```python

    from django.contrib.auth import get_user_model

    history = History.objects.fetch(User.objects.first())
    history.logs.all()
```

`fetch()` always returns an History instance, regardless it is saved on db or not.
You must rely on it's `pk` value or you should check for `logs`.

## CHANGES ##

### 0.2.0

* Rename project to django-model-history-log (sorry, no migration path)
* Reformat all codebase with black
* Update isort/flake8 config
* Use django JSONField
* Remove default ordering, use only in admin
* Add register/unregister actions
* Add HistoryQuerySet.fetch api
* Save str(source) as {History,HistoryLog}.label
* Add en translations
* Add it translations

### 0.1.1

* added missing `on_delete` on HistoryRow.history field

### 0.1.0

* initial relase
