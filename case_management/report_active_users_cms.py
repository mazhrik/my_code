import requests
import json
from core_management.elasticsearch_handler_v2 import ElasticsearchHandler

es_obj = ElasticsearchHandler()


def get_report_content(gtrs):
    print("--------------------------------Case targets are--------------------------------")
    print(gtrs)
    print("--------------------------------------------------------------------------------")
    report_response={}
    for gtr, username in gtrs.items():
        posts_response=es_obj.full_text_search(gtr, "*posts", "GTR")
        total = posts_response['hits']['total']['value']
        report_response[username]=total

    #c = Counter(report_response)
    #most_active = c.most_common(5)
    return report_response

