from loguru import logger
import random

from .base_classes import NewsDataclass, BaseParser


class FakeParser(BaseParser):
    SOURCE_NAME: str = 'FakeSource'
    BASE_URL: str = 'fake_source::fake_link'

    def get_news(self, num_links: int) -> list[NewsDataclass]:
        news_number = random.randint(0, 10000000)
        news_list = [NewsDataclass(f'Fake New number {news_number}', f'{self.BASE_URL}::{news_number}')]

        return news_list

    def _get_news_from_page(self) -> list[NewsDataclass]:
        pass
