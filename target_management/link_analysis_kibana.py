import requests
import json
from OCS_Rest import settings

ip = settings.CLUSTER_IP
port = settings.PORT_ES


#-----------------------global variabes---------
# gtr="st_tw_232"
# ctr="1"
# field_to_analyze= ["username","username_c"]
headers = {
         "Content-Type": "application/json",
      }



#----------------REST API------------------------------
def search(query):
    response = requests.get("http://{0}:{1}/twitter*,facebook*,linkedin*,news*,reddit*,instagram*,youtube*,keybase*,trends*,rss*/_search".format(ip,port),
                        headers=headers,
                        data=json.dumps(query)
                    )
    return response






#--------------------Extract the target-----------------
def get_alpha(gtr, fields=None):
    if not fields:
        raise Exception("Define Cretaria for Alpha Function e.g by=['username','username_c'] : supports RegExp")
    fields = ["*"+key for key in fields]
    query = {
            "query":{
                "bool":{
                "must":[{
                        "match":{
                            "GTR":gtr,
                            }
                        }]
                    }
                }
        }

    query["_source"] = True
    query['size'] = "10000"
    query['sort'] = {"_score":{"order":"desc"}}
    query['fields'] = fields

    query["highlight"] = {"order":"score","fields":{"*":{}} }

    response = search(query)
    print('-------------------response  :',response)
    results = []
    for result in json.loads(response.content)['hits']['hits']:
                for keys,values in result.get('fields',{}).items():
                    for value in values:
                            if value not in ["","null",None]:
                                results.append(value)
    return (list(set(results)),fields)








#--------------------Transform the Kibana Response-----------------
def get_beta(alphas,gtr,ctr):
    print("--------------------------------Alpha's--------------------------------")
    print()
    #print(alphas[0])
    print()
    print("--------------------------------Alpha's--------------------------------")

    targets = alphas[0]
    fields = alphas[1]
    query = {
    "query": {
        "query_string": {
            "query": " OR ".join(["("+target+")" for target in targets]),
            "type":"phrase",
            "fields": fields
        }
    }
    }
    query["_source"] = True
    query['size'] = "10000"
    query['sort'] = {"_score":{"order":"desc"}}
    query["highlight"] = {"order":"score","pre_tags":[""],"post_tags":[""],"fields":{"*":{}} }

    response = search(query)
    print("response   :",response)
    

    response = json.loads(response.content)
    if response.get('hits', {}).get('hits', None):
        print("No betas found")

    print('response recieved')
    results = []
    beta_gtrs=[]
    for highlight in response.get('hits',{}).get('hits',[]):
        beta_gtr = highlight.get('_source', {}).get('GTR', None)
        if beta_gtr != gtr and beta_gtr not in beta_gtrs:
            to_return = {}

            to_return['_id'] = highlight.get('_id',None)
            to_return['_index'] = highlight.get('_index',None)
            to_return['beta_GTR'] = highlight.get('_source',{}).get('GTR',None)
            to_return['beta_CTR'] = highlight.get('_source', {}).get('CTR', None)
            #to_return['target_type'] = highlight.get('_source',{}).get('target_type',None)
            #to_return['target_subtype'] = highlight.get('_source',{}).get('target_subtype',None)
            to_return['matched_values'] = str(highlight.get('highlight',None))
            results.append(to_return)
            beta_gtr= highlight.get('_source',{}).get('GTR',None)
            beta_gtrs.append(beta_gtr)

    response_link_analysis= {}
    #if (len(results)!=0):
    response_link_analysis['GTR']= gtr
    response_link_analysis['CTR'] = ctr
    response_link_analysis['algorithm_type'] = 'basic_link_analysis'
    response_link_analysis['beta_GTR_list'] = beta_gtrs
    response_link_analysis['matched_values_list'] = results
    return response_link_analysis






def get_link_analysis(GTR,CTR,field_to_analyze= ["username","username_c"]):
    print("-------------get_link_analysiss---------------")
    # ---------------------Link Analysis Response---------------
    to_be_saved = get_beta(get_alpha(GTR, fields=field_to_analyze), GTR, CTR)
    print(to_be_saved)
    return to_be_saved






"""
#--------------------Save in elastic Search-------------------
def insert_one_data(_index, data, doc_type):
    res = es.index(index=_index, doc_type=doc_type, body=data)
    # index will return insert info: like as created is True or False
    print(res)
insert_one_data("link_analysis", to_be_saved, "_doc")
print("saved")
"""