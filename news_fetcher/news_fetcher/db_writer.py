from loguru import logger
from peewee import Database, Model
from slugify import slugify

from .models import News, NewsSource, db
from .parser.base_classes import BaseParser, NewsDataclass


class DBWriter:
    db: Database = db
    models: list[Model] = [
        News,
        NewsSource
    ]

    def create_tables(self) -> None:
        self.db.create_tables(models=self.models)

    @staticmethod
    def insert_news_sources(parsers: list[type(BaseParser)]) -> None:
        for parser in parsers:
            NewsSource.get_or_create(
                name=parser.SOURCE_NAME,
                slug=slugify(parser.SOURCE_NAME),
                link=parser.BASE_URL
            )

    @staticmethod
    def insert_news(news: list[NewsDataclass], parser: BaseParser) -> None:
        news_source = NewsSource.get(slug=slugify(parser.SOURCE_NAME))
        inserted_count = 0

        for n in news:
            _, created = News.get_or_create(
                title=n.title,
                news_source=news_source,
                link=n.link
            )
            inserted_count += created

        logger.info(f'Inserted {inserted_count} rows')

