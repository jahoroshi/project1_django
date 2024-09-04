#!/bin/bash

PORT=8000

if lsof -i :$PORT > /dev/null; then
    echo "Port $PORT is already in use. Killing all processes using the port."
    lsof -t -i :$PORT | xargs -r kill -9
    sleep 2
fi

exec /home/ubuntu/.cache/pypoetry/virtualenvs/project1-6Bpdu8kL-py3.12/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 -c /home/ubuntu/project1/project1/config/gunicorn.conf.py project_1.wsgi:application
