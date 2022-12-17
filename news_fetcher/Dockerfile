FROM python:3.10-alpine

WORKDIR /usr/src/news_fetcher

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY entrypoint.sh .
RUN sed -i 's/\r$//g' /usr/src/news_fetcher/entrypoint.sh
RUN chmod +x /usr/src/news_fetcher/entrypoint.sh

COPY news_fetcher .

ENTRYPOINT ["/usr/src/news_fetcher/entrypoint.sh"]