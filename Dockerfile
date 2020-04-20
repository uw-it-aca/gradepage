FROM acait/django-container:1.0.24 as django

USER root
RUN apt-get update && apt-get install mysql-client libmysqlclient-dev libpq-dev -y
USER acait

ADD --chown=acait:acait course_grader/VERSION /app/course_grader/
ADD --chown=acait:acait setup.py /app/
ADD --chown=acait:acait requirements.txt /app/

RUN . /app/bin/activate && pip install -r requirements.txt

RUN . /app/bin/activate && pip install nodeenv && nodeenv -p && npm install -g npm && ./bin/npm install less -g

ADD --chown=acait:acait . /app/
ADD --chown=acait:acait docker/ project/
ADD --chown=acait:acait docker/app_start.sh /scripts
RUN chmod u+x /scripts/app_start.sh

RUN . /app/bin/activate && python manage.py compress -f && python manage.py collectstatic  --noinput
