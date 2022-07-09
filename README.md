# django-model-history #

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

### 0.1.1

* added missing `on_delete` on HistoryRow.history field

### 0.1.0

* initial relase
