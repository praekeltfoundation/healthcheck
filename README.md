# healthcheck

## Running tests
```
$ pip install -e .
$ python manage.py test
```

## Running locally
```
$ createdb healthcheck
$ DJANGO_SETTINGS_MODULE=healthcheck.settings.text python manage.py migrate
$ DJANGO_SETTINGS_MODULE=healthcheck.settings.text python manage.py runserver
