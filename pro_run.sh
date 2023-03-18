#!/bin/bash

echo -e "------------------------------------------------ OCS CORE START---------------------------------------------"

periodic_task_worker="Periodic Task Worker"
periodic_task_beat="Periodic Task Beat"
osint_core="OSINT Core"


gotodirectory="cd /home/core/Desktop/ocs_rest/"
activatevirtualenv="source /home/core/Desktop/ocs_rest/venv/bin/activate"
periodictaskworker="nohup celery -A OCS_Rest worker -l info >> /home/core/Desktop/ocs_logs/polling.log"
periodictaskbeat="nohup celery -A OCS_Rest beat -l info >> /home/core/Desktop/ocs_logs/beat.log"
osintcore="nohup gunicorn --bind=0:8000 --workers=5 --env DJANGO_SETTINGS_MODULE=OCS_Rest.settings OCS_Rest.wsgi >> /home/core/Desktop/ocs_logs/ocs.log"

set -e


gnome-terminal --tab --title="$periodic_task_worker" --command="bash -c 'echo -----------Running --------------; $gotodirectory;$periodictaskworker;$SHELL '" \
               --tab --title="$periodic_task_beat" --command="bash -c 'echo Running; $gotodirectory;$periodictaskbeat; $SHELL'"




cd /home/core/Desktop/ocs_rest/
nohup gunicorn --bind=0:8000 --workers=8 --timeout 120 --env DJANGO_SETTINGS_MODULE=OCS_Rest.settings OCS_Rest.wsgi |& tee -a /home/core/Desktop/ocs_logs/ocs.log