from models import User, News, NewsSource, UserNewsSource, UserAction, db
from telegram.ext import Updater
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import CommandHandler, RegexHandler, MessageHandler
from telegram.ext.filters import Filters
import logging
import os

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class BaseNewsSourcesCommandResponder:

    def __init__(
            self,
            update: Update,
            context: CallbackContext,
            command: str
    ):
        self.update = update
        self.context = context
        self.command = command
        self.has_news_source = None
        self.news_source_slug = None
        self._parse_source_from_command()
        self.news_sources = []
        self._prepare_news_sources_if_needed()

    def _parse_source_from_command(self):
        if self.update.message.text == self.command:
            self.has_news_source = False
        else:
            self.has_news_source = True
            self.news_source_slug = self.update.message.text.replace(f'{self.command}_', '')

    def send_news_sources(self) -> None:
        log_user_action(self.update)

        for news_source in self.news_sources:
            text = f'{self.command}_{news_source.slug}'
            self.context.bot.send_message(chat_id=self.update.effective_chat.id, text=text)

    def _prepare_news_sources_if_needed(self) -> None:
        if self.has_news_source:
            return

        self._prepare_relevant_news_sources()


class FollowSourceResponder(BaseNewsSourcesCommandResponder):
    def follow_source(self):
        user = User.get(chat_id=self.update.effective_chat.id)
        news_source = NewsSource.get(slug=self.news_source_slug)

        _, is_saved = UserNewsSource.get_or_create(user=user, news_source=news_source)

        log_user_action(self.update, bool(is_saved))

        if is_saved:
            text = f'Подписка осуществлена успешно'
            self.context.bot.send_message(chat_id=self.update.effective_chat.id, text=text)

    def _prepare_relevant_news_sources(self):
        all_news_source = NewsSource.select()
        user_news_source = NewsSource.select()\
            .join(UserNewsSource).join(User)\
            .where(User.chat_id == self.update.effective_chat.id)
        not_followed_sources = all_news_source - user_news_source
        self.news_sources = list(not_followed_sources)


class UnfollowSourceResponder(BaseNewsSourcesCommandResponder):
    def unfollow_source(self):
        user_id = User.get(chat_id=self.update.effective_chat.id).chat_id
        news_source_id = NewsSource.get(slug=self.news_source_slug).id

        is_deleted = UserNewsSource\
            .get(UserNewsSource.user == user_id, UserNewsSource.news_source == news_source_id)\
            .delete_instance()

        log_user_action(self.update, bool(is_deleted))

        if is_deleted:
            text = f'Отписка осуществлена успешно'
            self.context.bot.send_message(chat_id=self.update.effective_chat.id, text=text)

    def _prepare_relevant_news_sources(self):
        followed_news_sources = NewsSource.select()\
            .join(UserNewsSource)\
            .join(User)\
            .where(User.chat_id == self.update.effective_chat.id)
        self.news_sources = list(followed_news_sources)


class FromSourceResponder(BaseNewsSourcesCommandResponder):
    def send_source_news(self):
        most_recent_news = self.get_news()

        log_user_action(self.update)

        for news in most_recent_news:
            text = f'{news.title}\n{news.link}'
            self.context.bot.send_message(chat_id=self.update.effective_chat.id, text=text)

    def get_news(self) -> list[News]:
        user_limit_news = User.get(chat_id=self.update.effective_chat.id).limit_news
        news_source = NewsSource.get(slug=self.news_source_slug)
        news = News.select()\
            .join(NewsSource)\
            .where(NewsSource.id == news_source.id)\
            .limit(user_limit_news)
        return list(news)

    def _prepare_relevant_news_sources(self):
        all_news_sources = NewsSource.select()
        self.news_sources = list(all_news_sources)


def start(update: Update, context: CallbackContext):
    text = """
    Новостной телеграм бот
    /from_source[_title] - получить n новостей из источника title. Если title не указан - вывод всех источников
    /update_n n - изменить количество новостей n, которые выгружаются за один раз командой /from_source
    /follow_source[_title] - подписаться на уведомления о новых новостях источника title. Если title не указан - 
    список всех источников
    /unfollow_source[_title] - отписаться от уведомлений о новых новостях источника title. Если title не указан - 
    список всех источников
    """
    User.get_or_create(chat_id=update.effective_chat.id)
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    log_user_action(update)


def update_n(update: Update, context: CallbackContext):
    user = User.get(chat_id=update.effective_chat.id)
    if not context.args:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Пожалуйста введите число от 1 до 15")
        return
    limit_news = context.args[0]

    try:
        limit_news = int(limit_news)
    except:
        text = 'Пожалуйста введите число от 1 до 15'
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        log_user_action(update, is_success=False)
    else:
        user.limit_news = limit_news
        user.save()
        context.bot.send_message(chat_id=update.effective_chat.id, text="Успешно обновлено")
        log_user_action(update)


def from_source(update: Update, context: CallbackContext):
    command_text = '/from_source'
    responder = FromSourceResponder(
        update,
        context,
        command_text
    )
    if responder.has_news_source:
        responder.send_source_news()
    else:
        responder.send_news_sources()


def follow_source(update: Update, context: CallbackContext):
    command_text = '/follow_source'
    responder = FollowSourceResponder(
        update,
        context,
        command_text
    )
    if responder.has_news_source:
        responder.follow_source()
    else:
        responder.send_news_sources()


def unfollow_source(update: Update, context: CallbackContext):
    command_text = '/unfollow_source'
    responder = UnfollowSourceResponder(
        update,
        context,
        command_text
    )
    if responder.has_news_source:
        responder.unfollow_source()
    else:
        responder.send_news_sources()


def usual_message(update: Update, context: CallbackContext):
    log_user_action(update, is_command=False)


def send_news_sources_with_command(
        update: Update,
        context: CallbackContext,
        news_sources: list[NewsSource],
        command: str
):
    for news_source in news_sources:
        text = f'{command}_{news_source.slug}'
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def auto_send_news(context: CallbackContext):
    news = News.select().where(News.is_checked == False)
    for n in news:
        for user_news_source in n.news_source.user_news_sources:
            chat_id = user_news_source.user.chat_id
            text = f'{n.title}\n{n.link}'
            context.bot.send_message(chat_id=chat_id, text=text)
        n.is_checked = True
        n.save()


def log_user_action(update: Update, is_command: bool = True, is_success: bool = True):
    UserAction.create(
        user=update.effective_chat.id,
        message=update.message.text,
        is_success=is_success,
        is_command=is_command,
    )

    logger.info(f'New action {UserAction}')


if __name__ == '__main__':
    models = [
        User,
        NewsSource,
        News,
        UserNewsSource,
        UserAction,
    ]

    db.create_tables(models=models)

    updater = Updater(token=os.environ.get('SECRET_KEY'), use_context=True)
    dispatcher = updater.dispatcher
    updater.job_queue.run_repeating(callback=auto_send_news, interval=60)

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(RegexHandler('^(/from_source(_[\w]+)?)$', from_source))
    dispatcher.add_handler(CommandHandler('update_n', update_n))
    dispatcher.add_handler(RegexHandler('^(/follow_source(_[\w]+)?)$', follow_source))
    dispatcher.add_handler(RegexHandler('^(/unfollow_source(_[\w]+)?)$', unfollow_source))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, usual_message))

    updater.start_polling()
    updater.idle()
