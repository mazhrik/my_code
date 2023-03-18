import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def do_login(function):
    def wrapper(*args, **kwargs):
        function(**kwargs)


class AisApiController(object):

    def __init__(self, max_tries=3):

        self.ais = None
        self.status_code = 0
        self.username = settings.AIS_SERVER_USER
        self.password = settings.AIS_SERVER_PASSWORD
        self.ip = settings.AIS_IP
        self.port = settings.AIS_SERVER_PORT
        self.server_base_url = 'http://{0}:{1}/'.format(self.ip, self.port)
        self.max_tries = max_tries
        self.header = ''
        self.ess_api_token = ''

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
            response = requests.get(self.server_base_url + add_target_url, headers=self.header)

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

    def do_request(self, url, header, payload):
        try:
            if self.connect():
                print('payload', payload)
                response = requests.post(url, headers=self.header, data=payload)
                print('response', response)
                return response.json()
        except Exception as e:
            print('error', e)
            return None

    def text_analytics(self, input_text, operation='common_words'):
        add_target_url = 'text_analytics'
        payload = {'text': input_text, 'task': operation}
        return self.do_request(self.server_base_url + add_target_url, self.header, payload)


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

    def microcrawler_status(self):
        try:
            add_target_url = 'crawler_status/'
            payload = {}
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}

    def crawler_internet_connection(self):
        try:
            add_target_url = 'crawler_internet/'
            payload = {}
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            # print(response.json())
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
                response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, json=payload_json)
                print(response.json())
                return response.json()

        except Exception as e:
            print(e)
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

            Header = {'Authorization': 'Token {0}'.format(ESS_API_TOKEN)}
            'application/json'))]
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data={'url': url},
                                     files={'image': image})
            # print(response.json())
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}


    def action_post(self, text, social_media, username, password):
        try:
            add_target_url = 'avatar/post/'
            payload = {'text': text, 'social_media': social_media, 'email': username, 'password': password}
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            print(response.json())
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}

    def action_comment(self, text, post_url, social_media, username, password):
        try:
            add_target_url = 'avatar/comment/'
            payload = {'text': text, 'social_media': social_media, 'target_post': post_url, 'email': username,
                       'password': password}
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            print(response.json())
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}

    def action_reaction(self, reaction, post_url, social_media, username, password):
        try:
            add_target_url = 'avatar/reaction/'
            payload = {'Reaction': reaction, 'social_media': social_media, 'target_post': post_url, 'email': username,
                       'password': password}
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            print(response.json())
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}

    def action_share(self, text, post_url, social_media, username, password):
        try:
            add_target_url = 'avatar/comment/'
            payload = {'text': text, 'social_media': social_media, 'target_post': post_url, 'email': username,
                       'password': password}
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            print(response.json())
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}

    def action_send_message(self, social_site, target_username, message, username='majidahmed.123@outlook.com',
                            password='someonesomeone'):
        try:
            add_target_url = 'avatar/message/'
            payload = {'social_media': social_site, 'target_username': target_username, 'email': username,
                       'password': password, 'message': message}
            print(payload)
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            print(response.json())
            return response.json()

        except Exception as e:
            print(e)
            return None

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

    def tweets_near_location(self, query, location):
        try:
            add_target_url = 'twitter/phrase_near_location/'
            payload = {'phrase': query, 'location': location}
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            print(response.json())
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}

    def tweets_near_location_within_miles(self, location, distance):
        try:
            add_target_url = 'twitter/near_location_within_miles/'
            payload = {'location': location, 'distance': str(distance) + ' mil'}
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            print(response.json())
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}

    def tweets_positive(self, query):
        try:
            add_target_url = 'twitter/positive/'
            payload = {'query': query}
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            print(response.json())
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}

    def tweets_negative(self, query):
        try:
            add_target_url = 'twitter/negative/'
            payload = {'query': query}
            response = requests.post(ESS_SERVER_BASE_URL + add_target_url, headers=Header, data=payload)
            print(response.json())
            return response.json()

        except Exception as e:
            print(e)
        return {'response': 'ess replied null'}

    def tweets(self, query):
        try:
            add_target_url = 'twitter/search/'
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
