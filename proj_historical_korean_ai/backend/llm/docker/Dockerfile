FROM python:3.11.7

SHELL ["/bin/bash", "-c"]

ENV APP_ACTIVE_ENV=${FASTAPI_APP_ACTIVE_ENV}
ENV APP_PORT=8001
ENV APP_LOG_LOCATION=logs

ENV TZ=Asia/Seoul
ENV APP_PATH=/apps

EXPOSE ${APP_PORT}

COPY . ${APP_PATH}
WORKDIR ${APP_PATH}

RUN rm -rf ${APP_PATH}/test
RUN rm -rf ${APP_PATH}/logs

ENV POETRY_HOME /usr/local
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/usr/local python3 -

RUN poetry install
CMD poetry run uvicorn --host 0.0.0.0 --port ${APP_PORT} app.main:app
