FROM praekeltfoundation/django-bootstrap:py3.7-stretch

RUN apt-get update && \
	apt-get install -yq --no-install-recommends wget make git && \
	apt-get clean && \
	rm -rf /var/lib/apt/lists/*

ENV DJANGO_SETTINGS_MODULE "healthcheck.settings.production"
CMD ["healthcheck.wsgi:application"]

COPY setup.py /app
COPY requirements.txt /app
RUN pip install -e .

COPY . /app

RUN DJANGO_SETTINGS_MODULE='healthcheck.settings.test' python manage.py collectstatic --noinput
