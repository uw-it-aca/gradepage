#!/bin/bash

if [ "$ENV"  = "localdev" ]
then

  python manage.py migrate
  python manage.py loaddata persistent_messages.json

else

  # adjust timeouts to account for slow downstream response
  #DOWNSTREAM_TIMEOUT=90

  #export GUNICORN_CMD_ARGS="--timeout $DOWNSTREAM_TIMEOUT"

  #sed 's/\(^[ ]*server {\)/ proxy_read_timeout '$DOWNSTREAM_TIMEOUT's;\n\n\1/' /etc/nginx/nginx.conf > /tmp/nginx.tmp
  #cat /tmp/nginx.tmp > /etc/nginx/nginx.conf

fi
