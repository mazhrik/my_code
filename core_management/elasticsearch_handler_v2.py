import datetime
import time

from elasticsearch import Elasticsearch
import json
import requests
from datetime import date
from OCS_Rest import settings
import calendar
from operator import itemgetter
import re

SIZE = 10000

headers = {
    "Content-Type": "application/json",
}


class ElasticsearchHandler(object):

    def __init__(self):
        self.es = None
        self.case_index = 'case_data'
        self.cluster_ip = settings.CLUSTER_IP
        self.port = settings.PORT_ES
        self.username = settings.USERNAME_ES
        self.password = settings.PASSWORD_ES
        if self.connect():
            print("Connected to Elasticsearch Cluster")
        else:
            print("Connection failed reconnecting to Elasticsearch Cluster")
            self.re_connect()

    def connect(self):
        try:
            self.es = Elasticsearch(['http://{ip}:{port}/'.format(ip=self.cluster_ip, port=self.port)],
                                    http_auth=(self.username, self.password))
            return True
        except Exception as error:
            print(error)
            return False

    # def get_response_by_type(self, index, document_type, channel, limit=20):
    #     try:
    #         actual_response = []
    #         responses = self.es.search(
    #             index=index,
    #             body={
    #                 "query": {
    #                     "match": {
    #                         "Channel": channel
    #                     }
    #                 },
    #                 "size": limit
    #             }
    #         )
    #         for response in responses['hits']['hits']:
    #             actual_response.append(response['_source'])
    #         return actual_response
    #     except Exception as error:
    #         print(error)

    def re_connect(self):
        try:
            return self.connect()
        except Exception as error:
            print(error)
            return False

    def get_target_response(self, index, limit=20):
        count = 0
        try:
            res = self.es.search(
                index=index,
                body={
                    "query": {
                        "match_all": {
                        },
                    },
                    "size": SIZE,
                },

            )
            for i in res['hits']['hits']:
                count = count + 1
                print(json.dumps(i["_source"]))

        except Exception as error:
            print(error)
        print(count)


    def get_ml_model(self, index):
        actual_response=[]
        try:
            res = self.es.search(
                index=index,
                body={
                    "query": {
                        "match_all": {}
                    
                    }
                   
                },
            )
            for response in res['hits']['hits']:
                actual_response.append(response['_source'])
            return actual_response
        except Exception as error:
            print(error)    

    def get_filesize(self,gtr,target_type,target_subtype):
        folder_size = ""
        index = "{}_{}_meta_data".format(target_type,target_subtype)
        try:
            query = {
                "query":{
                    "match":{
                        "GTR":gtr
                    }
                }
            } 
            res = self.es.search(
                index=index,
                body=query
            )
            folder_size = res['hits']['hits'][0]['_source']['folder_size']
            folder_size = str(int(folder_size) / 1000000)
            return folder_size
        except Exception as error:
            print(error)
            return False


    def get_response_by_index(self, index, channel, limit=20):
        # try:
        #     actual_response = []
        #     responses = self.es.search(
        #         index=index,
        #         body={
        #             "query": {
        #                 "match": {
        #                     "Channel": channel
        #                 }
        #             },
        #             "size": limit
        #         }
        #     )
        #     for response in responses['hits']['hits']:
        #         actual_response.append(response['_source'])
        #     return actual_response
        # except Exception as error:
        #     print(error)
        today = date.today()
        # actual = today.strftime("%yyyy/%mm/%d")
        # actual_date = actual.replace(hour=23, minute=30)
        # actual_date = today.strftime("%y/%m/%d")
        # pub = lastItem.pub_date
        end_date = datetime.datetime(today.year, today.month, today.day)
        end_date = end_date.timestamp()
        # ts = ciso8601.parse_datetime(end_date)
        # time.mktime(ts.timetuple())
        # end_date = datetime.datetime(pub.year, pub.month, pub.day)

        created_on_gte = datetime.datetime.timestamp(datetime.datetime.now() + datetime.timedelta(hours=-48*2))
        created_on_lte = datetime.datetime.timestamp(datetime.datetime.now() + datetime.timedelta(hours=24))
        actual_response = []
        try:
            
            responses = self.es.search(
                index=index,
                body={
                    "query": {
                        "bool": {
                            "must": [
                                {
                                    "match": {
                                        "Channel_name.keyword": channel
                                    }
                                },
                                {
                                "range": {
                                    "created_on": {
                                        "gte": created_on_gte * 1000,
                                        "lte": created_on_lte * 1000
                                    }
                                }
                            }

                            ]
                        }
                    },
                    "sort": {
                        "created_on": {
                            "order": "desc"
                        }
                    },
                    "size": limit,
                },
            )
            if responses['hits']['hits']:
                for response in responses['hits']['hits']:
                    actual_response.append(response['_source'])
                return actual_response
            else:
                return actual_response
        except Exception as error:
            print(error)

    def get_twitter_trends(self, index, country, created_on_gte, created_on_lte, limit=20):
        try:
            actual_response = []
            responses = self.es.search(
                index=index,
                body={
                    "query": {
                        "bool": {
                            "must": [
                                {
                                    "range": {
                                        "created_on": {
                                            "gte": created_on_gte * 1000,
                                            "lte": created_on_lte * 1000
                                        }
                                    }
                                },
                                {
                                    "match": {
                                        "twitter_country_trends.country": country
                                    }
                                }
                            ]
                        }
                    },
                    "size": limit,
                    "from": 0,
                    "sort": {
                        "created_on": {
                            "order": "desc"
                        }
                    }
                },
            )
            for response in responses['hits']['hits']:
                actual_response.append(response['_source'])
            return actual_response
        except Exception as error:
            print(error)

    def query_generator(self, document_type, index, idx_type, gtr, limit):
        responses = self.es.search(
            index=index,
            doc_type=document_type,
            body={
                "query": {
                    "bool": {
                        "must": [
                            {
                                "match_phrase": {
                                    "_type": idx_type
                                }
                            },
                            {
                                "match_phrase": {
                                    "GTR": gtr
                                }
                            }
                        ]
                    }

                }, "size": limit}
        )
        for response in responses['hits']['hits']:
            responses.append(response['_source'])
        return responses

    def get_trends(self, index, created_on_gte, created_on_lte, limit=20):
        try:
            actual_response = []
            print('created_on', created_on_gte * 1000)
            print('created_on', created_on_lte * 1000)
            responses = self.es.search(
                index=index,
                body={
                    "query": {
                        "range": {
                            "created_on": {
                                "gte": round(created_on_gte * 1000),
                                "lte": round(created_on_lte * 1000)
                            }

                        }
                    },
                    "size": limit
                }
            )
            for response in responses['hits']['hits']:
                actual_response.append(response['_source'])
            print(actual_response)
            return actual_response
        except Exception as error:
            print(error)

    def get_google_trends(self, index, country, limit=20):
        try:
            actual_response = []
            responses = self.es.search(
                index=index,
            #     body={
            #         "query": {
            #             "bool": {
            #                 "must": [
            #                     {
            #                         "match": {
            #                             "google_trends_all.country": country
            #                         }
            #                     }
            #                 ]
            #             }
            #         },
            #         "size": limit,
            #         "from": 0,
            #         "sort": {
            #             "created_on": {
            #                 "order": "desc"
            #             }
            #         }
            #     },
            # )

                       body={
                    "query": {
                        "match_all":{}
                    },
                    "size": limit,
                    "from": 0,
                    "sort": {
                        "created_on": {
                            "order": "desc"
                        }
                    }
                },
            )
            for response in responses['hits']['hits']:
                actual_response.append(response['_source'])
            return actual_response
        except Exception as error:
            print(error)

    def get_google_trends_by_country(self, index, country, limit=20):
        try:

            actual_response = []
            responses = self.es.search(

                index=index,
                        body={
                    "query": {
                        "bool": {
                            "must": [
                                {
                                    "match": {
                                        "google_trends_all.country": country
                                    }
                                }
                            ]
                        }
                    },
                    "size": limit,
                    "from": 0,
                    "sort": {
                        "created_on": {
                            "order": "desc"
                        }
                    }
                },
            )
            for response in responses['hits']['hits']:
                actual_response.append(response['_source'])
            return actual_response
        except Exception as error:
            print(error)

    def get_response_by_gtr(self, index, gtr_id, limit=20):
        # print(get_ml_model"------------LIMIT------", limit)
        all_responses = dict()
        data_resp = dict()
        try:
            responses = self.es.search(
                index=index,
                body=
                {
                    "query": {
                        "match": {
                            "GTR": gtr_id
                        },
                    },
                    'size': limit

                }
            )
            count = 0
            for res in responses['hits']['hits']:
                data_resp = dict(res.copy())
                data_resp["_source"].update({'es_id': str(res['_id'])})
                if data_resp["_type"] not in all_responses:
                    all_responses[data_resp["_type"]] = [data_resp["_source"]]
                else:
                    all_responses[data_resp["_type"]].append(data_resp["_source"])
            return all_responses['_doc'], count
        except Exception as error:
            # print(error)
            return [], 0
    def get_response_by_gtr_portfolio_report(self, index, gtr_id):
        # print(get_ml_model"------------LIMIT------", limit)
        response_result=[]
        try:
            responses = self.es.search(
                index=index,
                body=
                {
                    "query": {
                        "match": {
                            "GTR": gtr_id
                        },
                    },

                }
            )

            for res in responses['hits']['hits']:
                response_result.append(res['_source'])
            return response_result
        except Exception as error:
            print(error)
                  

    def get_all_posts(self, lte=0, size=100):
        all_responses = dict()
        try:
            responses = self.es.search(
                index='*_*_posts',

                body=
                {
                    "query": {
                        "match_all": {}
                    },
                    "from": lte,
                    "size": size,
                }
            )
            count = 0
            for res in responses['hits']['hits']:
                data_resp = dict(res.copy())
                data_resp["_source"].update({'es_id': str(res['_id'])})
                if data_resp["_type"] not in all_responses:
                    all_responses[data_resp["_type"]] = [data_resp["_source"]]
                else:
                    all_responses[data_resp["_type"]].append(data_resp["_source"])
            return all_responses['_doc'], count
        # ,
        # "sort": {
        #     "posts.comments.timestamp": {
        #         "order": "desc"
        #     }
        except Exception as error:
            # print(error)
            return [], 0

    def get_all_followers(self, lte=0, size=100):
        all_responses = dict()
        try:
            responses = self.es.search(
                index='*_*_followers',

                body=
                {
                    "query": {
                        "match_all": {}
                    },
                    "from": lte,
                    "size": size,
                }
            )
            count = 0
            for res in responses['hits']['hits']:
                data_resp = dict(res.copy())
                data_resp["_source"].update({'es_id': str(res['_id'])})
                if data_resp["_type"] not in all_responses:
                    all_responses[data_resp["_type"]] = [data_resp["_source"]]
                else:
                    all_responses[data_resp["_type"]].append(data_resp["_source"])
            return all_responses['_doc'], count
        # ,
        # "sort": {
        #     "posts.comments.timestamp": {
        #         "order": "desc"
        #     }
        except Exception as error:
            # print(error)
            return [], 0

    def get_all_followings(self, lte=0, size=100):
        all_responses = dict()
        try:
            responses = self.es.search(
                index='*_*_following',

                body=
                {
                    "query": {
                        "match_all": {}
                    },
                    "from": lte,
                    "size": size,
                }
            )
            count = 0
            for res in responses['hits']['hits']:
                data_resp = dict(res.copy())
                data_resp["_source"].update({'es_id': str(res['_id'])})
                if data_resp["_type"] not in all_responses:
                    all_responses[data_resp["_type"]] = [data_resp["_source"]]
                else:
                    all_responses[data_resp["_type"]].append(data_resp["_source"])
            return all_responses['_doc'], count
        # ,
        # "sort": {
        #     "posts.comments.timestamp": {
        #         "order": "desc"
        #     }
        except Exception as error:
            # print(error)
            return [], 0

    def get_posts_by_gtr(self, gtr, lte=0, size=100):
        all_responses = dict()
        try:
            responses = self.es.search(
                index='*_*_posts',
                body=
                {
                    "query": {
                        "match": {
                            "GTR": gtr
                        }
                    },
                    "from": lte,
                    "size": size,
                }
            )
            count = 0
            for res in responses['hits']['hits']:
                data_resp = dict(res.copy())
                data_resp["_source"].update({'es_id': str(res['_id'])})
                if data_resp["_type"] not in all_responses:
                    all_responses[data_resp["_type"]] = [data_resp["_source"]]
                else:
                    all_responses[data_resp["_type"]].append(data_resp["_source"])
            return all_responses['_doc'], count
        # ,
        # "sort": {
        #     "posts.comments.timestamp": {
        #         "order": "desc"
        #     }
        except Exception as error:
            # print(error)
            return [], 0

    def get_followers_by_gtr(self, gtr, lte=0, size=100):
        all_responses = dict()
        try:
            responses = self.es.search(
                index='*_*_followers',
                body=
                {
                    "query": {
                        "match": {
                            "GTR": gtr
                        },
                    },
                    "from": lte,
                    "size": size,
                }
            )
            count = 0
            for res in responses['hits']['hits']:
                data_resp = dict(res.copy())
                data_resp["_source"].update({'es_id': str(res['_id'])})
                if data_resp["_type"] not in all_responses:
                    all_responses[data_resp["_type"]] = [data_resp["_source"]]
                else:
                    all_responses[data_resp["_type"]].append(data_resp["_source"])
            return all_responses['_doc'], count
        except Exception as error:
            # print(error)
            return [], 0

    def get_followings_by_gtr(self, gtr, lte=0, size=100):
        all_responses = dict()
        try:
            responses = self.es.search(
                index='*_*_following',
                body=
                {
                    "query": {
                        "match": {
                            "GTR": gtr
                        },
                    },
                    "from": lte,
                    "size": size,
                }
            )
            count = 0
            for res in responses['hits']['hits']:
                data_resp = dict(res.copy())
                data_resp["_source"].update({'es_id': str(res['_id'])})
                if data_resp["_type"] not in all_responses:
                    all_responses[data_resp["_type"]] = [data_resp["_source"]]
                else:
                    all_responses[data_resp["_type"]].append(data_resp["_source"])
            return all_responses['_doc'], count
        except Exception as error:
            # print(error)
            return [], 0

    def get_response_by_alpha_gtr(self, index, doc_type, alpha_gtr, limit=20):
        all_responses = dict()

        try:
            responses = self.es.search(
                index=index,
                body={
                    "query": {
                        "match": {
                            "alpha_GTR": alpha_gtr
                        },
                    },
                    "size": limit
                }
            )
            count = 0
            for res in responses['hits']['hits']:
                if res["_type"] == 'pos_followers':
                    count += 1
                if res["_type"] not in all_responses:

                    all_responses[res["_type"]] = [res["_source"]]
                else:
                    all_responses[res["_type"]].append(res["_source"])

            # print(all_responses)
            return all_responses
        except Exception as error:
            return error

    def get_response_by_gtr_and_type(self, index, gtr_id, document_type, limit=20):
        try:
            res = self.es.search(
                index=index,
                doc_type=document_type,
                body={
                    "query": {
                        "match": {
                            'GTR': gtr_id
                        },
                    },
                    "size": limit
                },

            )
            print(res['hits']['hits']['_type'])
        except Exception as error:
            print(error)

    def get_image_analysis_FRS(self, title, limit=100):
        try:
            res = self.es.search(
                index="image_analytics_tms",
                body={
                    "query": {
                        "bool":{
                            "must":[
                                {
                                    "match": {
                                        "title.keyword": str(title)
                                    }

                                },
                            ],
                            # "filter": [
                            #     {
                            #     "range": {
                            #         "distance": {
                            #         "lt": 10,
                            #         }
                            #     }
                            #     }
                            # ]
                        }                
                    },
                    "sort":[
                        {
                            "distance":{"order":"asc"}
                        }
                    ],
                    "size": limit,
                }
            )
            data = []
            for res in res['hits']['hits']:
                print("res,-----------", res)
                if res:
                    data.append(res['_source'])
            return data
        except Exception as e:
            print(e)
            return []
    def delete_image_analysis_FRS(self, title):
        try:
            res = self.es.search(
                index="image_analytics_tms",
                body={
                    "query": {
                        "match": {
                            "title": str(title)
                        }
                        
                    }
                }
            )
            data = []
            for res in res['hits']['hits']:
                if res:
                    data.append(res['_id'])
            print(data)        
            for deleted_data in data:
                res = self.es.delete(
                    index="image_analytics_tms",
                    id=deleted_data
                )
            print('deleted')


        except Exception as e:
            print(e)
            return []

    def get_response_id(self, id):

        try:
            res = self.es.search(
                body={
                    "query": {
                        "match": {
                            '_id': id
                        }
                    }
                }
            )
            for res in res['hits']['hits']:
                return res['_source']

        except Exception as error:
            return error

    def bi_tool_matched_query_result(self, index_type, query_type, attribute, value, conditions, size=SIZE):
        and_dict = {}
        or_dict = {}
        and_dict['must'] = {}
        or_dict['should'] = {}
        main_dict = {}
        main_list = []
        final_list = []
        final_dict = {}
        final_dict['bool'] = {}

        for j in range(len(attribute)):
            dict = {}
            dict[attribute[j]] = value[j]
            main_list.append(dict)

        for k in main_list:
            main_dict['match'] = k
            final_list.append(main_dict)
            main_dict = {}

        and_list = []
        or_list = []
        count = 0

        if conditions[count] == 'and':
            and_list.append(final_list[0])
        if conditions[count] == 'or':
            or_list.append(final_list[0])

        for x in range(len(final_list)):
            if count < len(conditions):
                if conditions[count] == 'and':
                    and_list.append(final_list[x + 1])
                    count += 1
                    if count < len(conditions):
                        if conditions[count] == 'or':
                            or_list.append(final_list[x + 1])
                            count += 1

        and_dict['must'] = and_list
        or_dict['should'] = or_list

        final_dict['bool'] = and_dict
        final_dict['bool']['should'] = or_list

        print(final_dict)

        try:
            res = self.es.search(
                index=index_type,
                doc_type=query_type,
                body={
                    "query": final_dict,
                    "size": size
                }

            )

            return res

        except Exception as error:
            return error

    # ------------------------ Rapideye API Queries ---------------------
    #
    # def facebook_linkedin_investigation_query(self, index, attribute, value):
    #     names_list = []
    #     check_in_list = []
    #     contact_information_list = []
    #     investigation_response = {}
    #     try:
    #         name_res = self.es.search(
    #             index=[index + '_profile_profile_information', 'facebook_profile_check_ins'],
    #             body={
    #                 "query": {
    #                     "match": {
    #                         'GTR': value
    #                     },
    #                 },
    #             },
    #         )
    #         for i in name_res['hits']['hits']:
    #             names_list.append(i['_source'])
    #
    #         checkin_res = self.es.search(
    #             index=index + '_profile_check_ins',
    #             body={
    #                 "query": {
    #                     "match": {
    #                         attribute: value
    #                     }
    #                 }
    #             }
    #         )
    #         for i in checkin_res['hits']['hits']:
    #             check_in_list.append(i['_source'])
    #
    #         contact_information_res = self.es.search(
    #             index=index + '_profile_contact_information',
    #             body={
    #                 "query": {
    #                     "match": {
    #                         attribute: value
    #                     }
    #                 }
    #             }
    #         )
    #         for i in contact_information_res['hits']['hits']:
    #             contact_information_list.append(i['_source'])
    #         investigation_response['investigation_response'] = names_list
    #         print("-----", investigation_response)
    #         investigation_response.update({'investigation_response': contact_information_list})
    #         investigation_response.update({'investigation_response': check_in_list})
    #         investigation_response['investigation_response'] = contact_information_list
    #         print(investigation_response)
    #         return investigation_response
    #     except Exception as error:
    #         print(error)

    # ----------------------------- Rapideye API Queries ---------------------

    def create_mapping(self):
        try:
            mapping = {
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 1
                },
                "mappings": {
                    "properties": {
                        "case_id": {
                            "type": "long"
                        },
                        "case_description": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        },
                        "case_map": {
                            "properties": {
                                "created_on": {
                                    "type": "date"
                                },
                                "id": {
                                    "type": "long"
                                },
                                "location": {
                                    "type": "long"
                                },
                                "map_name": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256
                                        }
                                    }
                                },
                                "shapes": {
                                    "properties": {
                                        "dataArray": {
                                            "properties": {
                                                "lat": {
                                                    "type": "float"
                                                },
                                                "lng": {
                                                    "type": "float"
                                                },
                                                "info": {
                                                    "type": "text"
                                                },
                                                "type": {
                                                    "type": "text"
                                                },
                                                "layerno": {
                                                    "type": "long"
                                                },
                                                "layername": {
                                                    "type": "text"
                                                },
                                                "shape_id": {
                                                    "type": "long"
                                                },
                                                "cords": {
                                                    "properties": {
                                                        "lat": {
                                                            "type": "float"
                                                        },
                                                        "lng": {
                                                            "type": "float"
                                                        }
                                                    }
                                                },
                                                "rad": {
                                                    "type": "long"
                                                }
                                            }
                                        }
                                    }
                                },
                                "updated_on": {
                                    "type": "date"
                                }
                            }
                        },
                        "case_number": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        },
                        "case_priority": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        },
                        "case_state": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        },
                        "case_title": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        },
                        "case_type": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        },
                        "created_on": {
                            "type": "date"
                        },
                        "expire_on": {
                            "type": "date"
                        },
                        "id": {
                            "type": "long"
                        },
                        "incident_datetime": {
                            "type": "date"
                        },
                        "investigators": {
                            "properties": {
                                "cnic": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256
                                        }
                                    }
                                },
                                "email": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256
                                        }
                                    }
                                },
                                "employee_id": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256
                                        }
                                    }
                                },
                                "first_name": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256
                                        }
                                    }
                                },
                                "id": {
                                    "type": "long"
                                },
                                "image_url": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256
                                        }
                                    }
                                },
                                "investigator_type": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256
                                        }
                                    }
                                },
                                "last_name": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256
                                        }
                                    }
                                },
                                "phone": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256
                                        }
                                    }
                                },
                                "user": {
                                    "type": "long"
                                }
                            }
                        },
                        "is_enabled": {
                            "type": "boolean"
                        },
                        "is_expired": {
                            "type": "boolean"
                        },
                        "locations": {
                            "properties": {
                                "id": {
                                    "type": "long"
                                },
                                "latitude": {
                                    "type": "float"
                                },
                                "longitude": {
                                    "type": "float"
                                }
                            }
                        },
                        "people": {
                            "properties": {
                                "accent": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256
                                        }
                                    }
                                },
                                "can_read": {
                                    "type": "boolean"
                                },
                                "can_speak": {
                                    "type": "boolean"
                                },
                                "can_write": {
                                    "type": "boolean"
                                },
                                "category": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256
                                        }
                                    }
                                },
                                "cnic": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256
                                        }
                                    }
                                },
                                "description": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256
                                        }
                                    }
                                },
                                "email": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256
                                        }
                                    }
                                },
                                "first_name": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256
                                        }
                                    }
                                },
                                "fluency": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256
                                        }
                                    }
                                },
                                "gender": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256
                                        }
                                    }
                                },
                                "id": {
                                    "type": "long"
                                },
                                "language": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256
                                        }
                                    }
                                },
                                "last_name": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256
                                        }
                                    }
                                },
                                "phone": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256
                                        }
                                    }
                                },
                                "picture": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256
                                        }
                                    }
                                }
                            }
                        },
                        "updated_on": {
                            "type": "date"
                        },
                        "user": {
                            "type": "long"
                        }
                    }
                }
            }
            index_string = 'case_management'
            response = self.es.indices.create(
                index=index_string,
                body=mapping,
                ignore=400  # ignore 400 already exists code
            )
            print(response)
        except Exception as Ex:
            import trace
            print("here", Ex)
            pass

    def save_document(self, json_file, index_string, unique_identity):
        try:
            response = self.es.index(index=index_string, id=unique_identity, body=json_file)
            print(response)
        except Exception as Ex:
            status_es = self.es.cluster.health(wait_for_status='yellow', request_timeout=1)
            import trace
            print('status es', status_es)
            print("Error while saving Doc", Ex)
            pass

    def delete_document(self, index, gtr):
        try:
            response = self.es.delete_by_query(
                index=index,
                body={
                    "query": {
                        "match": {
                            'GTR': gtr
                        }
                    }
                }
            )
            print(response)
            return True
        except Exception as Ex:
            status_es = self.es.cluster.health(wait_for_status='yellow', request_timeout=1)
            import trace
            print('status es', status_es)
            print("Error while saving Doc", Ex)
            return False

    def delete_ml_model(self, index, name):
        try:
            response = self.es.delete_by_query(
                index=index,
                body={
                    "query": {
                        "match": {
                            'name': name
                        }
                    }
                }
            )
            print(response)
            return True
        except Exception as Ex:
            status_es = self.es.cluster.health(wait_for_status='yellow', request_timeout=1)
            import trace
            print('status es', status_es)
            print("Error while saving Doc", Ex)
            return False

    def change_detection(self, gtr):
        all_response = []
        try:
            responses = self.es.search(
                index='*change_detection',
                body=
                {
                    "query": {
                        "match": {
                            "GTR": gtr
                        },
                    },
                    "size": SIZE,
                }
            )
            for response in responses['hits']['hits']:
                all_response.append(response['_source'])

            return all_response
        except Exception as error:
            return error

    def get_categorization_visual(self, from_date, to_date ,output_format=["GTR", "created_on", "posts.url_c", "url",
                                                             "categorization.predictions", "categorization.confidence"]):
        fields = ["*"]
        data = {
          "query": {
           "bool":{
             "must": [
                # {"match": { "categorization.predictions": { "query": category } } },
                # {"match": { "created_on": { "query": date } }},
                # {"exists": {"field": "categorization.predictions"}}
                 {"exists": {"field": "categorization.predictions"}},
                 {"range": {"created_on": {"gte": from_date, "lte": to_date}}}
             ]
           }
          },
          "fields":output_format,
          "_source": True,
          "size":"10000",
          "sort":{ "_score":{"order":"desc" } }
          }

        data["highlight"] = {"order": "score", "pre_tags": [""], "post_tags": [""], "fields": {"*": {}}}
        headers = {
            "Content-Type": "application/json",
        }

        url = 'http://{ip}:{port}/'.format(ip=self.cluster_ip, port=self.port)
        print('-------------------------------------', url)
        response = requests.get(
            # "http://192.168.18.155:9200/twitter*,facebook*,linkedin*,news*,reddit*,instagram*,youtube*,keybase*,trends*,rss*/_search",
        url + "twitter*,facebook*,linkedin*,news*,reddit*,instagram*,youtube*,keybase*,generic_crawler*,trends*,rss*/_search",
        headers=headers,
        data=json.dumps(data)
        )

        print('response recieved')
        results = []
        try:
            for highlight in json.loads(response.content)['hits']['hits']:
                to_return = {}

                to_return['_id'] = highlight.get('_id', None)
                to_return['_index'] = highlight.get('_index', None)
                to_return['GTR'] = highlight.get('_source', {}).get('GTR', None)
                to_return['target_type'] = highlight.get('_source', {}).get('target_type', None)
                to_return['target_subtype'] = highlight.get('_source', {}).get('target_subtype', None)
                #to_return['highlight'] = highlight.get('highlight', None)
                to_return['fields'] = highlight.get('fields', None)
                results.append(to_return)
        except:
            print("response missing!")

        # print(json.dumps(results, indent=5))
        # res= json.dumps(results, indent=5)
        return results

