from copy import deepcopy


def clean_response(response=None):
    keys_required = ['general_information', 'profile_information',
                     'person_of_interests', 'target_information', 'info', 'other_information', 'contact_information']

    result = deepcopy(response)
    posts_analytics = {'emotion', 'sentiment', 'categorization'}
    for inner_key in response:
        if isinstance(response[inner_key], list):
            for idx in range(len(response[inner_key])):
                for last_key in response[inner_key][idx]:
                    if isinstance(response[inner_key][idx][last_key], dict):
                        if inner_key == 'posts' and last_key in posts_analytics:
                            pass
                        else:
                            temp = dict(result[inner_key][idx][last_key])
                            del result[inner_key][idx][last_key]
                            result[inner_key][idx].update(temp)

    result_keys = [*result]

    for key in keys_required:
        if key in result_keys:
            if len(result[key]) != 0:
                result.update(result[key][0].items())
                del result[key]

    mining_data = dict()
    if 'data_mining' in result:
        data_mining = result['data_mining']
        try:
            if data_mining:
                for type_of_mining in data_mining:
                    if type_of_mining['algorithm_type']:
                        # print(type_of_mining['algorithm_type'])
                        if type_of_mining['algorithm_type'] == 'common_words':
                            mining_data.update({'common_words': type_of_mining['list_attributes']})
                        elif type_of_mining['algorithm_type'] == 'word_cloud':
                            mining_data.update({'word_cloud': type_of_mining['string_attributes']})
                        elif type_of_mining['algorithm_type'] == 'behavioural_analysis':
                            mining_data.update({'behavioural_analysis': type_of_mining['list_attributes']})
                        elif type_of_mining['algorithm_type'] == 'most_used_hashtags':
                            mining_data.update({'most_used_hashtags': type_of_mining['list_attributes']})
                        elif type_of_mining['algorithm_type'] == 'target_summary':
                            mining_data.update({'target_summary': type_of_mining['string_attributes']})

                    else:
                        pass
        except Exception as ex:
            pass
    if 'analytics' in result:
        analytics = result['analytics']
        try:
            if analytics:
                for type_of_mining in analytics:
                    if type_of_mining['title']:
                        # print('title------------------', type_of_mining['title'])
                        if type_of_mining['title'] == 'post_frequnency_graph':
                            mining_data.update({'post_frequnency_graph': type_of_mining})
                    else:
                        pass
        except Exception as ex:
            pass
        # print('________!!!!!!!!!!!!!!!!!!!!!!!!!', result['analytics'])
    return result, mining_data
