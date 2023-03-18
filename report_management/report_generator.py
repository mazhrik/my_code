from core_management import elasticsearch_handler
import time

es = elasticsearch_handler.ElasticsearchHandler()

facebook_profile_report_config = {
    "facebook_profile_response_tms": {
        "name": {"type": "profile_information",
                 "columns": [{"col_name": "name", "alias": "name", "data_type": "string"},
                             {"col_name": "image", "alias": "image", "data_type": "string"}], "filters": []},
        "target_summary": {"type": "data_mining",
                           "columns": [
                               {"col_name": "string_attributes", "alias": "target_summary", "data_type": "string"}],
                           "filters": [{"match_phrase": {"algorithm_type": "target_summary"}}]},
        "posts_report": {"type": "posts",
                         "columns": [{"col_name": "emotion", "alias": "emotion", "data_type": "list"},
                                     {"col_name": "sentiment", "alias": "sentiment", "data_type": "list"},
                                     {"col_name": "categorization", "alias": "categorization", "data_type": "list"},
                                     {"col_name": "comments", "alias": "comments", "data_type": "list",
                                      "post_flag": "posts"},
                                     {"col_name": "reactions", "alias": "reactions", "data_type": "dict-length",
                                      "post_flag": "posts"}],
                         "filters": []},
        "close_associates": {"type": "close_associates",
                             "columns": [{"col_name": "score", "alias": "score", "data_type": "string",
                                          "post_flag": "close_associates"},
                                         {"col_name": "name", "alias": "name", "data_type": "string",
                                          "post_flag": "close_associates"},
                                         {"col_name": "image", "alias": "image", "data_type": "string",
                                          "post_flag": "close_associates"},
                                         ],
                             "filters": []},
    }
}


def twitter_report_data(gtr_id):
    pass


def query_generator(idx_type, gtr, filters_conf):
    query_body = {
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

        }, "size": 100}

    for filter in filters_conf:
        query_body["query"]["bool"]["must"].append(filter)

    return query_body


def query_executer(cols_config, index_name, query, idx_type):
    res_data = dict()
    while True:
        try:
            res = es.es.search(index=index_name, body=query)
            # print('res', res)
            break
        except Exception as ex:
            print("issue: ", ex)
            time.sleep(2)

    obj = None if len(res.get("hits", {}).get("hits", [{}])) <= 0 else res.get("hits", {}).get("hits", [{}])[0].get(
        "_source", None)
    if obj is not None:
        for col in cols_config:
            if col.get("post_flag", False):
                res_data[col["alias"]] = obj.get(col.get("post_flag")).get(col["col_name"])
            else:
                res_data[col["alias"]] = obj.get(col["col_name"])
            if isinstance(res_data[col["alias"]], list):
                res_data[col["alias"]] = res_data[col["alias"]][:3]

    else:
        return obj
    return res_data


if __name__ == "__main__":
    index_name = "facebook_profile_response_tms"
    gtr = "5feb1519da0a01c6c00ef5e4"
    response_obj = {}
    try:
        for data_conf in facebook_profile_report_config.get(index_name):
            data_obj = facebook_profile_report_config.get(index_name)
            idx_type = data_obj.get(data_conf).get("type")
            query = query_generator(idx_type, gtr, data_obj.get(data_conf).get("filters"))
            res = query_executer(data_obj.get(data_conf).get("columns"), index_name, query, idx_type)
            response_obj[data_conf] = res
        print(response_obj)
    except Exception as error:
        print(error)
