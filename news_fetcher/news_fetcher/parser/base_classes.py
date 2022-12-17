from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class NewsDataclass:
    title: str
    link: str


class BaseParser(ABC):
    BASE_URL: str
    SOURCE_NAME: str
    page: int
    headers: dict = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
    }

    @abstractmethod
    def get_news(self, num_links: int) -> list[NewsDataclass]:
        pass

    @abstractmethod
    def _get_news_from_page(self) -> list[NewsDataclass]:
        pass
