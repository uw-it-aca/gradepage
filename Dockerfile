ARG DJANGO_CONTAINER_VERSION=1.4.1

FROM gcr.io/uwit-mci-axdd/django-container:${DJANGO_CONTAINER_VERSION} as app-container

USER root

RUN apt-get update && apt-get install mysql-client libmysqlclient-dev -y

USER acait

ADD --chown=acait:acait . /app/
ADD --chown=acait:acait docker/ /app/project/
ADD --chown=acait:acait docker/app_start.sh /scripts
RUN chmod u+x /scripts/app_start.sh

RUN /app/bin/pip install -r requirements.txt
RUN /app/bin/pip install mysqlclient

RUN . /app/bin/activate && pip install nodeenv && nodeenv -p &&\
    npm install -g npm && ./bin/npm install less -g

RUN . /app/bin/activate && python manage.py collectstatic --noinput &&\
    python manage.py compress -f

FROM gcr.io/uwit-mci-axdd/django-test-container:${DJANGO_CONTAINER_VERSION} as app-test-container

COPY --from=app-container /app/ /app/
COPY --from=app-container /static/ /static/
