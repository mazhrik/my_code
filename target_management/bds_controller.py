import requests
from OCS_Rest import settings
import json

requests.adapters.DEFAULT_RETRIES = 3

HEADERS = {
    'X-Requested-By': 'admin',
    'Content-Type': 'application/json',
}


class BDSController(object):
    def __init__(self):
        self.ip = settings.BDS_SPARK_IP
        self.port = settings.BDS_PORT
        self.username = settings.BDS_USERNAME
        self.password = settings.BDS_PASSWORD

    def do_request(self, data):
        try:
            response = requests.post(url='http://{ip}:{port}/batches'.format(ip=self.ip, port=self.port),
                                     headers=HEADERS, data=data, verify=True,
                                     auth=(self.username, self.password), timeout=30)
            return response
        except Exception as error:
            return error

    def sentiment_analysis(self, gtr_id, ctr_id, target_type, target_subtype):
        try:
            data = {"file": "hdfs:///user/bds/spark/spark_batch/ai/sentiment.py",
                    "args": [gtr_id, ctr_id, target_type, target_subtype],
                    "queue": "Spark_Batches",
                    "pyFiles": ["hdfs:///user/bds/elastic_search/es_pyspark_handler.py",
                                "hdfs:///user/bds/identification/identification.py",
                                "hdfs:///user/bds/spark/spark_batch/publisher/publisher.py",
                                "hdfs:///user/bds/spark/spark_batch/publisher/status_codes.py"]}
            config = {
                "spark.driver.memory":"12g",
                "spark.executor.memory":"8g",
                "spark.executor.memoryOverhead":"8g"
            }
            data['conf'] = config
            response = self.do_request(json.dumps(data))
            return response
        except Exception as error:
            return error

    def change_detection(self, gtr_id, ctr_id, target_type, target_subtype):
        try:
            data = {"file": "hdfs:///user/bds/spark/spark_batch/generic/change_detection.py",
                    "queue": "Spark_Batches",
                    "args": [gtr_id, ctr_id, target_type, target_subtype],
                    "pyFiles": ["hdfs:///user/bds/elastic_search/es_pyspark_handler.py",
                                "hdfs:///user/bds/identification/identification.py",
                                "hdfs:///user/bds/spark/spark_batch/publisher/publisher.py",
                                "hdfs:///user/bds/spark/spark_batch/publisher/status_codes.py"]}
            response = self.do_request(json.dumps(data))
            return response
        except Exception as error:
            return error

    def sentiment_distribution(self, gtr_id, ctr_id, target_type, target_subtype):
        try:
            data = {"file": "hdfs:///user/bds/spark/spark_batch/generic/profile_sentiment_distribution.py",
                    "queue": "Spark_Batches",
                    "args": [gtr_id, ctr_id, target_type, target_subtype],
                    "pyFiles": ["hdfs:///user/bds/elastic_search/es_pyspark_handler.py",
                                "hdfs:///user/bds/identification/identification.py",
                                "hdfs:///user/bds/spark/spark_batch/publisher/publisher.py",
                                "hdfs:///user/bds/spark/spark_batch/publisher/status_codes.py"]}
            
            response = self.do_request(json.dumps(data))
            return response
        except Exception as error:
            return error

    def emotions_analyst(self, gtr_id, ctr_id, target_type, target_subtype):
        try:
            data = {"file": "hdfs:///user/bds/spark/spark_batch/ai/emotion.py",
                    "queue": "Spark_Batches",
                    "args": [gtr_id, ctr_id, target_type, target_subtype],
                    "pyFiles": ["hdfs:///user/bds/elastic_search/es_pyspark_handler.py",
                                "hdfs:///user/bds/identification/identification.py",
                                "hdfs:///user/bds/spark/spark_batch/publisher/publisher.py",
                                "hdfs:///user/bds/spark/spark_batch/publisher/status_codes.py"]}
            config = {
                "spark.driver.memory":"12g",
                "spark.executor.memory":"8g",
                "spark.executor.memoryOverhead":"8g"
            }
            data['conf'] = config
            response = self.do_request(json.dumps(data))
            return response
        except Exception as error:
            return error

    def text_categorization(self, gtr_id, ctr_id, target_type, target_subtype):
        try:
            data = {"file": "hdfs:///user/bds/spark/spark_batch/ai/categorization.py",
                    "queue": "Spark_Batches",
                    "args": [gtr_id, ctr_id, target_type, target_subtype],
                    "pyFiles": ["hdfs:///user/bds/elastic_search/es_pyspark_handler.py",
                                "hdfs:///user/bds/identification/identification.py",
                                "hdfs:///user/bds/spark/spark_batch/publisher/publisher.py",
                                "hdfs:///user/bds/spark/spark_batch/publisher/status_codes.py"]}
            config = {
                "spark.driver.memory":"12g",
                "spark.executor.memory":"8g",
                "spark.executor.memoryOverhead":"8g"
            }
            data['conf'] = config
            response = self.do_request(json.dumps(data))
            return response
        except Exception as error:
            return error

    def target_summary(self, gtr_id, ctr_id, target_type, target_subtype):
        try:
            data = {"file": "hdfs:///user/bds/spark/spark_batch/data_mining/target_summary.py",
                    "args": [gtr_id, ctr_id, target_type, target_subtype],
                    "queue": "Spark_Batches",
                    "pyFiles": ["hdfs:///user/bds/elastic_search/es_pyspark_handler.py",
                                "hdfs:///user/bds/identification/identification.py",
                                "hdfs:///user/bds/spark/spark_batch/publisher/publisher.py",
                                "hdfs:///user/bds/spark/spark_batch/publisher/status_codes.py"]}
            response = self.do_request(json.dumps(data))
            return response
        except Exception as error:
            return error

    def word_cloud(self, gtr_id, ctr_id, target_type, target_subtype):
        try:
            data = {"file": "hdfs:///user/bds/spark/spark_batch/data_mining/wordclouds.py",
                    "queue": "Spark_Batches",
                    "args": [gtr_id, ctr_id, target_type, target_subtype],
                    "pyFiles": ["hdfs:///user/bds/elastic_search/es_pyspark_handler.py",
                                "hdfs:///user/bds/identification/identification.py",
                                "hdfs:///user/bds/spark/spark_batch/publisher/publisher.py",
                                "hdfs:///user/bds/spark/spark_batch/publisher/status_codes.py"]}
            response = self.do_request(json.dumps(data))
            return response
        except Exception as error:
            return error

    def posts_frequent_graph(self, gtr_id, ctr_id, target_type, target_subtype):
        try:
            data = {"file": "hdfs:///user/bds/spark/spark_batch/analytics/posts_frequency.py",
                    "queue": "Spark_Batches",
                    "args": [gtr_id, ctr_id, target_type, target_subtype],
                    "pyFiles": ["hdfs:///user/bds/elastic_search/es_pyspark_handler.py",
                                "hdfs:///user/bds/identification/identification.py",
                                "hdfs:///user/bds/spark/spark_batch/publisher/publisher.py",
                                "hdfs:///user/bds/spark/spark_batch/publisher/status_codes.py"]}
            response = self.do_request(json.dumps(data))
            return response
        except Exception as error:
            return error

    def posts_categorization_distributions(self, gtr_id, ctr_id, target_type, target_subtype):
        try:
            data = {"file": "hdfs:///user/bds/spark/spark_batch/analytics/profile_categorization_distribution.py",
                    "queue": "Spark_Batches",
                    "args": [gtr_id, ctr_id, target_type, target_subtype],
                    "pyFiles": ["hdfs:///user/bds/elastic_search/es_pyspark_handler.py",
                                "hdfs:///user/bds/identification/identification.py",
                                "hdfs:///user/bds/spark/spark_batch/publisher/publisher.py",
                                "hdfs:///user/bds/spark/spark_batch/publisher/status_codes.py"]}
            response = self.do_request(json.dumps(data))
            return response
        except Exception as error:
            return error

    def frequent_hashtags(self, gtr_id, ctr_id, target_type, target_subtype):
        try:
            data = {"file": "hdfs:///user/bds/spark/spark_batch/data_mining/most_used_hashtags.py",
                    "queue": "Spark_Batches",
                    "args": [gtr_id, ctr_id, target_type, target_subtype],
                    "pyFiles": ["hdfs:///user/bds/elastic_search/es_pyspark_handler.py",
                                "hdfs:///user/bds/identification/identification.py",
                                "hdfs:///user/bds/spark/spark_batch/publisher/publisher.py",
                                "hdfs:///user/bds/spark/spark_batch/publisher/status_codes.py"]}
            response = self.do_request(json.dumps(data))
            return response
        except Exception as error:
            return error

    def common_words(self, gtr_id, ctr_id, target_type, target_subtype):
        try:
            data = {"file": "hdfs:///user/bds/spark/spark_batch/data_mining/common_words.py",
                    "args": [gtr_id, ctr_id, target_type, target_subtype],
                    "queue": "Spark_Batches",
                    "pyFiles": ["hdfs:///user/bds/elastic_search/es_pyspark_handler.py",
                                "hdfs:///user/bds/identification/identification.py",
                                "hdfs:///user/bds/spark/spark_batch/publisher/publisher.py",
                                "hdfs:///user/bds/spark/spark_batch/publisher/status_codes.py"]}
            response = self.do_request(json.dumps(data))
            return response
        except Exception as error:
            return error

    def text_processing_req(self, input_string, algorithm_type, data_id):
        try:
            data = {"file": "hdfs:///user/bds/spark/spark_batch/data_mining/text_processing.py",
                    "args": [input_string, algorithm_type, data_id],
                    "queue": "Spark_Batches",
                    "pyFiles": ["hdfs:///user/bds/elastic_search/es_pyspark_handler.py",
                                "hdfs:///user/bds/identification/identification.py",
                                "hdfs:///user/bds/spark/spark_batch/publisher/publisher.py",
                                "hdfs:///user/bds/spark/spark_batch/publisher/status_codes.py"]}
            response = self.do_request(json.dumps(data))
            return response
        except Exception as error:
            return error

    def behavior_analysis(self, gtr_id, ctr_id, target_type, target_subtype):
        try:
            data = {"file": "hdfs:///user/bds/spark/spark_batch/data_mining/behavioural_analysis.py",
                    "args": [gtr_id, ctr_id, target_type, target_subtype],
                    "queue": "Spark_Batches",
                    "pyFiles": ["hdfs:///user/bds/elastic_search/es_pyspark_handler.py",
                                "hdfs:///user/bds/identification/identification.py",
                                "hdfs:///user/bds/spark/spark_batch/publisher/publisher.py",
                                "hdfs:///user/bds/spark/spark_batch/publisher/status_codes.py"]}
            response = self.do_request(json.dumps(data))
            return response
        except Exception as error:
            return error

    def image_analytics(self, current_link, target_type, target_subtype, title):
        try:
            data = {"queue":"Spark_Batches", 
            "file": "hdfs:///user/bds/spark/spark_batch/image_analytics/frs.py",
            "args": [current_link, target_type,target_subtype, title], 
            "pyFiles":["hdfs:///user/bds/elastic_search/es_pyspark_handler.py"]}
            response = self.do_request(json.dumps(data))
            return response
        except Exception as error:
            return str(error)

