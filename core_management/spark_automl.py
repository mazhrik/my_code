import requests,json
from OCS_Rest import settings






def is_running():
        headers = {
        'X-Requested-By': 'admin',
        'Content-Type': 'application/json',
        }
        aliases = ['bds-automl.py','AUTOML_OCS']
        is_running = False
        res = requests.get("http://{}:{}/ws/v1/cluster/apps?states=RUNNING".format(settings.YARN_IP,settings.YARN_PORT))
        if res.json()['apps']:
            apps = res.json()['apps']['app']
            for app in apps:
                app_name = app['name']
                print(app_name)
                if app_name in aliases:
                    is_running = True
                    break



        res = requests.get("http://{}:{}/ws/v1/cluster/apps?states=ACCEPTED".format(settings.YARN_IP,settings.YARN_PORT))
        if res.json()['apps']:
            apps = res.json()['apps']['app']
            for app in apps:
                app_name = app['name']
                print(app_name)
                if app_name in aliases:
                    is_running = True
                    break
        return is_running


class SparkApiController(object):
    def __init__(self):
        global is_running 
        self.name = settings.BDS_USERNAME
        self.password = settings.BDS_PASSWORD
        self.server_base_url = 'http://{}:{}/batches'.format(settings.BDS_SPARK_IP,settings.BDS_PORT)
        self.name = "AUTOML_OCS"
        self.headers = {'X-Requested-By': 'admin',
                        'Content-Type': 'application/json'}
        self.is_running = is_running
    
    def ml_training(self, training_time, is_csv ,  csv_name, is_datawarehouse, from_, to, model_name, type_):
        print(vars(self))
        datawarehouse = str(is_datawarehouse).lower().title()
        args = [training_time, is_csv,csv_name, datawarehouse, from_, to, model_name, type_]
        args = [str(val) for val  in args]
        print("ml_training----------------\n\n------------------",args)
        data = {
            "queue":"Spark_Batches", 
            "file": "hdfs:///user/automl/bds-automl.py", 
            "driverMemory": "20g", 
            "executorMemory": "12g",
            "conf":{
                "spark.executor.memoryOverhead":"8g",
                "spark.executor.instances":3
            },
            "name":self.name,
            "args":args,
        }
        data=json.dumps(data)
        print(self.server_base_url)
        if not self.is_running():
            result = requests.post(url=self.server_base_url,  headers=self.headers, data=data, verify=False, auth=(self.name, self.password)) 
            return {"status_code":400,"message":"Job Successfully Started","result":result}
        else:
            return {"status_code":400,"message":"A Job is already in progress","result":[]}

