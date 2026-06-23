import contextvars
import uuid

from app.base.singleton_meta import SingletonMeta
from app.config.authentication_config.jwt_authentication_provider import UserDetailsDto


class ContextRepository(metaclass=SingletonMeta):
    __context_request_id = contextvars.ContextVar("request_id")
    __context_user_details = contextvars.ContextVar("user_details")
    __context_use_transactional = contextvars.ContextVar("use_transactional")
    __context_transaction_ids = contextvars.ContextVar("transaction_ids")

    def __init__(self):
        pass

    def set_request_id(self):
        self.__context_request_id.set(f"{uuid.uuid4()}")

    def set_user_details(self, user_details: UserDetailsDto):
        self.__context_user_details.set(user_details)

    def set_use_transactional(self, use_transactional: bool = True):
        self.__context_use_transactional.set(use_transactional)

    def add_transaction_ids(self, transaction_id: str = str(uuid.uuid4())):
        self.__context_transaction_ids.set(self.get_transaction_ids() + [transaction_id])

    def remove_transaction_ids(self, transaction_id: str = None):
        if transaction_id is None:
            self.__context_transaction_ids.set(self.get_transaction_ids()[:-1])
        elif transaction_id in self.get_transaction_ids():
            self.__context_transaction_ids.set(
                list(filter(lambda item: item != transaction_id, self.get_transaction_ids()))
            )

    def get_request_id(self) -> str:
        return self.__context_request_id.get("")

    def get_user_details(self) -> UserDetailsDto:
        return self.__context_user_details.get(UserDetailsDto(
            seq=0,
            member_id="",
            member_type_cd=""
        ))

    def get_use_transactional(self) -> bool:
        return self.__context_use_transactional.get(False)

    def get_transaction_ids(self) -> [str]:
        return self.__context_transaction_ids.get([])


context_repository = ContextRepository()
