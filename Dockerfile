FROM praekeltfoundation/django-bootstrap:py3.7-stretch

ENV DJANGO_SETTINGS_MODULE "healthcheck.settings.production"
CMD ["healthcheck.wsgi:application"]

COPY setup.py /app
COPY requirements.txt /app

RUN apt-get update && apt-get install -y gdal-bin
RUN pip install -e .

COPY . /app

RUN DJANGO_SETTINGS_MODULE=healthcheck.settings.test ./manage.py collectstatic --noinput
