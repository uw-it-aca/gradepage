#!/bin/bash

if [ "$ENV"  = "localdev" ]
then

  python manage.py migrate
  python manage.py loaddata persistent_messages.json

else

  export GUNICORN_CMD_ARGS="--timeout 300"

fi
