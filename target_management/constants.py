from django.utils.translation import gettext as _

# Constants used for Target Management
TARGET_TYPE = [('fb', _('facebook')),
               ('tw', _('twitter')),
               ('in', _('instagram')),
               ('ln', _('linkedin')),
               ('yt', _('youtube')),
               ('rd', _('reddit')),
               ('kb', _('keybase')),
               ('gn', _('generic')),
               ('se', _('search_engine')),
               ('nw', _('news')),
               ("tk", _("tiktok")),
               ("sc", _("snapchat")),
               ("tb", _("tumblr")),
               ("dw", _("darkweb"))]

INDEX_PLATFORM_ALL = [('fb', _('facebook_*')),
                      ('tw', _('twitter_*')),
                      ('in', _('instagram_*')),
                      ('ln', _('linkedin_*')),
                      ('tk', _('tiktok_*')),
                      ('sc', _('snapchat_*')),
                      ('tb', _('tumblr_*')),
                      ('yt', _('youtube_*')),
                      ('rd', _('reddit_*')),
                      ('kb', _('keybase_*')),
                      ('gn', _('generic_*')),
                      ('se', _('search_engine_*')),
                      ('nw', _('news_*'))]

TARGET_SUB_TYPE = (
    ('per', _('profile')),
    ('pag', _('page')),
    ('gro', _('group')),
    ('com', _('company')),
    ('hash', _('hash')),
    ('sub', _('subreddit')),
    ('sear', _('search')),
    ('news', _('news')),
    ('cha', _('channel')),
)

AIS_PROCESS = (
    ('cat', _('profile')),
    ('fac', _('page')),
    ('gro', _('group')),
    ('comp', _('company')),
    ('hash', _('hash')),
    ('red', _('subreddit')),
    ('sear', _('search')),
    ('news', _('news')),
)

PERIODIC_INTERVALS = (
    (0, _('one time only')),
    (5, _('once per 5 minutes ')),
    (10, _('once per 10 minutes ')),
    (15, _('once per 15 minutes ')),
    (30, _('once per 30 minutes ')),
    (40, _('once per 40 minutes ')),
    (60, _('once per 60 minutes ')),
    (90, _('once per 90 minutes ')),
    (120, _('once per 120 minutes ')),
    (180, _('once per 180 minutes ')),
    (360, _('once per 360 minutes ')),
    (720, _('once per 720 minutes ')),
)

TARGET_INDEX_RESOLVE = (
    ('instagram,profile', _('instagram_profile_')),
    ('tiktok,profile', _('tiktok_profile_')),
    ('snapchat,profile', _('snapchat_profile_')),
    ('tumblr,profile', _('tumblr_profile_')),
    ('instagram,page', _('instagram_page_')),
    ('twitter,profile', _('twitter_profile_')),
    ('instagram,group', _('instagram_group_')),
    ('facebook,profile', _('facebook_profile_')),
    ('facebook,page', _('facebook_page_')),
    ('facebook,group', _('facebook_group_')),
    ('linkedin,profile', _('linkedin_profile_')),
    ('linkedin,company', _('linkedin_company_')),
    ('reddit,profile', _('reddit_profile_')),
    ('keybase,search', _('keybase_')),
    ('youtube,profile', _('youtube_channel_')),
    ('youtube,channel', _('youtube_channel_')),
    ('reddit,subreddit', _('reddit_subreddit_')),
    ('generic,search', _('generic_crawler_')),
)
DOCUMENTS_TYPE_CHOICES = ['posts']

INDEX_LIST = ['followers', 'following', 'profile_information', 'accomplishments', 'admins', 'associated_groups',
              'check_ins', 'close_associates', 'data_mining', 'community_posts', 'education', 'events',
              'external_url', 'family','friends', 'info', 'interests', 'location_details', 'moderators',
              'page_numbers', 'posts', 'professional_skills', 'relationship', 'target_information', 'videos',
              'volunteering', 'web_links', 'profile_work', 'controllers', 'creator', 'history', 'location_details',
              'member_stats', 'moderators', 'page_members', 'posting_stats', 'rules', 'type', 'work',
              'countries_involved', 'statistics', 'entity', 'family', 'films', 'games', 'general_information',
              'likes', 'media_links', 'music', 'notes', 'questions', 'data_mining', 'reviews', 'sports',
              'tv_programmes', 'honors', 'all', 'popular', 'new', 'address', 'creation_date', 'dnssec', 'updated_date',
              'domain_information',
              'heading', 'headings', 'images', 'links', 'name_servers', 'nets', 'paragraphs', 'span', 'status',
              'domain_name',
              'emails', 'expiration_date', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7',
              'karma_points', 'data_mining', 'analytics']

