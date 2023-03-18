import requests
import json


def get_categorization_visual(category, output_format):
    fields = ["*"]
    data = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"categorization.predictions": {"query": category}}},
                    # {"match": {"created_on": {"query": date}}}
                ]
            }
        },
        "fields": output_format,
        "_source": True,
        "size": "10000",
        "sort": {"_score": {"order": "desc"}}
    }

    data["highlight"] = {"order": "score", "pre_tags": [""], "post_tags": [""], "fields": {"*": {}}}
    headers = {
        "Content-Type": "application/json",
    }
    response = requests.get(
        "http://192.168.18.155:9200/twitter*,facebook*,linkedin*,news*,reddit*,instagram*,youtube*,keybase*,trends*,rss*/_search",
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
            # to_return['highlight'] = highlight.get('highlight', None)
            to_return['fields'] = highlight.get('fields', None)
            results.append(to_return)
    except:
        print("response missing!")

    # print(json.dumps(results, indent=5))
    # res = json.dumps(results, indent=5)
    return results


res = get_categorization_visual("anti-state", ["GTR", "username", "created_on", "posts.url_c", "url"])


# def report_generation(category, date):
#
#     res = get_categorization_visual(category, date)
#
#     for r in res:
#         print(r)
