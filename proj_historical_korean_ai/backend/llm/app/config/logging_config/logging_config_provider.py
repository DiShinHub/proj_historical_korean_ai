import logging

from app.repository.context_repository import context_repository


class RequestIdLoggingFilter(logging.Filter):

    def filter(self, record):
        record.request_id = context_repository.get_request_id()
        return True
