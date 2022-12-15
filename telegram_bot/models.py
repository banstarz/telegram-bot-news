import peewee as pw
from datetime import datetime


db = pw.SqliteDatabase('telegram.db')


class BaseModel(pw.Model):
    id = pw.PrimaryKeyField(unique=True)

    class Meta:
        database = db


class User(pw.Model):
    chat_id = pw.PrimaryKeyField(unique=True)
    is_active = pw.BooleanField(default=True)
    limit_news = pw.SmallIntegerField(default=5)

    class Meta:
        db_table = 'users'
        database = db

    def __str__(self):
        return f'User {self.chat_id}'


class NewsSource(BaseModel):
    name = pw.CharField()
    slug = pw.CharField()
    link = pw.CharField()

    class Meta:
        db_table = 'news_sources'
        order_by = 'name'

    def __str__(self):
        return 'News Source: ' + self.name


class News(BaseModel):
    title = pw.CharField()
    created = pw.DateTimeField(default=datetime.now)
    news_source = pw.ForeignKeyField(NewsSource, on_delete='CASCADE', backref='news')
    link = pw.CharField()
    is_checked = pw.BooleanField(default=False)

    class Meta:
        db_table = 'news'
        order_by = ('-created',)

    def __str__(self):
        return 'News: ' + self.title[:10]


class UserNewsSource(BaseModel):
    user = pw.ForeignKeyField(User, on_delete='CASCADE', backref='user_news_sources')
    news_source = pw.ForeignKeyField(NewsSource, on_delete='CASCADE', backref='user_news_sources')
    last_checked = pw.DateTimeField

    class Meta:
        db_table = 'user__news_source'

    def save(self, *args, **kwargs):
        self.last_checked = datetime.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'({str(self.user)} <-> {str(self.news_source)})'
