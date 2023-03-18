from elasticsearch import Elasticsearch
import json
from OCS_Rest import settings
from datetime import date

SIZE = 10000


class ElasticsearchHandler(object):

    def __init__(self):
        self.es = None
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

    def get_response_by_type(self, index, document_type, channel, limit=20):
        try:
            actual_response = []
            responses = self.es.search(
                index=index,
                doc_type=document_type,
                body={
                    "query": {
                        "match": {
                            "Channel": channel
                        }
                    },
                    "size": limit
                }
            )
            for response in responses['hits']['hits']:
                actual_response.append(response['_source'])
            return actual_response
        except Exception as error:
            print(error)

    def get_twitter_trends(self, index, trend_type, country, created_on_gte, created_on_lte, limit=20):
        try:
            actual_response = []
            responses = self.es.search(
                index=index,
                doc_type=trend_type,
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

    def get_trends(self, index, trend_type, created_on_gte, created_on_lte, limit=20):
        try:
            actual_response = []
            print('created_on', created_on_gte * 1000)
            print('created_on', created_on_lte * 1000)
            responses = self.es.search(
                index=index,
                doc_type=trend_type,
                body={
                    "query": {
                        "range": {
                            "created_on": {
                                "gte": created_on_gte * 1000,
                                "lte": created_on_lte * 1000
                            }

                        }
                    },
                    "size": limit
                }
            )
            for response in responses['hits']['hits']:
                actual_response.append(response['_source'])
            return actual_response
        except Exception as error:
            print(error)

    def get_response_by_gtr(self, index, gtr_id, limit=20):
        all_responses = dict()

        try:
            responses = self.es.search(
                index=index,
                body={
                    "query": {
                        "match": {
                            "GTR": gtr_id
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
            return all_responses, count
        except Exception as error:
            return error

    def get_response_by_alpha_gtr(self, index, doc_type, alpha_gtr, limit=10000):
        all_responses = dict()

        try:
            responses = self.es.search(
                index=index,
                body={
                    "query": {
                        "match": {
                            "GTR": alpha_gtr
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

    def get_posts_by_gtr(self, index, gtr_id, limit=20):
        posts_list = []
        all_posts = {}
        all_posts['posts'] = {}
        try:
            responses = self.es.search(
                index=index,
                doc_type='posts',
                body={
                    "query": {
                        "match": {
                            "GTR": gtr_id
                        }
                    },
                    "size": limit
                }
            )
            for r in responses['hits']['hits']:
                posts_list.append(r['_source'])
            all_posts['posts'] = posts_list
            return all_posts
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

    def get_response_by_id_and_type(self, index, document_type, id, limit=20):
        try:

            res = self.es.search(
                index=index,
                doc_type=document_type,
                body={
                    "query": {
                        "match": {
                            '_id': id
                        },
                    },
                    "size": limit
                },
            )
            for i in res['hits']['hits']:
                print(i['_source'])
        except Exception as error:
            print(error)

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

# obj = ElasticsearchHandler()
# abc = obj.get_response_by_alpha_gtr(index='link_analysis', alpha_gtr='5fec15cdda0a01c6c00ef83a', limit=1000)
# print(abc)
