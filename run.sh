#!/bin/sh
COMMAND=$*
if [ $1 = 'test' ]; then
    COMMAND="python manage.py test && flake8"
fi
echo $COMMAND
docker-compose run app sh -c "$COMMAND"