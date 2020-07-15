FROM praekeltfoundation/django-bootstrap:py3.7-stretch

RUN apt-get update && \
	apt-get install -yq --no-install-recommends wget make git && \
	apt-get clean && \
	rm -rf /var/lib/apt/lists/*

# COPY ./nginx.conf /etc/nginx/conf.d

ENV DJANGO_SETTINGS_MODULE "healthcheck.settings.production"
CMD ["healthcheck.wsgi:application"]
COPY setup.py /app
RUN pip install -e .

COPY . /app

RUN pip install -r ./requirements.txt

RUN DJANGO_SETTINGS_MODULE='healthcheck.settings.test' python manage.py collectstatic --noinput
