### UserProfile application
This application contains `Covid19Triage` and `HealthCheckUserProfile` models. It has been transferred to this repository from [ndoh-hub](https://github.com/praekeltfoundation/ndoh-hub/), specifically `eventstore` application.

There is a [custom migration](./migrations/0006_auto_20200818_1539.py) to improve database performance.

It is possible to import existing database dump using 
```sh
$ python manage.py loaddata
```
