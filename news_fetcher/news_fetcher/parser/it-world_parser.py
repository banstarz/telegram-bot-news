from bs4 import BeautifulSoup
from request_decorators import delay_request, retry
import requests
import logging
from base_classes import News, BaseParser


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class ItWorldParser(BaseParser):
    SOURCE_NAME: str = 'it-world'
    BASE_URL: str = 'https://www.it-world.ru/'

    def get_posts_urls(self, num_links: int) -> list[News]:
        links = list()
        self.page = 1

        while len(links) < num_links:
            logger.info(f'Get post links from {self.page} page')
            page_links = self._get_posts_urls_from_page()
            logger.info(f'Found {len(page_links)} links')
            if not page_links:
                break

            links.extend(page_links)
            self.page += 1

        num_links = min(num_links, len(links))

        return links[:num_links]

    @retry(3)
    @delay_request(3)
    def _get_posts_urls_from_page(self) -> list[News]:
        page_path = f'it-news/?PAGEN_1={self.page}&IBLOCK_CODE=it-news'
        response = requests.get(url=self.BASE_URL + page_path, headers=self.headers)
        soup = BeautifulSoup(response.text, 'lxml')
        page_number = int(soup.find(class_='navigation-n navigation-current').text)
        logger.info(f'{page_number} page number')
        if self.page != page_number:
            logger.info('We out')
            return list()

        news_posts = soup.find(class_='load-list').find_all(class_='news__content')
        news_list = [News(tag.a.text, tag.a['href']) for tag in news_posts]

        return news_list
