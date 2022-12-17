import requests

from loguru import logger
from bs4 import BeautifulSoup
from datetime import datetime

from .base_classes import NewsDataclass, BaseParser
from .request_decorators import delay_request, retry


class CNewsParser(BaseParser):
    SOURCE_NAME: str = 'CNews'
    BASE_URL: str = 'https://www.cnews.ru/'
    page_path: str

    def get_news(self, num_links: int) -> list[NewsDataclass]:
        logger.info(f'Start scraping {self.SOURCE_NAME}')
        links = list()
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.page_path = f'main/more_lenta/{current_datetime}'

        while len(links) < num_links:
            logger.debug(f'Get post links from {self.page_path} page')
            page_links = self._get_news_from_page()
            logger.debug(f'Found {len(page_links)} links')
            if not page_links:
                break

            links.extend(page_links)

        num_links = min(num_links, len(links))

        return links[:num_links]

    @retry(3)
    @delay_request(3)
    def _get_news_from_page(self) -> list[NewsDataclass]:
        response = requests.get(url=self.BASE_URL + self.page_path, headers=self.headers)
        soup = BeautifulSoup(response.text, 'lxml')
        logger.debug(f'Page path {self.page_path}')

        news_posts = soup.find_all(class_='allnews_item')
        news_list = [NewsDataclass(tag.a.text, tag.a['href']) for tag in news_posts]
        self.page_path = soup.find('a', class_='read_more_btn')['href']
        logger.debug(f'New page_page {self.page_path}')

        return news_list

