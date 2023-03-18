# settings for celery
# BROKER_URL = 'pyamqp://ocs_broker:rapidev@192.168.18.27/v_ocs_broker'
# CELERY_RESULT_BACKEND = ''
# CELERY_ACCEPT_CONTENT = ['application/json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json'
# CELERY_TIMEZONE = 'Asia/Karachi'
# broker_url = 'pyamqp://ocs_broker:rapidev@10.10.101.103/v_ocs_broker'
broker_url = 'pyamqp://ocs_broker:rapidev@10.10.102.10/v_ocs_broker'

# broker_url = 'pyamqp://ocs_broker:
# rapidev@localhost/v_ocs_broker'
result_backend = 'rpc://'

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Asia/Karachi'
enable_utc = True
