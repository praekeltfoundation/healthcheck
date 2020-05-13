FROM praekeltfoundation/django-bootstrap:py3.7-stretch

ENV DJANGO_SETTINGS_MODULE "healthcheck.settings.production"
CMD ["healthcheck.wsgi:application"]
COPY setup.py /app
RUN pip install -e .

COPY . /app
RUN DJANGO_SETTINGS_MODULE='healthcheck.settings.test' python manage.py collectstatic --noinput
