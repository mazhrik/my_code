
# from celery.utils.log import get_task_logger
# from celery.task import periodic_task
# from celery.schedules import crontab
# from core_management.views import BigView
#
# bv = BigView()
#
# @periodic_task(run_every=(crontab(minute=0.15)), name='periodic_general_task')
# def periodic_general_task():
#     print("______Perodic Interval_______________")
#
#     bv.news_crawl()
#     bv.google_world_trends()
#     bv.covid_data_get()
#     bv.reddit_trends()
#     bv.trends_crawl()
