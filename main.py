from common import config
from requests.exceptions import HTTPError
from urllib3.exceptions import MaxRetryError
import argparse
import logging
import news_page_objects as news
import re
import datetime
import csv



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

is_well_formed_link = re.compile(r'^https?://.+/.+$')
is_root_path = re.compile(r'^/.+$')

def _news_scraper(news_site_uid):
    host = config()['news_sites'][news_site_uid]['url']
    logging.info('Beginning scraper for {}'.format(host))
    homepage = news.HomePage(news_site_uid, host)
    articles=[]
    for link in homepage.article_links:
       article_page = _fetch_article(news_site_uid, host, link)
       if(article_page):
            logger.info('Article fetched!!')
            articles.append(article_page)
            break
    _save_articles(news_site_uid, articles)

def _save_articles(news_site_uid, articles):
    now = datetime.datetime.now().strftime('%Y_%m_%d')
    out_file_name = '{news_site_uid}_{datetime}_articles.csv'.format(
        news_site_uid=news_site_uid,
        datetime=now
    )
    csv_headers = list(filter(lambda property: not property.startswith('_'), dir(articles[0])))
    with open(out_file_name, mode='w+', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(csv_headers)
        for article in articles:
            row = [str(getattr(article, prop)) for prop in csv_headers]
            writer.writerow(row)

def _fetch_article(news_site_uid, host, link):
    logger.info('Start fetching article at {}'.format(link))
    article = None
    try:
        article_page = news.ArticlePage(news_site_uid, _build_link(host, link))
    except (HTTPError, MaxRetryError) as e:
        logger.warning('Error while fetching the article', exc_info=False)
    
    if article_page and not article_page.content or not article_page.title or not article_page.date:
        logger.warning('Invalid article. There is no valid article (no content, no title)')
        return None
    return article_page

def _build_link(host, link):
    if is_well_formed_link.match(link):
        return link
    if(is_root_path.match(link)):
        return '{}{}'.format(host, link)
    return '{host}/{uri}'.format(host=host,uri=link)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    news_site_choices = list(config()['news_sites'].keys())
    parser.add_argument('news_site', help='The news site that you want to scrape',
                        type=str, choices=news_site_choices)
    args = parser.parse_args()
    _news_scraper(args.news_site)
