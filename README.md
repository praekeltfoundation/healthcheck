# healthcheck

## Installation
```sh
$ docker-compose up --build
```
You should configure `.env` file to ensure that your instance works as intended.

Example `.env` config:
```sh
DJANGO_SETTINGS_MODULE=healthcheck.settings.dev
SECRET_KEY=secret-key
DATABASE_URL=psql://user:password@db:5432/table
ALLOWED_HOSTS=*
TURN_API_KEY=turn-api-key
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
CELERY_ACCEPT_CONTENT=application/json
CELERY_TASK_SERIALIZER=json
CELERY_RESULT_SERIALIZER=json
```
`PostgreSQL` is used by default in docker container named `db`. It's best to not change that. You can change the following enviromental variables in `docker-compose.yml`:
```yml
db:
    environment: 
        - POSTGRES_PASSWORD=django
        - POSTGRES_USER=django
        - POSTGRES_DB=healthcheck
```
You also need to include those in `DATABASE_URL`.
You should re-build your local container after adding new dependencies.

After building, create admin account
```sh
$ python manage.py createsuperuser
```
You can use provided credentials to log into [admin panel](http://127.0.0.1:8000/admin).

## Running
```sh
$ docker-compose up
```

You can access shell by either installing all dependencies from `setup.py`, `requirements.txt` and `requirements-dev.txt` in your `venv` and running
```sh
$ python manage.py shell
```
 or by connecting to docker container shell using following command:
```sh
$ docker-compose run django bash
```

## Submitting a PR
Before submitting a PR make sure you have ran tests
```sh
$ pip install -e .
$ python manage.py test
```
and formatted your code. To do so, run:
```
$ isort **/*.py
$ black .
$ flake8 .
```
`flake8` will point out any errors but it is not used during PR testing. It is best to keep the least amount of these errors.
It is strongly advised to wrap any of requests your test make with [responses](https://github.com/getsentry/responses) library.

## Load fixtures
```
$ python loaddata <fixturename>
```
where `<fixturename>` is the name of the fixture file you’ve created. 
Each time you run loaddata, the data will be read from the fixture and re-loaded into the database. 
Note this means that if you change one of the rows created by a fixture and then run loaddata again, you’ll wipe out any changes you’ve made.

or 
```
$ ./manage.py loaddata clinicfinder/fixtures/*.json
```
To load all fixtures at once