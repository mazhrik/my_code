from yarn_api_client import ResourceManager
import sys
import json
import requests


import requests,json

headers = {
    'X-Requested-By': 'admin',
    'Content-Type': 'application/json',
}

RUNNINGS = []
ACCEPTED = []


def killjob():
    global RUNNINGS
    global ACCEPTED
    aliases = ["AUTOML_OCS"]

    is_running = False
    res = requests.get("http://master.rapidev.ae:8088/ws/v1/cluster/apps?states=RUNNING")
    if res.json()['apps']:
        apps = res.json()['apps']['app']
        print(apps)
        for app in apps:
            app_name = app['name']
            #print(app['id'])
            if app_name in aliases:
                RUNNINGS.append(app['id'])
            #     is_running = True
            #     break


    res = requests.get("http://master.rapidev.ae:8088/ws/v1/cluster/apps?states=ACCEPTED")
    if res.json()['apps']:
        apps = res.json()['apps']['app']
        for app in apps:
            app_name = app['name']
            #print(app['id'])
            if app_name in aliases:
                ACCEPTED.append(app['id'])
                # is_running = True
    # return is_running



    print("Running")
    print(RUNNINGS)
    print("Accepted")
    print(ACCEPTED)


    for application_id in ACCEPTED:
        rm = ResourceManager(["http://master.rapidev.ae:8088"])
        app_kill = rm.cluster_application_kill(application_id)
        print("ACCEPTED JOB KILLED SUCCESSFULLY")
    
    for application_id in RUNNINGS:
        rm = ResourceManager(["http://master.rapidev.ae:8088"])
        app_kill = rm.cluster_application_kill(application_id)
        print("RUNNING JOB KILLED SUCCESSFULLY")

# killjob()


