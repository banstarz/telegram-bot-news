import os

import schedule
import time
from loguru import logger

from news_fetcher.db_writer import DBWriter
from news_fetcher.parser.cnews_parser import CNewsParser
from news_fetcher.parser.computerworld_parser import ComputerWorldParser
from news_fetcher.parser.it_world_parser import ItWorldParser
from news_fetcher.parser.fake_parser import FakeParser


def put_prepared_news():
    parser = parsers[-1]
    news = parser.get_prepared_news()
    writer.insert_news(news, parser)


def fetch_news():
    logger.info('Start fetching news')
    for parser in parsers:
        news = parser.get_news(16)
        writer.insert_news(news, parser)

    logger.info('News fetched. Going to sleep')


parsers = [
    CNewsParser(),
    ComputerWorldParser(),
    ItWorldParser(),
]

if os.environ.get('START_FAKE_NEWS_SOURCE'):
    parsers.append(FakeParser())

writer = DBWriter()
writer.insert_news_sources(parsers)

if os.environ.get('START_FAKE_NEWS_SOURCE'):
    put_prepared_news()

schedule.every(1).minutes.do(fetch_news)
logger.info('News-fetcher started')

while True:
    schedule.run_pending()
    time.sleep(10)
