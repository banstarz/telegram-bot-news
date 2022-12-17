import requests

from loguru import logger
from bs4 import BeautifulSoup

from .base_classes import NewsDataclass, BaseParser
from .request_decorators import delay_request, retry


class ItWorldParser(BaseParser):
    SOURCE_NAME: str = 'ITWorld'
    BASE_URL: str = 'https://www.it-world.ru/'

    def get_news(self, num_links: int) -> list[NewsDataclass]:
        logger.info(f'Start scraping {self.SOURCE_NAME}')
        links = list()
        self.page = 1

        while len(links) < num_links:
            logger.debug(f'Get post links from {self.page} page')
            page_links = self._get_news_from_page()
            logger.debug(f'Found {len(page_links)} links')
            if not page_links:
                break

            links.extend(page_links)
            self.page += 1

        num_links = min(num_links, len(links))

        return links[:num_links]

    @retry(3)
    @delay_request(3)
    def _get_news_from_page(self) -> list[NewsDataclass]:
        page_path = f'it-news/?PAGEN_1={self.page}&IBLOCK_CODE=it-news'
        response = requests.get(url=self.BASE_URL + page_path, headers=self.headers)
        soup = BeautifulSoup(response.text, 'lxml')
        page_number = int(soup.find(class_='navigation-n navigation-current').text)
        logger.debug(f'{page_number} page number')
        if self.page != page_number:
            logger.debug('We out')
            return list()

        news_posts = soup.find(class_='load-list').find_all(class_='news__content')
        news_list = [NewsDataclass(tag.a.text, self.BASE_URL + tag.a['href'][1:]) for tag in news_posts]

        return news_list
