FROM ghcr.io/praekeltfoundation/docker-django-bootstrap-nw:py3.9-bullseye as builder

RUN apt-get-install.sh build-essential libpq-dev

COPY setup.py requirements.txt ./

# Remove the pip config to re-enable caching.
RUN rm /etc/pip.conf
RUN pip install -e .
RUN mkdir /wheels
# Copy any binary wheels we've built into /wheels for installation in the
# runtime image.
RUN for f in $(find /root/.cache/pip/wheels -type f | grep -v 'none-any.whl$'); do cp $f /wheels/; done


FROM ghcr.io/praekeltfoundation/docker-django-bootstrap-nw:py3.9-bullseye

ENV DJANGO_SETTINGS_MODULE "healthcheck.settings.production"
CMD ["healthcheck.wsgi:application"]

RUN apt-get-install.sh gdal-bin

COPY --from=builder /wheels /wheels

COPY . /app
RUN pip install -f /wheels -e .

RUN DJANGO_SETTINGS_MODULE=healthcheck.settings.test ./manage.py collectstatic --noinput