GENERIC_INDEX_LIST = [
    'creation_date',
    'dnssec', 'domain_name',
    'emails', 'expiration_date', 'heading',
    'headings', 'images', 'links',
    'name_servers', 'nets', 'paragraphs',
    'span', 'status', 'target_information', 'text',
    'updated_date', 'page_information', 'basic_information',
    'categorization'
]

KEYBASE_INDEX_LIST = ['facebook_events', 'facebook_groups', 'facebook_pages',"darkweb",
                      'facebook_pictures', 'facebook_posts', 'facebook_users', 'facebook_videos', 'instagram_hashtags',
                      'instagram_places', 'instagram_users', 'linkedin', 'news_data',
                      'reddit_data', 'search_engine_ask', 'search_engine_baidu', 'search_engine_bing',
                      'search_engine_duckduckgo', 'search_engine_google',
                      'search_engine_yahoo', 'search_engine_yandex', 'target_information', 'twitter_tweets',
                      'youtube_videos', 'followers', 'profile_following', 'profile_information', 'accomplishments', 'admins',
                      'associated_groups', 'search_engine', 'linkedin_data',
                      'check_ins', 'close_associates', 'data_mining', 'community_posts', 'education', 'events',
                      'external_url', 'family', 'friends', 'info', 'interests', 'location_details', 'moderators',
                      'page_numbers', 'posts', 'professional_skills', 'relationship', 'target_information', 'videos',
                      'volunteering', 'web_links', 'profile_work', 'controllers', 'creator', 'history',
                      'location_details',
                      'member_stats', 'moderators', 'page_members', 'posting_stats', 'rules', 'type', 'work',
                      'countries_involved', 'statistics', 'entity', 'family', 'films', 'games', 'general_information',
                      'likes', 'media_links', 'music', 'notes', 'questions', 'data_mining', 'reviews', 'sports',
                      'tv_programmes', 'honors', 'all', 'popular', 'new', 'address', 'creation_date', 'dnssec',
                      'updated_date',
                      'domain_information',
                      'heading', 'headings', 'images', 'links', 'name_servers', 'nets', 'paragraphs', 'span', 'status',
                      'domain_name',
                      'emails', 'expiration_date', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7',
                      'karma_points', 'data_mining', 'analytics', 'generic_crawler_creation_date',
                      'generic_crawler_dnssec', 'generic_crawler_domain_name',
                      'generic_crawler_emails', 'generic_crawler_expiration_date', 'generic_crawler_heading',
                      'generic_crawler_headings', 'generic_crawler_images', 'generic_crawler_links',
                      'generic_crawler_name_servers', 'generic_crawler_nets', 'generic_crawler_paragraphs',
                      'generic_crawler_span', 'generic_crawler_status', 'generic_crawler_target_information',
                      'generic_crawler_updated_date']


# GENERIC_KEYBASE_INDEX_LIST = ['generic_crawler_creation_date', 'generic_crawler_dnssec', 'generic_crawler_domain_name',
#                               'generic_crawler_emails', 'generic_crawler_expiration_date', 'generic_crawler_heading',
#                               'generic_crawler_headings', 'generic_crawler_images', 'generic_crawler_links',
#                               'generic_crawler_name_servers', 'generic_crawler_nets', 'generic_crawler_paragraphs',
#                               'generic_crawler_span', 'generic_crawler_status', 'generic_crawler_target_information',
#                               'generic_crawler_updated_date'
# ]

