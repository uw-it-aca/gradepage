FROM gcr.io/uwit-mci-axdd/django-container:1.3.6 as app-container

USER root

RUN apt-get update && apt-get install mysql-client libmysqlclient-dev vim -y

USER acait

ADD --chown=acait:acait course_grader/VERSION /app/course_grader/
ADD --chown=acait:acait setup.py /app/
ADD --chown=acait:acait requirements.txt /app/
RUN . /app/bin/activate && pip install -r requirements.txt

RUN . /app/bin/activate && pip install mysqlclient

ADD --chown=acait:acait . /app/
ADD --chown=acait:acait docker/ project/
ADD --chown=acait:acait docker/app_start.sh /scripts
RUN chmod u+x /scripts/app_start.sh

RUN . /app/bin/activate && pip install nodeenv && nodeenv -p &&\
    npm install -g npm && ./bin/npm install less@3.13.1 -g

RUN . /app/bin/activate && python manage.py collectstatic --noinput &&\
    python manage.py compress -f

FROM gcr.io/uwit-mci-axdd/django-test-container:1.3.6 as app-test-container

COPY --from=app-container /app/ /app/
COPY --from=app-container /static/ /static/
