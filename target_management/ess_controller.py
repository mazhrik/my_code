import asyncio
import threading

import requests
import logging
from django.conf import settings
import json
import aiohttp

logger = logging.getLogger(__name__)

TIME_OUT = 60


def do_login(function):
    def wrapper(*args, **kwargs):
        function(**kwargs)


class EssApiController(object):

    def __init__(self, max_tries=3):

        self.ess = None
        self.status_code = 0
        self.username = settings.ESS_SERVER_USER
        self.password = settings.ESS_SERVER_PASSWORD
        self.ip = settings.ESS_IP
        self.port = settings.ESS_SERVER_PORT
        self.server_base_url = 'http://{0}:{1}/'.format(self.ip, self.port)
        self.max_tries = max_tries
        self.header = ''
        self.ess_api_token = ''
        self.answer = {}

    def login(self):
        try:

            login_url = 'login/'
            response = requests.post(self.server_base_url + login_url,
                                     data={'username': self.username, 'password': self.password})
            print('login response', response)
            if response.status_code == 200:
                print(self.header)
                self.ess_api_token = response.content.decode('utf-8').split(':')[1].strip('"}')
                print(self.ess_api_token)
                self.header = {'Content-Type': 'application/x-www-form-urlencoded',
                               'Authorization': 'Token {0}'.format(self.ess_api_token)}

                print("Logged in")
                return True

        except Exception as e:
            print(e)
            return False

    def connection_status(self):
        try:
            add_target_url = 'connection'
            response = requests.get(self.server_base_url + add_target_url,
                                    headers=self.header)

            if response.status_code == 200:
                print('connection to ess ok')
                return True

            elif response.status_code == 401:
                print('invalid request')
                return False
            else:
                return False

        except Exception as e:
            print(e)

    def connect(self):
        try:
            if self.connection_status():
                print('connection')
                return True
            else:
                if self.login():
                    return True
                else:
                    return False
        except Exception as e:
            print(e)
            return False

    def do_request(self, url, header, payload, img_rever=False):
        try:
            if self.connect():
                print('payload', payload)
                if img_rever:
                    response = requests.post(url, headers=self.header, data={"url": payload['url']}, timeout=TIME_OUT)
                else:
                    print("------------", payload)
                    if payload == 'crawler_status':
                        response = requests.post(url, headers=self.header)
                    else:

                        response = requests.post(url, headers=self.header, data=payload)

                print('response', response)
                return response.json()
        except Exception as e:
            print('error', e)
            return None

    def ess_add_smart_search_target(self, username='arooma.shah', subtype='page', target_type='facebook'):
        add_target_url = 'smart_search/'
        payload = {'username': username, 'category': target_type, 'entity_type': subtype}
        print('payload:', payload)
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def add_target(self, username, target_type, target_sub_type, GTR, CTR, max_posts=10, avatar_password="", avatar_username=""):
        print("USERNAME", username)
        add_target_url = 'target/'
        payload = {'username': username, 'category': target_type, 'entity_type': target_sub_type, 'GTR': GTR,
                   'CTR': CTR, 'max_posts': max_posts, 'avatar_username':avatar_username, 'avatar_password':avatar_password}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def instagram_target_identification(self, query):
        add_target_url = 'instagram_target_identifier/'
        payload = {'query': query}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def facebook_target_identification(self, query):
        add_target_url = 'facebook_target_identifier/'
        payload = {'query': query, 'entity_type': 'users'}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def linkedin_target_identification(self, query):
        add_target_url = 'linkedin_target_identifier/'
        # Shehroz changed these payloads, added entity_type
        payload = {'query': query, 'entity_type': 'people'}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def twitter_target_identification(self, query):
        add_target_url = 'twitter_target_identifier/'
        payload = {'query': query}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def reddit_target_identification(self, query):
        add_target_url = 'reddit_target_identifier/'
        payload = {'query': query}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def tiktok_target_identification(self, query):
        add_target_url = 'tiktok_target_identifier/'
        payload = {'query': query}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def tumblr_target_identification(self, query):
        add_target_url = 'tumblr_target_identifier/'
        payload = {'query': query}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def google_trends(self, country='pakistan', realtime=False):
        add_target_url = 'google/trends/'
        payload = {'country': country, 'realtime': realtime}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def youtube_target_identification(self, query):
        add_target_url = 'youtube_target_identifier/'
        payload = {'query': query}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def target_internet_survey(self, name, email, phone, address):
        add_target_url = 'target_internet_survey/'
        payload = {'name': name, 'email': email, 'phone': phone, 'address': address}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def fake_identity_generator(self, nationality, gender, age):
        add_target_url = 'identitygenerator'
        payload = {'nationality': nationality, 'gender': gender, 'age': age}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def dark_web_search(self, query):
        add_target_url = 'darksearch'
        payload = {'query': query}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def leaked_data_whatsapp(self, phone_num):
        add_target_url = 'leaked_data_whatsapp/'
        
        payload = {
            'phone_number': phone_num
        }

        return self.do_request(self.server_base_url + add_target_url, self.header, payload=payload)

    def google_scholar_data_scraper(self, query):
        add_target_url = 'scholar'
        payload = {'query': query}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def google_patents_data_scraper(self, query):
        add_target_url = 'patents'
        payload = {'query': query}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def amazon_data_scraper(self, query):
        add_target_url = 'amazon'
        payload = {'query': query}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def daraz_data_scraper(self, query):
        add_target_url = 'daraz'
        payload = {'query': query}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def tweets_near_location(self, query, location):
        add_target_url = 'twitter/phrase_near_location/'
        payload = {'phrase': query, 'location': location}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def tweets_near_location_within_miles(self, location, distance):
        add_target_url = 'twitter/near_location_within_miles/'
        payload = {'location': location, 'distance': str(distance) + ' mil'}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def tweets_positive(self, query):
        add_target_url = 'twitter/positive/'
        payload = {'query': query}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def tweets_negative(self, query):
        add_target_url = 'twitter/negative/'
        payload = {'query': query}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def tweets(self, query):
        add_target_url = 'twitter/search/'
        payload = {'query': query}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def tweets_search_result(self, category, all_of_these_words, exact_phrase, any_of_these_words, none_of_these_words,
                             hashtags,
                             language, from_these_accounts, to_these_accounts, mentioning_these_accounts, replies,
                             only_replies, links, only_tweet_with_links, min_replies, min_likes, min_retweets,
                             from_date, to_date):
        add_target_url = 'twitter_tools/'
        payload = {'category': category, 'all_of_these_words': all_of_these_words, 'exact_phrase': exact_phrase,
                   'any_of_these_words': any_of_these_words, 'none_of_these_words': none_of_these_words,
                   'hashtags': hashtags, 'language': language, 'from_these_accounts': from_these_accounts,
                   'to_these_accounts': to_these_accounts, 'mentioning_these_accounts': mentioning_these_accounts,
                   'replies': replies, 'only_replies': only_replies, 'links': links,
                   'only_tweet_with_links': only_tweet_with_links, 'min_replies': min_replies, 'min_likes': min_likes,
                   'min_retweets': min_retweets, 'from_date': from_date, 'to_date': to_date}
        return self.do_request(self.server_base_url + add_target_url, self.header, json.dumps(payload))

    def create_payload(self, title="",url=''):
        add_target_url = 'ip_shortend_url'
        payload = {'url': url, 'title':title}
        # print(payload)
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def image_reverse_lookup(self, image, url=''):
        add_target_url = 'image_lookup'
        payload = {'image': image, 'url': url}
        # payload=[("files", ("image", image, "application/octet")),("data",
        # ("data", json.dumps(url), "application/json" ))]
        return self.do_request(self.server_base_url + add_target_url, self.header, payload, img_rever=True)

    def get_domains_ip_info(self, domian='www.google.com'):
        add_target_url = 'domain_ip_information'
        payload = {'domain': domian}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def get_domains_info(self, domian='www.google.com'):
        add_target_url = 'domain_information'
        payload = {'domain': domian}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def track_ip(self, code):
        add_target_url = 'ip_tracking'
        payload = {'code': code}
        print(payload)
        # response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def get_tag_originator(self, tagName):
        add_target_url = 'tag_originator'
        payload = {'tag': tagName}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def ess_add_twitter_trends_worldwide_target(self):
        add_target_url = 'social/twitter/worldtrends/'
        payload = {}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def twitter_trends(self, country):
        add_target_url = 'twitter/trends/'
        payload = {'country': country}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def youtube_trends(self):
        add_target_url = 'youtube/trends/'
        payload = {}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def reddit_trends(self):
        add_target_url = 'reddit/trends/'
        payload = {}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def microcrawler_status(self):
        add_target_url = 'crawler_status/'
        payload = {}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def crawler_internet_connection(self):
        add_target_url = 'crawler_internet/'
        payload = {}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def dynamic_crawling(self, url, ip_address, domain, pictures, videos, heading, paragraphs, links, GTR, CTR,vpn=False):
        add_target_url = 'generic/'
        payload = {'url': url, 'ip_address': ip_address, 'domain': domain, 'pictures': pictures,
                   'videos': videos, 'headings': heading, 'paragraphs': paragraphs, 'links': links, 'GTR': GTR,
                   'CTR': CTR, 'vpn':vpn}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def add_keybase_target(self, keywords, social_sites, GTR, CTR):
        add_target_url = 'keybase/'
        payload = {"keywords": keywords, "GTR": str(GTR), "CTR": str(CTR), "social_sites": social_sites}
        payload_json = json.dumps(payload)
        print('payload', type(payload_json))
        return self.do_request(self.server_base_url + add_target_url, self.header, json.dumps(payload_json))

    def ess_add_news_target(self, top=10, news_site='bbc'):
        add_target_url = 'news/'
        payload = {'number_of_headlines': top, 'news_paper': news_site}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def get_news_search(self, news):
        add_target_url = 'news_search'
        payload = {'query': news}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def news_crawling(self, top=10, news_site='bbc', channel_link = "https://www.bbc.com/news" ):
        add_target_url = 'news_crawler/'
        payload = {'number_of_headlines': top, 'channel_name': news_site, "channel_link": channel_link}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def action_post(self, text, social_media, username, password, image_url):

        add_target_url = 'avatar/post/'
        payload = {'text': text, 'social_media': social_media, 'email': username, 'password': password, "media": image_url}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def action_comment(self, text, post_url, social_media, username, password):

        add_target_url = 'avatar/comment/'
        payload = {'text': text, 'social_media': social_media, 'target_post': post_url, 'email': username,
                   'password': password}

        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def action_reaction(self, reaction, post_url, social_media, username, password):
        add_target_url = 'avatar/reaction/'
        payload = {'Reaction': reaction, 'social_media': social_media, 'target_post': post_url, 'email': username,
                   'password': password}

        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def action_share(self, text, post_url, social_media, username, password):
        add_target_url = 'avatar/share/'
        payload = {'text': text, 'social_media': social_media, 'target_post': post_url, 'email': username,
                   'password': password}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def action_send_message(self, social_site, target_username, message, username='majidahmed.123@outlook.com',
                            password='someonesomeone'):
        add_target_url = 'avatar/message/'
        payload = {'social_media': social_site, 'target_username': target_username, 'email': username,
                   'password': password, 'message': message}
        print(payload)
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def action_add_friend(self, social_media, email, username, password, target_type):
        add_target_url = 'avatar/addfriend_group/'
        payload = {'social_media': social_media, 'email': email, 'username': username,
                   'password': password, "target_type":target_type}
        print(payload)
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def social_acc_login(self, id, email, username, social_media, status):
        add_target_url = 'social_acc/relogin/'
        payload = {
            'id': id,
            'email': email,
            'username': username,
            'social_media': social_media,
            'status': status,
        }
        print(payload)

        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def getall_sm_account(self):
        add_target_url = 'getall_sm_account/'
        payload = {}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def add_sm_account(self, social_media, username, status, email, password, userid):
        """
        @params <required>
        """
        add_target_url = 'add_sm_account/'
        payload = {'social_media': social_media, 'username': username, 'status': status, 'email': email,
                   'password': password, 'id': userid}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def update_sm_account(self, social_media, username, status, email, password, userid):
        add_target_url = 'update_sm_account/'
        payload = {'social_media': social_media, 'username': username, 'status': status, 'email': email,
                   'password': password, 'id': userid}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def delete_sm_account(self, userid):
        add_target_url = 'delete_sm_account/'
        payload = {'id': userid}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def get_task_terminate(self, task_id):
        add_target_url = 'task_terminate'
        payload = {'task_id': task_id}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)

    def get_crawler_status(self):
        add_target_url = 'crawler_status/'
        return self.do_request(self.server_base_url + add_target_url, self.header, payload='crawler_status')

