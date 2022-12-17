import requests

from loguru import logger
from bs4 import BeautifulSoup

from .base_classes import NewsDataclass, BaseParser
from .request_decorators import delay_request, retry


class ComputerWorldParser(BaseParser):
    SOURCE_NAME: str = 'ComputerWorld'
    BASE_URL: str = 'https://www.computerworld.com/'

    def get_news(self, num_links: int) -> list[NewsDataclass]:
        links = list()
        self.page = 1

        while len(links) < num_links:
            logger.info(f'Get post links from {self.page} page')
            page_links = self._get_news_from_page()
            logger.info(f'Found {len(page_links)} links')
            if not page_links:
                break

            links.extend(page_links)
            self.page += 1

        num_links = min(num_links, len(links))

        return links[:num_links]

    @retry(3)
    @delay_request(3)
    def _get_news_from_page(self) -> list[NewsDataclass]:
        page_path = f'napi/tile?def=loadMoreList&pageType=index&typeIds=2%2C7&typeSlug=news&days=-{self.page*40}&pageSize=20&offset={(self.page-1)*20}&ignoreExcludedIds=true&brandContentOnly=false&includeBlogTypeIds=1%2C3&includeVideo=true&liveOnly=true&videoWeight=2&sortOrder=date&locale_id=0&startIndex=20'
        response = requests.get(url=self.BASE_URL + page_path, headers=self.headers)
        soup = BeautifulSoup(response.text, 'lxml')
        logger.info(f'{self.page} page number')

        news_posts = soup.find_all('h3')
        news_list = [NewsDataclass(tag.a.text, self.BASE_URL + tag.a['href']) for tag in news_posts]

        return news_list