# obj = ElasticsearchHandler()
# # obj.get_response_by_gtr(index='twitter_profile_posts', gtr_id='st_tw_58', limit=1000)
# obj.delete_document()

# obj.get_response_by_gtr('facebook_profile_posts', 'st_fb_291')

    def rapideye_fetched_data(self, index, attributes, values):
        response_list = []
        main_list = []
        final_list = []
        main_dict = {}
        final_dict = {}
        index = index+'*profile_information'
        for a in range(len(attributes)):
            dict = {}
            dict[attributes[a]+".keyword"] = values[a]
            main_list.append(dict)

        for k in main_list:
            main_dict['match'] = k
            final_list.append(main_dict)
            main_dict = {}
        final_dict['must'] = final_list

        responses = self.es.search(
            index=index,
            body={
                "query": {
                    "bool": final_dict
                },
                'size': SIZE
            },
        )
        for response in responses['hits']['hits']:
            response_list.append(response['_source'])

        # toset = set(response_list)
        # response_list = list(toset)

        return response_list

    def es_response_count(self, index_name):

        index_name =  index_name+'*profile_information'
        res = requests.get("http://{ip}:{port}/{index}/_count?q=_id:*".format(ip=self.cluster_ip, port=self.port,
                                                                              index=index_name))
        return res.json()['count']

    def delete_by_gtr(self, gtr):
        try:
            response = self.es.delete_by_query(
                index='*',
                body={
                    "query": {
                        "match": {
                            'GTR': gtr
                        }
                    }
                }
            )
        except Exception as Ex:
            return Ex

        return True

    def full_text_search(self, keyword, index, field):
        res = self.es.search(
            index=index,
            body={
                "query": {
                    "match": {
                        field: keyword
                    }
                }
            }
        )
        return res

    def search(self, query, index_prefix):
        response = requests.get(
            'http://{ip}:{port}/'.format(ip=self.cluster_ip, port=self.port) + index_prefix + "*/_search",
            headers=headers,
            data=json.dumps(query)
        )
        return response

    def get_GTR_per_platform(self, platform):
        GTRs = {"instagram": "st_in",
                "facebook": "st_fb",
                "linkedin": "st_li",
                "reddit": "st_rd"}
        try:
            platform_gtr = GTRs[platform]
            return platform_gtr
        except:
            return None

    def get_gtrs_in_case(self, platform, case_id):
        query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "wildcard": {
                                "linked_data.GTR": {
                                    "value": str(platform) + "*",
                                    "boost": 1.0,
                                    "rewrite": "constant_score"
                                }
                            }

                        },
                        {
                            "match": {
                                "case_id": case_id
                            }
                        }

                    ]
                }
            }
        }

        query["_source"] = False
        query['size'] = "10000"
        query['sort'] = {"_score": {"order": "desc"}}
        query['fields'] = ["linked_data.GTR", "linked_data.user_names"]
        # query["highlight"] = {"order": "score", "fields": {"linked_data.GTR": {}}}
        response = self.search(query, "case")
        # results= json.loads(response.content)
        # response = search(query)
        results = []
        case_targets_detail = {}
        print('')
        for result in json.loads(response.content)['hits']['hits']:
            linked_data_gtr = result['fields']['linked_data.GTR']
            linked_data_usernames = result['fields']['linked_data.user_names']
            for key, value in zip(linked_data_usernames, linked_data_gtr):
                if value not in ["", "null", None] and value.startswith(platform):
                    case_targets_detail[value] = key
                    results.append(value)
        return case_targets_detail
        # return results
    
    def update_categorization(self , GTR, post_id,new_categorization):
        """         Function which updates the categorization       """
        new_confidence=[]
        if(len(new_categorization)!=0):
            for each in new_categorization:
                new_confidence.append("0.99")
        gmt = time.gmtime()
        ts = calendar.timegm(gmt)
        bdy={
            "query": {
                "bool": {
                    "must": [
                        {"match": {'GTR': GTR}},
                        {"match": {'posts.id': post_id}}
                            ]
                        }
            },
            "script": {
            "source": "ctx._source.categorization = params.updatedc",
            "lang": 'painless',
            "params": {
                "updatedc": {"confidence":new_confidence, "predictions":new_categorization, "is_edited":True, "edited_on":ts*1000}
            }
            }
        }
        response = self.es.update_by_query(body=bdy, index="*posts")
        return response

    def get_all_ml_models(self):
        query = {
            "query":{
                "bool":{
                "must":[
                    {
                        "match_all":{}
                    }
                ]
                }
            },
            "sort" : [
              {"created_on" : {"order" : "desc"}}
            ]

        }
        response = self.es.search(query,"ml_models")['hits']['hits']
        response = list(map(lambda x: x['_source'],response))
        for i in response:
            if 'evaluation' in i:
                i['evaluations'] = i['evaluation']
                del i['evaluation']

        return response


    def get_ml_model(self,model_name,_type):
        get_new_model = {

            "query":{
                "bool":{
                "must":[
                    {
                        "match":{
                            "name":model_name
                        }
                    }
                ]}
            },
            "sort":[{"_score":{"order":"desc"}}]
                
        }
        
        
        get_active_model = {
            "query": {
                "bool": {
                "must": [
                    {
                    "match": {
                        "state": True
                    }
                    },
                    {
                    
                    "match": {
                        "type": _type
                    }
                    }
                ]
                }
            },
            "size":1
            }

        get_default_model = {
            "query": {
                "bool": {
                "must": [
                    {
                    "match": {
                        "subtype": "default"
                    }
                    },
                    {
                    
                    "match": {
                        "type": _type
                    }
                    }
                ]
                }
            },
            "size":1
            }



        def reFormatEval(response):
            response = list(map(lambda x: x['_source'],response))[0]
            if 'evaluation' in response:
                response['evaluations'] = response['evaluation']
                del response['evaluation']
            return response
        
        response = self.es.search(get_new_model,"ml_models")['hits']['hits']
        response = reFormatEval(response)

        active_model_response = self.es.search(get_active_model,"ml_models")['hits']['hits']
        # if active_model_response:
        
        try:
            active_model_response = reFormatEval(active_model_response)
            response["evaluations"]["old_model"] = active_model_response['evaluations']['new_model']
        except:
            default_model_response = self.es.search(get_default_model,"ml_models")['hits']['hits']
            default_model_response = reFormatEval(default_model_response)

            response["evaluations"]["old_model"] = default_model_response['evaluations']['new_model']


        return response


    # RESET MODEL STATE & DEPLOY
    def deploy_model(self,model_name):
        Q_reset_state = {
            "script":"ctx._source.state = false"
        }
        deploy_new_model = {    
            "query":{
                        
                    "match_phrase":{
                        "name":model_name                       
            
                    }
            },
            "script": {
            "source": "ctx._source.state = true",
            "lang": "painless"
            }
        }
        self.es.update_by_query("ml_models",body=Q_reset_state,conflicts="proceed",refresh=True)
        self.es.indices.refresh(index="ml_models")
        self.es.update_by_query("ml_models",body=deploy_new_model,conflicts="proceed",refresh=True)
        self.es.indices.refresh(index="ml_models")
        return self.get_all_ml_models()

    def discard_model(self,model_name):
        # Q_reset_state = {
        #     "script":"ctx._source.state = true"
        # }
        deploy_new_model = {    
            "query":{
                        
                    "match_phrase":{
                        "name":model_name                       
            
                    }
            },
            "script": {
            "source": "ctx._source.state = false",
            "lang": "painless"
            }
        }
        # self.es.update_by_query("ml_models",body=Q_reset_state,conflicts="proceed",refresh=True)
        # self.es.indices.refresh(index="ml_models")
        self.es.update_by_query("ml_models",body=deploy_new_model,conflicts="proceed",refresh=True)
        self.es.indices.refresh(index="ml_models")
        return self.get_all_ml_models()


    def update_sentiment(self , GTR, post_id,new_categorization):
        """         Function which update_sentiment      """
        new_confidence=[]
        if(len(new_categorization)!=0):
            for each in new_categorization:
                new_confidence.append("0.99")
        gmt = time.gmtime()
        ts = calendar.timegm(gmt)
        bdy={
            "query": {
                "bool": {
                    "must": [
                        {"match": {'GTR': GTR}},
                        {"match": {'posts.id': post_id}}
                            ]
                        }
            },
            "script": {
            "source": "ctx._source.sentiment = params.updatedc",
            "lang": 'painless',
            "params": {
                "updatedc": {"confidence":new_confidence, "predictions":new_categorization, "is_edited":True, "edited_on":ts*1000}
            }
            }
        }
        response = self.es.update_by_query(body=bdy, index="*posts")
        return response

    def update_additional_post_comment(self, gtr, post_id, comment, commenter_name):
        if(len(comment)!=0):
            gmt = time.gmtime()
            ts = calendar.timegm(gmt)
            bdy={
                "query": {
                    "bool": {
                        "must": [
                            {"match": {'GTR': gtr}},
                            {"match": {'posts.id': post_id}}
                                ]
                            }
                },
                "script": {
                "source": "if(ctx._source.posts.containsKey('additional_enduser_comments')) {ctx._source.posts.additional_enduser_comments.add(params.updatedv)} else {ctx._source.posts.additional_enduser_comments=params.updatedc}",
                "lang": 'painless',
                "params": {
                    "updatedc": [{"comment": comment, "commenter": commenter_name, "created_on": ts * 1000}],
                    "updatedv": {"comment": comment, "commenter": commenter_name, "created_on": ts * 1000}
                }
                }
            }
            response = self.es.update_by_query(body=bdy, index="*posts")
            return response

    def get_twitter_top_ten_user(self, GTR):

        def CountFrequency(my_list):
            freq = {}
            for item in my_list:
                if (item in freq):
                    freq[item] += 1
                else:
                    freq[item] = 1

            # for key, value in freq.items():
            #     print("% s : % d" % (key, value))
            return freq

        element = GTR.split('_')[1]
        print("element==",element)

        if (element == "tw"):
            platform = 'twitter_profile_posts'
            profile = 'twitter_profile_profile_information'
        elif (element == "fb"):
            platform = 'facebook_profile_posts'
            profile = 'facebook_profile_profile_information'
        elif (element == "ln" or element == "li"):
            platform = 'linkedin_profile_posts'
            profile = 'linkedin_profile_profile_information'
        elif (element == "in"):
            platform = 'instagram_profile_posts'
            profile = 'instagram_profile_profile_information'
        elif (element == "rd"):
            platform = 'reddit_profile_posts'
            profile = 'reddit_profile_profile_information'
        elif (element == "yt"):
            platform = 'youtube_channel_posts'
            profile = 'youtube_channel_profile_information'
        try:
            res = self.es.search(index=platform, body={"query": {"match": {"GTR": GTR}}},size=10000)
        except:
            print("not present post table")
        try:
            res_profile = self.es.search(index=profile, body={"query": {"match": {"GTR": GTR}}}, size=1)
        except:
            print('username is not present in the profile table')
            
        most_influential = []
        user_list=[]
        image_dictionary=[]
        for hit in res_profile['hits']['hits']:
            try:
                pro_username=(hit['_source']['username'])
            except:
                print("username is not present in the table")
                pro_username=''
                pass
            try:
                pro_name=(hit['_source']['name'])
                pro_name=''
            except:
                print('name is not present in the list')
                pass
            # print(pro_name,pro_username)



        for hit in res['hits']['hits']:
                try:
                    if(hit['_source']['posts']['author']['username']==pro_username or hit['_source']['posts']['author']['username']==""):
                        pass
                    else:
                        user_list.append(hit['_source']['posts']['author']['username'])
                        image_dictionary.append({"username":hit['_source']['posts']['author']['username'],"image":hit['_source']['posts']['author']['image']})
                except:
                    print("fields are not correctly spelled or present in the author section")
                    break


        for hit in res['hits']['hits']:
            # print(hit['_source']['posts']['comments'])
            try:
                for i in hit['_source']['posts']['comments']:
                    if(i['commenter']['username']==pro_username or i['commenter']['username']==""):
                        pass
                    else:
                        user_list.append(i['commenter']['username'])
                        image_dictionary.append({"username":i['commenter']['username'],"image":i['commenter']['image']})
            except:
                print("fields are not correctly spelled or present in the comments section")
                break
        for hit in res['hits']['hits']:
            try:
                for i in hit['_source']['posts']['reactions']['like']:
                    if (i['username'] == pro_username or i['username']==""):
                        pass
                    else:
                        user_list.append(i['username'])
                        image_dictionary.append({"username": i['username'],
                                            "image": i['image']})
            except:
                print("fields are not correctly spelled or present in the comments section")
                break
        # print(user_list)
        # print("images\n"+str(image_dictionary))
        temp=CountFrequency(user_list)
        # print(temp)
        top_10_influencers = dict(sorted(temp.items(), key=itemgetter(1), reverse=True)[:10])
        # print("top10Influencers\n"+str(top_10_influencers))
        for key,value in top_10_influencers.items():
            for i in image_dictionary:
                if(key==pro_username):
                    break
                if i['username']==key:
                    most_influential.append({"username":key,"image":i["image"],"count":value})
                    break

        return most_influential
        # for i in most_influential:
        #     print(i)


    #     def CountFrequency(my_list):
    #         freq = {}
    #         for item in my_list:
    #             if (item in freq):
    #                 freq[item] += 1
    #             else:
    #                 freq[item] = 1
    #         return freq
    # # for key, value in freq.items():
    # #     print("% s : % d" % (key, value))
    
    #     # input = input("Enter your GTR")
    #     element = GTR.split('_')[1]
    #     if (element != -1):
    #         platform = 'twitter_profile_posts'
    #     elif (element != -1):
    #         platform = 'facebook_profile_posts'
    #     elif (element != -1 or element != -1):
    #         platform = 'linkedin_profile_posts'
    #     elif (element != -1):
    #         platform = 'instagram_profile_posts'
    #     elif (element != -1):
    #         platform = 'reddit_profile_posts'
    #     elif (element!= -1):
    #         platform = 'youtube_channel_posts'
    #     res = self.es.search(index=platform, body={"query": {"match": {"GTR": GTR}}})
    #     # res = self.es.search(index="twitter_profile_posts", body={"query": {"match": {"GTR": GTR}}})


    #     username_list = []
    #     top_user = {}
    #     #Top Author
    #     for hit in res['hits']['hits']:
    #         username_list.append(hit['_source']['posts']['author']['username'])
    #     temp= CountFrequency(username_list)
    #     temp = dict(sorted(temp.items(), key=itemgetter(1), reverse=True)[:10])
    #     top_10_authors = [{"name":key, "value":value} for key, value in temp.items()]
    #     top_user['top_10_authors']= top_10_authors
    #     #Top Commentator
    #     commentator_list=[]
    #     for hit in res['hits']['hits']:
    #         # print(hit['_source']['posts']['comments'])
    #         for i in hit['_source']['posts']['comments']:
    #             commentator_list.append(i['commenter']['username'])
    #     temp1= CountFrequency(commentator_list)
    #     # top_10_commentators = dict(sorted(temp1.items(), key=itemgetter(1), reverse=True)[:10])
    #     temp1 = dict(sorted(temp1.items(), key=itemgetter(1), reverse=True)[:10])
    #     top_10_commentators = [{"name":key, "value":value} for key, value in temp1.items()]
    #     top_user['top_10_commentators']= top_10_commentators


    #     #Top Likers
    #     likers_list=[]
    #     for hit in res['hits']['hits']:
    #         for i in hit['_source']['posts']['reactions']['like']:
    #             likers_list.append(i['username'])
    #     temp2 = CountFrequency(likers_list)
    #     # top_10_likers = dict(sorted(temp2.items(), key=itemgetter(1), reverse=True)[:10])
  
    #     temp2 = dict(sorted(temp2.items(), key=itemgetter(1), reverse=True)[:10])
    #     top_10_likers = [{"name":key, "value":value} for key, value in temp2.items()]
    #     top_user['top_10_likers']= top_10_likers
    #     return top_user

    def get_top_ten_domain_name(self, GTR):
        # re_string="(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]"
        re_string="((?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,3}(?![a-zA-Z0-9]))"
        re_test='#'
        temp=[]
        store=[]

        def CountFrequency(my_list):
            freq = {}
            for item in my_list:
                if (item in freq):
                    freq[item] += 1
                else:
                    freq[item] = 1

            # for key, value in freq.items():
            #     print("% s : % d" % (key, value))
            return freq
        element = GTR.split('_')[1]
        if(element=="tw"):
            platform='twitter_profile_posts'
        elif (element=="fb"):
            platform = 'facebook_profile_posts'
        elif (element=="li" or element=="ln"):
            platform = 'linkedin_profile_posts'
        elif (element=="in"):
            platform = 'instagram_profile_posts'
        elif (element=="rd"):
            platform = 'reddit_profile_posts'
        elif (element=="yt"):
            platform = 'youtube_channel_posts'

        res = self.es.search(index=platform, body={"query": {"match": {"GTR": GTR}}}, size=10000)

        for hit in res['hits']['hits']:
            #print((hit['_source']['posts']['text_c']))
            store.append(re.findall(re_string,hit['_source']['posts']['text_c']))
            print(hit['_source']['posts']['text_c'])
        print(store)
        list_of_domain=[]
        for item in store:
            for i in item:
                if(i):
                    list_of_domain.append(i)
                else:
                    pass
        list_of_domain_count=CountFrequency(list_of_domain)
        print(list_of_domain_count)
        top_domains_shared = dict(sorted(list_of_domain_count.items(), key=itemgetter(1), reverse=True)[:10]) #For Top 10

        top_domain_names = [{"category":key, "value":values  }for key, values in top_domains_shared.items() ]
        # print(top_domains_shared)

        return top_domain_names
            
    def close_associates(self,GTR ,CTR , target_type, target_subtype):
    
        def get_username(GTR):
            
            response =self.es.search(index="{0}_{1}_target_information*".format(target_type,target_subtype),body={"query":{"match":{"GTR":str(GTR)}}},size=10000)
            response = response['hits']['hits']

            if len(response) > 0:
                return response[0]["_source"]["username"].lower()
            else:
                raise Exception("User Doesnot Exists")

        def clean_username(username):
            return re.sub("@","",username.lower())

        def remove_symbol(usernames):
            users = []
            current_username = get_username(GTR)
            print(current_username)
            filter_usernames = ["l.php",current_username,"photo","hashtag"]
            def wrapper(*args, **kwargs):
                for username in usernames(*args, **kwargs):
                    _ = clean_username(username)
                    if _:
                        if _ not in filter_usernames:
                            users.append(_)
                return users
            return wrapper


        def get_posts_data(GTR=None):
            
            response =self.es.search(
            index="{0}_{1}_posts*".format(target_type,target_subtype),
            body = {
            "query":{
                "match":{
                    "GTR":str(GTR)
                }

                }},
                size=10000
            )
            return response['hits']['hits']



        # Get Friends Data
        def get_friends_data(GTR=None):
            response =self.es.search(
            index="{0}_{1}_friends*".format(target_type,target_subtype),
            body = {
            "query":{
                "match":{
                    "GTR":str(GTR)
                }

                } },
                size=10000
                )
            return response["hits"]["hits"]


        # Get Followers Data
        def get_followers_data(GTR=None):
            response =self.es.search(
            index="{0}_{1}_follower*".format(target_type,target_subtype),
            body = {
            "query":{
                "match":{
                    "GTR":str(GTR)
                }

                }},
                size=10000
            ) 
            
            return response["hits"]["hits"]

        # Get Followers Data

        def get_followings_data(GTR=None):
            response =self.es.search(
            index="{0}_{1}_following*".format(target_type,target_subtype),
            body = {
            "query":{
                "match":{
                    "GTR":str(GTR)
                }

            }},
                size=10000
                )

            return response["hits"]["hits"]

        # Get username of persons who commented
        @remove_symbol
        def get_commenters_username(posts):
            usernames = []
            for post in posts.get("comments",[]):
                usernames.append(post['commenter']['username'])
            print("get_commenters_username")
            print(usernames)
            return usernames

        # Get username of persons replied to comments
        @remove_symbol
        def get_comments_reply_to(posts):
            usernames = []
            for post in posts.get("comments",[]):
                if post.get("reply_to",False):
                    repliers = re.findall("@\w+",post['reply_to'])
                    usernames = usernames + repliers
            return usernames

        # Get username of persons who reacted
        @remove_symbol
        def get_reactions(posts):
            usernames = []
            reaction_types = ["like","appreciation","empathy","interest","maybe","praise"]
            for reaction_type in reaction_types:
                for post in posts.get("reactions",{}).get(reaction_type,[]):
                    usernames.append(post['username'])
            return usernames


        # Get username of persons who the current user mentioned in posts
        @remove_symbol
        def get_post_mentions(posts):
            usernames = re.findall("\@w+",posts["text_c"])
            return usernames

        # Get username of persons who was mentioned in comments

        @remove_symbol
        def get_comments_post_mention(posts):
            usernames = []
            for post in posts.get("comments",[]):
                repliers = re.findall("@\w+",post['text'])
                usernames = usernames + repliers        
            return usernames

        # Get username of person who are friends

        @remove_symbol
        def get_friends(friends):
            usernames = []
            for username in friends:
                usernames.append(username["_source"]['username'])
            return usernames

        # Get username of person who are followers

        @remove_symbol
        def get_followers(followers):
            usernames = []
            for username in followers:
                username = username["_source"]
                if username.get("followers",False):
                    usernames.append(username["followers"]['username_c'])
                else:
                    usernames.append(username['username_c'])
            return usernames

        # Get username of person who the current user is following
        @remove_symbol
        def get_followings(following):
            usernames = []
            for username in following:
                username = username["_source"]
                if username.get("following",False):
                    usernames.append(username["following"]['username_c'])
                else:
                    usernames.append(username['username_c'])
            return usernames

        print(">> Reading Data")
        posts_data = get_posts_data(GTR)
        
        friends_data = get_friends_data(GTR)
        followers_data = get_followers_data(GTR)
        followings_data = get_followings_data(GTR)
        # print(json.dumps(data,indent=4))
        print(">> Data Read")
        print('-------->printttt')
        



        commenters = []
        comment_repliers = []
        reactions = []
        posts_mentions = []
        comments_posts_mentions = []
        friends = []
        followers = []
        followings = []

        # Extracting Posts Related Data

        for datum in posts_data:
            datum = datum['_source']["posts"]
            commenters = commenters + get_commenters_username(datum)
            comment_repliers = comment_repliers + get_comments_reply_to(datum)
            reactions = reactions + get_reactions(datum)
            posts_mentions = posts_mentions + get_post_mentions(datum)
            comments_posts_mentions = comments_posts_mentions + get_comments_post_mention(datum)

        # Extracting Miscs Data

        friends = get_friends(friends_data)
        followers = get_followers(followers_data)
        followings = get_followings(followings_data)

        weights = {
            "commenters":6,
            "comment_repliers":6,
            "posts_mentions":12,
            "reactions":3,
            "comments_replies":5,
            "comments_posts_mentions":8,
            "friends":8,
            "followers":4,
            "followings":10
        }


        _weights = weights.values()
        total = sum(_weights)
        print(total)
        for key,value in weights.items():
            weights[key] = value / total

        print(weights)

        max_pad = 0

        associates = {
            "commenters":commenters,
            "comment_repliers":comment_repliers,
            "reactions":reactions,
            "posts_mentions": posts_mentions,
            "comments_posts_mentions":comments_posts_mentions,
            "friends":friends,
            "followers":followers,
            "followings":followings
        }
        print()
        print("FRIENDS")
        print()
        print(associates["friends"])
        print()
        print()

        associates_meta_mapping = {
            "commenters":"posts",
            "comment_repliers":"posts",
            "reactions":"posts",
            "posts_mentions": "posts",
            "comments_posts_mentions":"posts",
            "friends":"friends",
            "followers":"followers",
            "followings":"followings"
            
        }


        print(associates_meta_mapping)
        print("BEFORE META")
        """
        META DATA
        """

        def get_meta(username,_type):
            mapped_type = associates_meta_mapping[_type]
            response =self.es.search(
            index="{0}_{1}_{2}".format(target_type,target_subtype,mapped_type),
            body = {
            "query":{
                "match":{
                    "GTR":str(GTR)
                }
            }},
                size=10000
                )
            
            response = response["hits"]["hits"]
            meta = {
                "GTR":GTR,
                "CTR":CTR,
                "target_type":target_type,
                "target_subtype":target_subtype,
                "entity_type":"users",
                "type":_type,
                "score":0,
                "image":"",
                "url":"",
                "username":""
            }
            meta['username'] = username
            meta['name'] = username
            if mapped_type == "posts":
                for datum in posts_data:
                    post = datum['_source']["posts"]
                    if _type == "commenters":
                        for _comments in post.get("comments",[]):
                            if _comments.get("commenter",False):
                                if clean_username(_comments["commenter"]['username']) == username:
                                    meta["image"] = _comments["commenter"]["image"]
                                    meta["url"] = _comments["commenter"]["url"]
                    elif _type == "reactions":
                        if post.get("reactions",False):
                            for key,value in post["reactions"].items():
                                for reacts in post["reactions"][key]:
                                    if reacts.get("username",False):
                                        if clean_username(reacts["username"]) == username:
                                            meta["image"] = reacts["image"]
                                            meta["url"] = reacts["url"]
                                            
                    elif _type == "comment_repliers" or _type == "posts_mentions" or _type == "posts_mentions":
                        response =self.es.search(
                        index="{0}_{1}_target_information*".format(target_type,target_subtype),
                        body = {
                        "query":{
                            "match":{
                                "username":str(username)
                            }
                        }},
                            size=1
                        )
                        response = response["hits"]
                        for _ in response:
                            _ = _["source"]
                            meta["image"]    = _["image"]
                            meta["url"]      = _["profile_url"]
                            
                    elif _type == "friends":
                        response =self.es.search(
                        index="{0}_{1}_friends*".format(target_type,target_subtype),
                        body = {
                        "query":{
                            "match":{
                                "username":str(username)
                            }
                        }},
                            size=1
                            )
            
                        response = response["hits"]["hits"]
                        meta["username"] = username
                        for _ in response:
                            _ = _["source"]
                            meta["image"]    = _["image"]
                            meta["url"]      = _["url"]
                            
                    elif _type == "followers":
                            response =self.es.search(
                            index="{0}_{1}_followers*".format(target_type,target_subtype),
                            body = {
                            "query":{
                                "match":{
                                    "username":str(username)
                                }
                            }},
                                size=1
                                )
                            
                            response = response["hits"]["hits"]
                            meta["username"] = username
                            for _ in response:
                                _ = _["source"]
                                meta["image"]    = _["image_c"]
                                meta["url"]      = _["url_c"]
                                
                    elif _type == "following":
                        response =self.es.search(
                        index="{0}_{1}_following*".format(target_type,target_subtype),
                        body = {
                        "query":{
                            "match":{
                                "username":str(username)
                            }
                            } },
                            size=10000
                            )
                        response = response.json()["hits"]["hits"]
                        meta["username"] = username
                        for _ in response:
                            _ = _["source"]
                            if _.get("following",False):
                                meta["image"]    = _['following']["image_c"]
                                meta["url"]      = _['following']["url_c"]
                                meta["username"] = _['following']["username_c"] if _['following']["username_c"] else username
                            elif _.get("username_c",False):
                                meta["image"]    = _["image_c"]
                                meta["url"]      = _["url_c"]
                                meta["username"] = _["username_c"] if _["username_c"] else username
            return meta
                    



        def compute(associates):
            user_scores = {}
            for key,value in associates.items():
                
                for username in associates[key]:
                    if not user_scores.get(username,False):
                        user_scores[username] = {}
                    if not user_scores[username].get(key,False):
                        user_scores[username][key] = 0

                for username in associates[key]:
                    user_scores[username][key] = user_scores[username][key] + weights[key]        
            return user_scores


        user_scores = compute(associates)
        total = 0
        for username,nest in user_scores.items():
            for key,value in nest.items():
                total = total + value
        print(total)
        for username,nest in user_scores.items():
            add_up = 0
            user_scores[username]["meta"] = {}
            for key in nest.copy():
                try:
                    if key != "meta":
                        nest[key] = float(nest[key])
                        add_up = add_up + nest[key]
                        user_scores[username]['meta'] = get_meta(username,key)
                except:
                    pass
            user_scores[username]['meta']["score"] = (add_up / total)

        user_scores = sorted(user_scores.items(), key= lambda x:x[1]["meta"]['score'],reverse= True)[:20]
        optimal_response = []
        for _ in user_scores:
            optimal_response.append(_[1]["meta"])

        print(json.dumps(optimal_response,indent = 4))

        # headers = {
        #     "Content-Type":"application/json"
        # }
        # Saving Calculations in Elasticsearch
        
        for to_save in optimal_response:
            # response = requests.post(f"http://{node_ip}:{node_port}/{target_type}_{target_subtype}_close_associates/_doc",data=json.dumps(to_save),headers=headers)
            res = self.es.index(index="{0}_{1}_close_associates".format(target_type,target_subtype),body=to_save)
            print(res,'---------------------___>success')
        # return {
        #     "message":"success"
        # }

    def leaked_data_elastic(self,leaked_data_dict,target_type):
        try:
            res = self.es.index("{0}_leaked_data".format(target_type),body=leaked_data_dict)
            print(res,'------------__>success elastic')
        
        except Exception as e:
            print(e)
            pass

        return{
            'message':'success'
        }


    def leaked_data_get(self,index,phone="",email="",id=""):
        args = [phone,email,id]
        res = []
        try:
            res = self.es.search(
                index=index,
                body={
                    "query":{
                        "query_string":{
                            "query":" OR".join([val for val in args if val])
                        }
                    },
                "size": 100,    
                "sort":[{"_score":{"order":"desc"}}]
            })['hits']['hits']
            print(res)           
        except Exception as e:
            print(e)  
        return res


# obj = ElasticsearchHandler()
# #
# abc = obj.change_detection('linkedin', 'st_li_593')

# res = obj.es_response_count('twitter')
# import requests
#
# res = requests.get("http://192.168.18.155:9200/facebook*/_count?q=_id:*")
# print(res)