"""

    def ess_add_twitter_trends_worldwide_target(self):
        try:
            add_target_url = 'social/twitter/worldtrends/'
            payload = {}
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            print(response.json())
            return response.json()
        except Exception as e:
            print(e)
            return {'response': 'ess replied null'}

    def target_internet_survey(self, name, email, phone, address):
        try:
            if (self.connect()):
                add_target_url = 'target_internet_survey/'
                payload = {'name': name, 'email': email, 'phone': phone, 'address': address}
                response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
                print(response.json())
                return response.json()
        except Exception as e:
            print(e)
            return {'response': 'ess replied null'}

    def dynamic_crawling(self, url, ip_address, domain, pictures, videos, heading, paragraphs, links, GTR, CTR):
        try:
            if (self.connect()):
                add_target_url = 'generic/'
                payload = {'url': url, 'ip_address': ip_address, 'domain': domain, 'pictures': pictures,
                           'videos': videos, 'heading': heading, 'paragraphs': paragraphs, 'links': links, 'GTR': GTR,
                           'CTR': CTR}

                response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)

                return response.json()
        except Exception as e:
            print(e)
            return None

    def add_target(self, username, category, entity_type, GTR, CTR, max_posts, apply_AI):
        try:
            if (self.connect()):
                apply_AI = json.dumps(apply_AI)

                add_target_url = 'target/'

                payload = {'username': username, 'category': category, 'entity_type': entity_type, 'GTR': GTR,
                           'CTR': CTR, 'max_posts': max_posts, 'apply_AI': apply_AI}
                response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)

                return response.json()

        except Exception as e:
            print(e)
            return None

    def news_crawling(self, top=10, news_site='bbc'):
        try:
            add_target_url = 'news_crawler/'
            payload = {'number_of_headlines': top, 'channel_name': news_site}
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            print(response.json())
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}

    def instagram_target_identification(self, query):
        try:
            add_target_url = 'instagram_target_identifier/'

            payload = {'query': query}
            print(payload)
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            print(response.json())
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}

    def facebook_target_identification(self, query):
        try:
            add_target_url = 'facebook_target_identifier/'
            payload = {'query': query}
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            print(response.json())
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}

    def linkedin_target_identification(self, query):
        try:
            add_target_url = 'linkedin_target_identifier/'
            payload = {'query': query}
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            print(response.json())
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}

    def twitter_target_identification(self, query):
        try:
            add_target_url = 'twitter_target_identifier/'
            payload = {'query': query}
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            print(response.json())
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}

    def reddit_target_identification(self, query):
        try:
            add_target_url = 'reddit_target_identifier/'
            payload = {'query': query}
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            print(response.json())
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}

    def youtube_target_identification(self, query):
        try:
            add_target_url = 'youtube_target_identifier/'
            payload = {'query': query}
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            print(response.json())
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}

    def add_keybase_target(self, keywords, social_sites, GTR, CTR):

        try:

            if (self.connect()):
                add_target_url = 'keybase/'

                payload = {'keywords': keywords, 'GTR': str(GTR), 'CTR': str(CTR), 'social_sites': social_sites}
                print(type(keywords), keywords)
                print(payload)
                Header = {'Content-Type': 'application/json',
                          'Authorization': 'Token {0}'.format(ESS_API_TOKEN)}
                import json
                payload_json = json.dumps(payload)
                print(response.json())
                return response.json()

        except Exception as e:
        return None

    def get_repute_management(self, keywords, social_sites, GTR, CTR):
        try:
            add_target_url = 'rms/'
            payload = {'keywords': keywords, 'GTR': str(GTR), 'CTR': str(CTR), 'social_sites': social_sites}
            import json
            payload_json = json.dumps(payload)

            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload_json)
            # print(response.json())
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}

    def get_rss_feed(self, gtr, ctr):
        try:
            add_target_url = 'rss_feeds'
            payload = {'GTR': gtr, 'CTR': ctr}
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}

    def get_tag_originator(self, tagName):
        try:
            add_target_url = 'tag_originator'
            payload = {'tag': tagName}
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}

    def get_news_search(self, news):
        try:
            add_target_url = 'news_search'
            payload = {'query': news}
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}

    def get_crawler_status(self):
        try:
            add_target_url = 'crawler_status/'
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header)
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}

    def get_task_terminate(self, task_id):
        try:
            add_target_url = 'task_terminate'
            payload = {'task_id': task_id}
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}

    def get_domains_ip_info(self, domian='www.google.com'):
        try:
            add_target_url = 'domain_ip_information'
            payload = {'domain': domian}
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}

    def get_domains_info(self, domian='www.google.com'):
        try:
            add_target_url = 'domain_information'
            payload = {'domain': domian}
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            # print(response.json())
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}

    def test_api(self, keywords, GTR, CTR):

        try:
            add_target_url = 'http://127.0.0.1:8000/core/test_api/'

            payload = {'keywords': keywords, 'GTR': GTR, 'CTR': CTR}
            print(payload)
            Header = {'Content-Type': 'application/json'}
            import json
            payload_json = json.dumps(payload)
            response = requests.get(add_target_url, headers=Header, json=payload_json)
            print(response.json())
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}


    def create_payload(self, url=''):
        try:
            add_target_url = 'ip_shortend_url'
            payload = {'url': url}
            print(payload)
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            print(response.json())
            return response.json()

        except Exception as e:
            print(e)
            return {'response': 'ess replied null'}

    def track_ip(self, code, start_date, end_date):
        try:
            add_target_url = 'ip_tracking'
            payload = {'code': code, 'start_date': start_date, 'end_date': end_date}
            print(payload)
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            print(response.json())
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}

    def image_reverse_lookup(self, image, url=''):
        try:
            # img = self.data["personal_info"]["image"]

            # req = requests.post(url=API_ENDPOINT, files=files)
            import json
            add_target_url = 'image_lookup'
            payload = {'image': image, 'url': url}
            # image = {'media': image}
          img = self.data["personal_info"]["image"]
            files = [('files', (img, open(img, 'rb'),'application/octet')),('data', ('data', json.dumps(self.data),
            'application/json')), ]

            Header = {'Authorization': 'Token {0}'.format(ESS_API_TOKEN)}
            'application/json'))]
            print(payload)
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data={'url': url},
                                     files={'image': image})
            print(response.json())
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}


   

    def twitter_trends(self, country='pakistan'):
        try:
            add_target_url = 'twitter/trends'
            payload = {'country': country}
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            print(response.json())
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}

    def twitter_world_trends(self):
        try:
            add_target_url = 'twitter/trends'
            payload = {}
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            print(response.json())
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}

    def youtube_trends(self):
        try:
            add_target_url = 'youtube/trends'
            payload = {}
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            print(response.json())
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}

    def reddit_trends(self):
        try:
            add_target_url = 'reddit/trends'
            payload = {}
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            print(response.json())
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}

    def google_trends(self, country='pakistan', realtime=False):
        try:
            add_target_url = 'google/trends'
            payload = {'country': country, 'realtime': realtime}
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            print(response.json())
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}

    # ...................................Tools Api's.................................

    def fake_identitity_generator(self, nationality, gender, age):
        try:
            add_target_url = 'identitygenerator'
            payload = {'nationality': nationality, 'gender': gender, 'age': age}
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            print(response.json())
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}

    def dark_web_search(self, query):
        try:
            add_target_url = 'darksearch'
            payload = {'query': query}
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}

    def amazon_data_scraper(self, query):
        try:
            add_target_url = 'amazon'
            payload = {'query': query}
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            print(response.json())
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}

    def daraz_data_scraper(self, query):
        try:
            add_target_url = 'daraz'
            payload = {'query': query}
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            print(response.json())
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}

    def google_scholar_data_scraper(self, query):
        try:
            add_target_url = 'scholar'
            payload = {'query': query}
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            print(response.json())
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}

    def google_patents_data_scraper(self, query):
        try:
            add_target_url = 'patents'
            payload = {'query': query}
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            print(response.json())
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}


    def social_media_create_post(self, img, username, text, media_type):
        try:
            add_target_url = 'create_post/'
            Header = {'Authorization': 'Token {0}'.format(ESS_API_TOKEN)}
            payload = {'username': username, 'text': text, 'socialmedia_type': media_type}
            image = {'img': img}
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload, files=image)
            print(response.json())
            return response.json()
        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}

    def social_media_delete_post(self, username, post_ref_id, post_type):
        try:
            add_target_url = 'delete_post/'
            Header = {'Authorization': 'Token {0}'.format(ESS_API_TOKEN)}
            payload = {'username': username, 'post_id': post_ref_id, 'socialmedia_type': post_type}
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            print(response.json())
            return response.json()
        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}

    def social_media_create_account(self, username, password, socialmedia_type):
        try:
            add_target_url = 'add_account/'
            Header = {'Authorization': 'Token {0}'.format(ESS_API_TOKEN)}
            payload = {'username': username, 'password': password, 'socialmedia_type': socialmedia_type}
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            print(response.json())
            return response.json()
        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}

    def social_media_post_info(self, username, password, socialmedia_type):
        try:
            add_target_url = 'post_information/'
            Header = {'Authorization': 'Token {0}'.format(ESS_API_TOKEN)}
            payload = {'username': username, 'password': password, 'socialmedia_type': socialmedia_type}
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            print(response.json())
            return response.json()
        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}


if __name__ == "__main__":
    pass

"""
