import requests
import bs4
from common import config

class NewsPage:

    def __init__(self, news_site_uid, url):
        self._config = config()['news_sites'][news_site_uid]
        self._queries = self._config['queries']
        self._html = None
        self._visit(url)
        self._url = url

    def _visit(self, url):
        response = requests.get(url)
        response.raise_for_status()
        self._html = bs4.BeautifulSoup(response.text, 'html.parser')
    
    def _select(self, query_string):
        return self._html.select(query_string)  

class HomePage(NewsPage):

    def __init__(self, news_site_uid, url):
       super().__init__(news_site_uid, url)

    @property
    def article_links(self):
        link_list=[]
        for queries in self._queries['homepage_article_links']:
            for link in self._select(queries):
                if link and link.has_attr('href'):
                    link_list.append(link)
        return {link['href'] for link in link_list}

class ArticlePage(NewsPage):
    def __init__(self, news_site_uid, url):
        super().__init__(news_site_uid, url)

    @property
    def title(self):
        result = self._select(self._queries['article_title'])
        return result[0].text if len(result) else ''
    @property
    def content(self):
        result = self._select(self._queries['article_content'])
        return result[0].text if len(result) else ''
        #print(result)

    @property
    def date(self):
        result = self._select(self._queries['article_date'])
        return result[0].text if len(result) else ''
        #print(result)
   
