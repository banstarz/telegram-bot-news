import peewee as pw
from datetime import datetime

db = pw.SqliteDatabase('../telegram_bot/telegram.db')


class BaseModel(pw.Model):
    id = pw.PrimaryKeyField(unique=True)

    class Meta:
        database = db


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

