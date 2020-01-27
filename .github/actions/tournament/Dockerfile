FROM python:3.6-alpine

RUN set -x \
  && apk add --no-cache bash git

RUN set -x \
  && pip install pipenv

COPY docker-entrypoint.sh /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