SERVER_CODE = (
    ("0", _("Successful! target added")),
    ("1", _("Failed! target not added")),
    ("2", _("Successful! target complete")),
    ("3", _("Failed! target not complete")),
    ("4", _("Successful!  AI job create")),
    ("5", _("Failed!  AI job not created")),
    ("10", _("API request received")),
    ("11", _("Failed! Invalid request")),
    ("12", _("Successful! Task assign to micro-crawler")),
    ("13", _("Failed! to assign to micro-crawler")),
    ("20", _("API request received")),
    ("21", _("Failed! Invalid request")),
    ("22", _("Successful! Target queued")),
    ("24", _("crawling start")),
    ("23", _("crawling Failed")),
    ("26", _("crawling complete")),
    ("28", _("media files Uploading Start")),
    ("30", _("media files Uploading Complete")),
    ("25", _("media files Uploading Failed")),
    ("27", _("Failed! data not store to BDS")),
    ("32", _("Successful! data store to BDS ")),
    ("40", _("Successful! Data extracted from ES")),
    ("43", _("Failed! Resources not allocated to job")),
    ("42", _("Successful!  data processed")),
    ("44", _("Successful!  processed results saved in ES")),
    ("47", _("ES communication failed")),
    ("45", _("Data doesn't exist in ES ")),
    ("49", _("Failed! Parameters missing in Request")),
    ("51", _("Failed! data processing failed")),
    ("66", _("Successful! BDS received data")),
    ("61", _("Failed! GTR doesn't exist in data")),
    ("60", _("Successful! GTR received")),
    ("63", _("Failed! Target identification failed")),
    ("64", _("Successful! Target backup saved")),
    ("65", _("Failed! Target backup not saved")),
    ("62", _("Successful! Target Transformed successfully")),
    ("67", _("Failed! Target Transformion failed")),
    ("53", _("Failed! processed data not loaded in ES")),
    # ("71", _("AI Operations Called")),
    # ("72", _("AI Operations Failed")),
    # ("73", _("AI Operations Completed")),
    )




NEW_SERVER_CODE = (
    ("0", _("Target Marked")),# Successful! target added 11111111111111111111
    # ("1", _("Failed! target not added")), # ------
    # ("2", _("Successful! target complete")), # ------
    # ("3", _("Failed! target not complete")), # -----
    # ("4", _("Successful!  AI job create")), # ------
    # ("5", _("Failed!  AI job not created")), # ------
    # ("10", _("API request received")),#
    # ("11", _("Failed! Invalid request")), # - -------------
    ("12", _("Crawling Started")),# # Successful! Task assign to micro-crawler 222222222222222222222
    ("13", _("Crawling Started")), #Failed! to assign to micro-crawler   333333333333333
    # ("20", _("API request received")), # are been use
    # ("21", _("Failed! Invalid request")), # ------
    # ("22", _("Successful! Target queued")), # are been use
    ("24", _("Crawling Started")),# crawling start 222222222222222222222
    ("23", _("Crawling Failed")), #crawling Failed   333333333333333
    ("26", _("Crawling Completed")),# crawling complete 333333333333333333333333
    ("28", _("JSON Moved in Data Directory")),# media files Uploading Start 5555555555555555555555555555555
    ("30", _("JSON Moved in Data Directory")), #media files Uploading Complete 5555555555555555555555555555
    # ("25", _("media files Uploading Failed")), # ------
    # ("27", _("Failed! data not store to BDS")), # -----
    ("32", _("JSON Stored in HDFS")),# Successful! data store to BDS 44444444444444444444444444444
     ("40", _("AI Operations Called")),#  are been use sometime # 888888888
     ("43", _("AI Operations Failed")), # ----------------- # 9999999999999999
     ("42", _("AI Operations Completed")),# are been use sometime # 99999
    ("44", _("Data Transformed to Elastic Search")),# Successful!  processed results saved in ES 6666666666666666666666666666666
    # ("47", _("ES communication failed")),  # are been use sometime
    # ("45", _("Data doesn't exist in ES ")), # ---------
     ("49", _("AI Operations Failed")), # 9999999999999999
     ("51", _("AI Operations Failed")), # 9999999999999999
    # ("66", _("Successful! BDS received data")),
    ("61", _("Crawling Failed")), # Failed! GTR doesn't exist in data 33333333333333333333
    # ("60", _("Successful! GTR received")),
    ("63", _("Crawling Failed")), # Failed! Target identification failed 33333333333333333333
    # ("64", _("Successful! Target backup saved")),
    # ("65", _("Failed! Target backup not saved")),
    ("62", _("Target Data displayed in App")), # Successful! Target Transformed successfully 777777777777777777777777
    # ("67", _("Failed! Target Transformion failed")),
   ("53", _("AI Operations Failed")), # 9999999999999999
    # ("71", _("AI Operations Called")), # 9999999999999999
    # ("72", _("AI Operations Failed")), # 99999999999999
    # ("73", _("AI Operations Completed")), # 88888888888888888888888888 
  )


target_status_dic ={"0":"1","12":"2","24":"2","23":"3","26":"3","13":"3", "61":"3", "63":"3", "32":"4","28":"5","30":"5","44":"6","62":"7","42":"9","53":"9","51":"9","49":"9","40":"8","43":"9"}

auto_update_status_dic = {"0":"1","12":"2","24":"2","26":"3","32":"4","28":"5","30":"5","44":"6","62":"7","40":"8","42":"9"}