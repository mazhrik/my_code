import datetime
from core_management import elasticsearch_handler
from target_management.models import SocialTarget
from target_management.signals import get_attribute
from target_management.link_analysis_kibana import get_link_analysis

es_object = elasticsearch_handler.ElasticsearchHandler()


class ElasticSearchResponseClean(object):

    def __init__(self):
        self.config_link_analysis = {"analysis": []}
        self.set_of_gtr = []
        self.flag = True
        self.beta_gtr = None

    def word_count(self, input_str):
        gen_sentence = dict()
        words = input_str.replace('{', '')
        words = words.replace('}', '')
        gen_sentence.update({'relation': words})
        return gen_sentence

    def graph_data(self, cleaned_responses):
        blasphemy_count = 0
        indecent_count = 0
        anti_state = 0
        law_order = 0
        incitement_to_offence = 0
        pornographic = 0
        sectarian = 0
        contempt_of_court = 0
        neither = 0
        happiness = 0
        sadness = 0
        neutral = 0
        worry = 0
        love = 0
        sentiment_positive = 0
        sentiment_negative = 0
        sentiment_neutral = 0
        emotions, sentiments, categorization = {}, {}, {}
        categorization_generic, categorization_new = {}, {}
        try:
            for post_data in cleaned_responses['posts']:
                if 'categorization' in post_data:
                    if 'blashphemy' in post_data['categorization']['predictions']:
                        blasphemy_count = blasphemy_count + 1
                    if 'indecent' in post_data['categorization']['predictions']:
                        indecent_count = indecent_count + 1
                    if 'anti-state' in post_data['categorization']['predictions']:
                        anti_state = anti_state + 1
                    if 'law and order' in post_data['categorization']['predictions']:
                        law_order = law_order + 1
                    if 'incitement to offence' in post_data['categorization']['predictions']:
                        incitement_to_offence = incitement_to_offence + 1
                    if 'pornographic' in post_data['categorization']['predictions']:
                        pornographic = pornographic + 1
                    if 'sectarian' in post_data['categorization']['predictions']:
                        sectarian = sectarian + 1
                    if 'contempt of court' in post_data['categorization']['predictions']:
                        contempt_of_court = contempt_of_court + 1
                    if 'neither' in post_data['categorization']['predictions']:
                        neither = neither + 1
                categorization = [{'Category': 'Blashphemy', 'value': blasphemy_count},
                                  {'Category': 'Indecent', 'value': indecent_count},
                                  {'Category': 'Law and order', 'value': law_order},
                                  {'Category': 'Anti-state', 'value': anti_state},
                                  {'Category': 'Incitement To Offence', 'value': incitement_to_offence},
                                  {'Category': 'Pornographic', 'value': pornographic},
                                  {'Category': 'Contempt Of Court', 'value': contempt_of_court},
                                  {'Category': 'Sectarian', 'value': sectarian},
                                  {'Category': 'Neither', 'value': neither},
                                  ]
            for post_data in cleaned_responses['posts']:
                if 'categorization' in post_data:
                    juck_data = post_data['categorization']['predictions']
                    if juck_data[0] not in categorization_new:
                        categorization_new[juck_data[0]] = 1
                    else:
                        categorization_new[juck_data[0]] = categorization_new[juck_data[0]] + 1

            generic = [{'Category': key, 'value': value} for key, value in categorization_new.items()]
            categorization_generic = sorted(generic, key = lambda i: i['value'],reverse=True)

            for sentiment_data in cleaned_responses['posts']:
                if 'sentiment' in sentiment_data:
                    if 'Negative' in sentiment_data['sentiment']['predictions']:
                        sentiment_negative = sentiment_negative + 1
                    if 'Positive' in sentiment_data['sentiment']['predictions']:
                        sentiment_positive = sentiment_positive + 1
                    if 'Neutral' in sentiment_data['sentiment']['predictions']:
                        sentiment_neutral = sentiment_neutral + 1
                sentiments = [{'Category': 'Positive', 'value': sentiment_positive},
                              {'Category': 'Negative', 'value': sentiment_negative},
                              {'Category': 'Neutral', 'value': sentiment_neutral}]

            for emotion_data in cleaned_responses['posts']:
                if 'emotion' in emotion_data:
                    if 'happiness' in emotion_data['emotion']['predictions']:
                        happiness = happiness + 1
                    if 'sadness' in emotion_data['emotion']['predictions']:
                        sadness = sadness + 1
                    if 'neutral' in emotion_data['emotion']['predictions']:
                        neutral = neutral + 1
                    if 'worry' in emotion_data['emotion']['predictions']:
                        worry = worry + 1
                    if 'love' in emotion_data['emotion']['predictions']:
                        love = love + 1
                emotions = [{'Category': 'Happiness', 'value': happiness},
                            {'Category': 'Sadness', 'value': sadness},
                            {'Category': 'Neutral', 'value': neutral},
                            {'Category': 'Worry', 'value': worry},
                            {'Category': 'Love', 'value': love}]
            return categorization, sentiments, emotions, categorization_generic
        except Exception as error:
            return [], [], []

    def get_beta_gtr_list(self, input_gtr):
        try:
            print('get', input_gtr)
            specific_object = SocialTarget.objects.filter(GTR=input_gtr).first()
            target_name = specific_object.user_names
            target_type = specific_object.target_type
            target_sub_type = specific_object.target_sub_type
            t_type, t_sub_type = get_attribute(target_type, target_sub_type)
            target_url = specific_object.target_url
            target_desc = specific_object.created_on
            target_id = specific_object.id
            target_title = specific_object.full_name
            if target_title == "":
                target_title = specific_object.user_names
            if self.flag:
                self.config_link_analysis['analysis'].append({"data": {"id": str(input_gtr),
                                                                       "name": target_title,
                                                                       "target_id": target_id,
                                                                       "target_type": target_type,
                                                                       "data_dump": {
                                                                           "created_on": target_desc,
                                                                           "username": target_name,
                                                                           "target_type": t_type,
                                                                           "target_sub_type": t_sub_type,
                                                                       }},
                                                              "style": {
                                                                  "background-image":
                                                                      target_url,
                                                                  "background-fit": "cover",
                                                                  "shape": "roundrectangle"
                                                              }, })
                self.flag = False
            else:
                print(input_gtr)
                self.config_link_analysis['analysis'].append({"data": {"id": str(input_gtr),
                                                                       "name": target_title,
                                                                       "target_id": target_id,
                                                                       "target_type": target_type,
                                                                       "data_dump": {
                                                                           "created_on": target_desc,
                                                                           "username": target_name,
                                                                           "target_type": t_type,
                                                                           "target_sub_type": t_sub_type,
                                                                       }
                                                                       },
                                                              "style": {
                                                                  "background-image":
                                                                      target_url,
                                                                  "background-fit": "cover"
                                                              }, })

            resp = es_object.get_response_by_alpha_gtr(index='link_analysis',
                                                       doc_type='joint_analysis',
                                                       alpha_gtr=input_gtr)
            joint_analysis = resp['_doc'][0]
            gtr_list = joint_analysis['beta_GTR_list']
            relations = joint_analysis['matched_values_list']
            if gtr_list:
                for idx in range(len(gtr_list)):
                    related_count = relations[idx]['matched_values']
                    set_of_counts = self.word_count(related_count)
                    self.config_link_analysis['analysis'].append({
                        "data": {
                            "source": str(input_gtr),
                            "target": str(gtr_list[idx]),
                            "data_edge": set_of_counts,

                        },
                    })
        except Exception as ex:
            # import traceback
            # traceback.print_exc()
            gtr_list = []
        return gtr_list

    def link_analysis_recursion(self, input_gtr, specific_object):
        print('aasd', input_gtr)
        self.set_of_gtr.append(input_gtr)
        beta_gtr_list = self.get_beta_gtr_list(input_gtr, specific_object)
        if beta_gtr_list:
            for beta_gtr in beta_gtr_list:
                if beta_gtr in set(self.set_of_gtr):
                    pass
                else:
                    specific_object = SocialTarget.objects.filter(GTR=beta_gtr).first()
                    print(beta_gtr)
                    self.link_analysis_recursion(beta_gtr, specific_object)
        return self.config_link_analysis

    def create_node(self, input_gtr, link_analysis_cyto):
        print('get', input_gtr)
        specific_object = SocialTarget.objects.filter(GTR=input_gtr).first()
        target_name = specific_object.user_names
        target_type = specific_object.target_type
        target_sub_type = specific_object.target_sub_type
        t_type, t_sub_type = get_attribute(target_type, target_sub_type)
        target_url = specific_object.target_url
        target_desc = specific_object.created_on
        target_id = specific_object.id
        target_title = specific_object.full_name
        if target_title == "":
            target_title = specific_object.user_names

        link_analysis_cyto['analysis'].append({"data": {"id": str(input_gtr),
                                                        "name": target_title,
                                                        "target_id": target_id,
                                                        "target_type": target_type,
                                                        "data_dump": {
                                                            "created_on": target_desc,
                                                            "username": target_name,
                                                            "target_type": t_type,
                                                            "target_sub_type": t_sub_type,
                                                        }},
                                               "style": {
                                                   "background-image":
                                                       target_url,
                                                   "background-fit": "cover",
                                                   "shape": "roundrectangle"
                                               }, })

    def link_analysis_explore(self, input_gtr, specific_object):
        try:
            print('aasd', input_gtr)
            link_analysis_cyto = {"analysis": []}
            result = get_link_analysis(input_gtr, 0)
            # start for the beta_gtr_list in resp
            self.create_node(input_gtr, link_analysis_cyto)

            gtr_list = result['beta_GTR_list']
            relations = result['matched_values_list']
            if gtr_list:
                for idx, gtr in enumerate(gtr_list):
                    related_count = relations[idx]['matched_values']
                    set_of_counts = self.word_count(related_count)

                    link_analysis_cyto['analysis'].append({
                        "data": {
                            "source": str(input_gtr),
                            "target": str(gtr_list[idx]),
                            "data_edge": set_of_counts,

                        },
                    })
                    self.create_node(gtr, link_analysis_cyto)

            return link_analysis_cyto
        except Exception as error:
            return error

    def format_response(self):
        for analysis in self.config_link_analysis['analysis']:
            print('analysis', analysis['alpha_gtr'])
            print('beta', analysis['beta_GTR_list'])
        return self.config_link_analysis

    def clean_response_summary(self, target_summary):
        target_summary_data = dict()
        response_keys = [*target_summary]
        if 'target_summary' in response_keys:
            target_summary_data.update({'target_summary': str(target_summary['target_summary'])})
        return target_summary_data

    def clean_most_common_hashtags(self, most_common_hashtags):
        most_common_hashtags_data = dict()
        response_keys = {*most_common_hashtags}
        tags_list = []
        if 'most_used_hashtags' in response_keys:
            for d in most_common_hashtags['most_used_hashtags']:
                tags_list.append({"tag" if k == "hashtag" else k: v for k, v in d.items()})
            most_common_hashtags_data.update({'hash_tags': tags_list})
        return most_common_hashtags_data

    def clean_most_common_words(self, most_common_words):
        most_common_words_data = dict()
        response_keys = {*most_common_words}
        tags_list = []
        # print(response_keys)
        if 'common_words' in response_keys:
            # print(most_common_words['list_attributes'])
            for d in most_common_words['common_words']:
                tags_list.append({"tag" if k == "word" else k: v for k, v in d.items()})
            most_common_words_data.update({'common': tags_list})
        return most_common_words_data

    def clean_response_freq(self, post_graph_freq):
        post_graph = post_graph_freq['post_frequnency_graph']
        print('asdasdas', post_graph)
        post_graph_data = dict()
        graph_list = []

        if all(v is not None for v in [post_graph['x_label'], post_graph['x_data'],
                                       post_graph['y_data'], post_graph['y_label']]):
            for x in range(0, len(post_graph['x_data'])):
                if isinstance(post_graph['x_data'][x], float):
                    changed_date = datetime.date.fromtimestamp(
                        float(post_graph['x_data'][x]))
                elif isinstance(post_graph['x_data'][x], str):
                    if post_graph['x_data'][x].isnumeric():
                        changed_date = datetime.date.fromtimestamp(
                            float(post_graph['x_data'][x]))
                    else:
                        changed_date = post_graph['x_data'][x]
                else:
                    changed_date = post_graph['x_data'][x]
                graph_list.append({post_graph['y_label']: post_graph['y_data'][x],
                                   post_graph['x_label']: changed_date})
            post_graph_data.update({'graph': graph_list})
        return post_graph_data

    def clean_response_cloud(self, word_cloud):
        word_cloud_data = dict()
        response_keys = [*word_cloud]
        print(response_keys)
        if 'word_cloud' in response_keys:
            word_cloud_data.update({'word_cloud': str(word_cloud['word_cloud'])})
        # print(word_cloud_data)
        return word_cloud_data

    # def clean_response_summary(self, word_cloud):
    #     word_cloud_data = dict()
    #     response_keys = [*word_cloud]
    #     print(response_keys)
    #     if 'target_summary' in response_keys:
    #         word_cloud_data.update({'target_summary': str(word_cloud['target_summary'])})
    #     # print(word_cloud_data)
    #     return word_cloud_data

    def clean_response(self, response=None):
        cleaned_data = response.copy()
        response_keys = [*response]
        # print(response_keys)
        check_keys = ['general_information', 'profile_information', 'likes', 'tv_programmes', 'books', 'music',
                      'person_of_interests', 'content', 'locations', 'search_engine',
                      'target_information', 'other_information', 'data_mining', 'contact_information',
                      'family', 'sports', 'posts', 'following', 'followers', 'work', 'skills']

        keys_to_add = {'accomplishments', 'education', 'work', 'professional_skills', 'interests', 'places',
                       'contact_information', 'web_links', 'volunteering', 'name', 'username', 'id', 'url', 'image',
                       'description', 'posts_count', 'followers_count', 'following_count', 'is_verified',
                       'is_business_account', 'is_private', 'is_joined_recently', 'admins', 'moderators',
                       'friends', 'family', 'relationship', 'following', 'followers', 'page_members', 'photos',
                       'associated_groups', 'close_associates', 'posts',
                       'videos', 'community_posts', 'events',
                       'check_ins', 'location_details', 'target_type', 'target_subtype', 'GTR', 'CTR', 'info', 'data'}
        posts = []
        data_mining = []
        search_engine = []
        tv_programmes = []
        followings = []
        followers = []
        music = []
        books = []
        likes = []
        family = []
        skill = []
        contact_information = []
        if response:
            for key in check_keys:
                if key in response_keys:
                    if response[key]:
                        for resp in response[key]:
                            if key == 'posts':
                                try:
                                    if 'posts' in resp:
                                        # posts.append(resp['posts'])
                                        if 'categorization' in resp:
                                            # posts.append(resp[0]['categorization'])
                                            resp['posts']['categorization'] = resp['categorization']
                                        if 'sentiment' in resp:
                                            resp['posts']['sentiment'] = resp['sentiment']
                                            print('resp', resp['sentiment'])
                                        posts.append(resp['posts'])
                                    # posts.append(resp['posts'])
                                except:
                                    posts.append(resp)
                            elif key == 'following':
                                try:
                                    followings.append(resp['following'])
                                except:
                                    followings.append(resp)
                            elif key == 'music':
                                try:
                                    music.append(resp['music'])
                                except:
                                    music.append(resp)
                            elif key == 'tv_programmes':
                                try:
                                    tv_programmes.append(resp['tv_programmes'])
                                except:
                                    tv_programmes.append(resp)
                            elif key == 'books':
                                try:
                                    books.append(resp['books'])
                                except:
                                    books.append(resp)
                            elif key == 'data_mining':
                                try:
                                    data_mining.append(resp['data_mining'])
                                except:
                                    data_mining.append(resp)

                            elif key == 'likes':
                                try:
                                    likes.append(resp['likes'])
                                except:
                                    likes.append(resp)
                            elif key == 'followers':
                                try:
                                    followers.append(resp['followers'])
                                except:
                                    followers.append(resp)
                            elif key == 'contact_information':
                                try:
                                    contact_information.append(resp['contact_information'])
                                except:
                                    contact_information.append(resp)
                            elif key == 'skills':
                                try:
                                    skill.append(resp['skills'])
                                except:
                                    skill.append(resp)
                            elif key == 'family':
                                try:
                                    family.append(resp['family'])
                                except:
                                    family.append(resp)

                            elif key == 'search_engine':
                                try:
                                    search_engine.append(resp['search_engine'])
                                except:
                                    search_engine.append(resp)
                            else:
                                cleaned_data.update(resp)
                        del cleaned_data[key]
                    else:
                        pass
        else:
            cleaned_data = None
            return cleaned_data
        cleaned_data_keys = {*cleaned_data}
        diff = set(keys_to_add) - set(cleaned_data_keys)
        print(diff)
        if diff:
            for key in diff:
                cleaned_data.update({key: []})
        else:
            pass
        # print(cleaned_data)
        cleaned_data.update({'posts': posts})
        cleaned_data.update({'likes': likes})
        cleaned_data.update({'following': followings})
        cleaned_data.update({'followers': followers})
        cleaned_data.update({'family': family})
        cleaned_data.update({'tv_programmes': tv_programmes})
        cleaned_data.update({'contact_information': contact_information})
        cleaned_data.update({'skills': skill})
        cleaned_data.update({'books': books})
        cleaned_data.update({'search_engine': search_engine})
        cleaned_data.update({'music': music})
        mining_data = dict()
        # print(data_mining)
        try:
            if data_mining:
                for type_of_mining in data_mining:
                    if type_of_mining['algorithm_type']:
                        print(type_of_mining['algorithm_type'])
                        if type_of_mining['algorithm_type'] == 'common_words':
                            mining_data.update({'common_words': type_of_mining['list_attributes']})
                        elif type_of_mining['algorithm_type'] == 'word_cloud':
                            mining_data.update({'word_cloud': type_of_mining['string_attributes']})
                    else:
                        pass
        except Exception as ex:
            print(ex)
        return dict(cleaned_data), mining_data
