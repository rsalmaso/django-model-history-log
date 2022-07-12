# django-model-history-log #

Register fields updates.


## Install ##

Add `model_history.apps.ModelHistoryConfig` into your `INSTALLED_APPS`

```
#!python
INSTALLED_APPS = [
    ...
    "model_history.apps.ModelHistoryConfig",
    ...
]
```

## CHANGES ##

### dev

* Rename project to django-model-history-log (sorry, no migration path)
* Reformat all codebase with black
* Update isort/flake8 config
* Use django JSONField
* Remove default ordering, use only in admin
* Add register/unregister actions

### 0.1.1

* added missing `on_delete` on HistoryRow.history field

### 0.1.0

* initial relase
