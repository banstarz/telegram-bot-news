import peewee as pw
from datetime import datetime

db = pw.SqliteDatabase('people.db')


class BaseModel(pw.Model):
    id = pw.PrimaryKeyField(unique=True)

    class Meta:
        database = db


class User(BaseModel):
    chat_id = pw.CharField()
    is_active = pw.BooleanField(default=True)
    limit_news = pw.SmallIntegerField(default=5)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return 'User ' + self.chat_id


class NewsSource(BaseModel):
    name = pw.CharField()
    link = pw.CharField()

    class Meta:
        db_table = 'news_sources'
        order_by = 'name'

    def __str__(self):
        return 'News Source: ' + self.name


class News(BaseModel):
    title = pw.CharField()
    created = pw.DateTimeField(default=datetime.now)
    news_source = pw.ForeignKeyField(NewsSource, on_delete='CASCADE')
    link = pw.CharField()

    class Meta:
        db_table = 'news'
        order_by = ('-created',)

    def __str__(self):
        return 'News: ' + self.title[:10]


class UserNewsSource(BaseModel):
    user = pw.ForeignKeyField(User, on_delete='CASCADE')
    news_source = pw.ForeignKeyField(NewsSource, on_delete='CASCADE')

    class Meta:
        db_table = 'user__news_source'

    def __str__(self):
        return f'({str(self.user)} <-> {str(self.news_source)})'


class UserViewedNews(BaseModel):
    user = pw.ForeignKeyField(User, on_delete='CASCADE')
    news = pw.ForeignKeyField(News, on_delete='CASCADE')

    class Meta:
        db_table = 'user_viewed_news'

    def __str__(self):
        return f'({str(self.user)} <-> {str(self.news)})'


def get_not_viewed_news(chat_id: str, news_source_name: str) -> list[News]:
    all_user_news = News.select().join(NewsSource).where(NewsSource.name == news_source_name)
    viewed_news = News.select().join(UserViewedNews).join(User).where(User.chat_id == chat_id)
    not_viewed_news = all_user_news - viewed_news
    return list(not_viewed_news)


def get_not_followed_sources(chat_id: str) -> list[NewsSource]:
    all_news_source = NewsSource.select()
    user_news_source = NewsSource.select().join(UserNewsSource).join(User).where(User.chat_id == chat_id)
    not_followed_sources = all_news_source - user_news_source
    return list(not_followed_sources)


def get_followed_sources(chat_id: str) -> list[NewsSource]:
    user_news_source = NewsSource.select().join(UserNewsSource).join(User).where(User.chat_id == chat_id)
    return list(user_news_source)


def get_news(chat_id: str, news_source_name: str) -> list[News]:
    user_limit_news = User.get(User.chat_id == chat_id).limit_news
    news_source = NewsSource.get(NewsSource.name == news_source_name)
    news = News.select().join(NewsSource).where(NewsSource.id == news_source.id).limit(user_limit_news)
    return list(news)
