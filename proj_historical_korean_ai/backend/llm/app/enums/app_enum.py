from enum import Enum


class AppEnum:

    class ActiveEnv(str, Enum):
        PRODUCTION = "prd"
        STAGING = "stg"
        DEVELOPMENT = "dev"
        LOCAL = "local"

        def __str__(self) -> str:
            return str(self.value)
