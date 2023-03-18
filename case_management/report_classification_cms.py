import requests
import json
from collections import Counter
from core_management.elasticsearch_handler_v2 import ElasticsearchHandler

es_obj = ElasticsearchHandler()


def try_(gtrs_detail,category, platform):
    final_output={}
    should_clause=[]
    gtrs= list(gtrs_detail.keys())
    #gtrs=['st_in_815', 'st_in_940']
    if(len(gtrs)!=0):
        for gtr in gtrs:
            should_clause.append({"match":{"GTR":gtr}})
        output_format = ["GTR", "posts.comments.commenter.username", category+".predictions"]
        data = {
          "query": {
           "bool":{
             "must": [
                #{"match": { "categorization.predictions": { "query": category } } }
                #{"match": { "GTR": "st_in_584" }},
                 #{"match": {"GTR": "st_in_653"}},
                {"exists": {"field": category+".predictions"}}
                #{"exists": {"field": "posts.comments.commenter.username"}}
             ],
           "should": should_clause,
            "minimum_should_match": 1
           }
          },
          "fields":output_format,
          "_source": False,
          "size":"10000",
          "sort":{ "_score":{"order":"desc" } }

          }

        data["highlight"] = {"order": "score", "pre_tags": [""], "post_tags": [""], "fields": {"*": {}}}
        headers = {
            "Content-Type": "application/json",
        }
        response = es_obj.search(data, platform)
        response = json.loads(response.content)
        results = {}


        try:
            for highlight in response['hits']['hits']:
                resulting_fields=highlight['fields']
                if resulting_fields:
                    categorization_predictions= resulting_fields[category+".predictions"]
                    posts_comments_commenter_username = resulting_fields['posts.comments.commenter.username']
                    for category_res in categorization_predictions:
                        if category_res in results.keys():
                            for each_commenter in posts_comments_commenter_username:
                                results[category_res].append(each_commenter )
                        else:
                            results[category_res]= posts_comments_commenter_username

                #print(returned_fields=highlight.get('fields', None))
        except:
            print("response missing!")

        final_output= Counter(results)
        #most_active = final_output.most_common(commenters_limit)
        #print(most_active)
    return final_output
