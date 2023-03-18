from celery.utils.log import get_task_logger
from celery.task import task
from target_management.periodic_calls import PeriodicCall
from core_management.views import BigView
calls = PeriodicCall()
logger = get_task_logger(__name__)

bv = BigView()

@task(name='periodic_tasks')
def periodic_tasks():
    print("adding target")
    calls.add_target()
    calls.latest_trends()
    calls.latest_news()
    # bv.news_crawl()
    # bv.google_world_trends()
    # bv.covid_data_get()
    # bv.reddit_trends()
    # bv.trends_crawl()
