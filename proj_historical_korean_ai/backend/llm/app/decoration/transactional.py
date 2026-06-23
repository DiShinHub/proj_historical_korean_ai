import uuid
from functools import wraps

from app.config.database_config.database_config_repository import get_scoped_session
from app.repository.context_repository import context_repository


class Transactional:

    def __init__(self, readonly=False, join=False):
        self.readonly = readonly
        self.join = join

    def __call__(self, function):
        @wraps(function)
        async def decorator(*args, **kwargs):

            context_repository.set_use_transactional()

            transaction_id = None
            if not self.join:
                transaction_id = str(uuid.uuid4())
                context_repository.add_transaction_ids(transaction_id=transaction_id)

            scoped_session = get_scoped_session()

            async with scoped_session() as session:
                try:
                    # result = await function(*args, **kwargs, session=session)
                    result = await function(*args, **kwargs)
                    if not self.readonly and not self.join:
                        await session.commit()
                    return result
                except Exception as e:
                    if not self.readonly and not self.join:
                        await session.rollback()
                    raise e
                finally:
                    if not self.join and transaction_id:
                        context_repository.remove_transaction_ids(transaction_id=transaction_id)

        return decorator
