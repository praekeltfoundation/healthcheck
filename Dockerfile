FROM praekeltfoundation/django-bootstrap:py3.7-stretch

ENV DJANGO_SETTINGS_MODULE "healthcheck.settings.production"
CMD ["healthcheck.wsgi:application"]

RUN apt-get update && apt-get install -y gcc  \
    && pip install zbar-py==1.0.4 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get purge -y --auto-remove gcc

COPY setup.py /app
COPY requirements.txt /app
RUN pip install -e .

COPY . /app

RUN DJANGO_SETTINGS_MODULE=healthcheck.settings.test ./manage.py collectstatic --noinput
