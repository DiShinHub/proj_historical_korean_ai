import base64
import hashlib
import hmac
import secrets
import uuid
from datetime import datetime

import pytz

from app.tool.log_tool import LogTool


class ClientAuthenticationModule:
    __logger = LogTool.get_logger(__qualname__)

    __default_hmac_algorithm = "sha512"
    __default_timezone = "Asia/Seoul"
    __default_datetime_format = "%Y-%m-%dT%H:%M:%S.%f%z"

    def __init__(
            self,
            hmac_algorithm: str = None,
            timezone: str = None,
            datetime_format: str = None,
    ):
        self.__default_hmac_algorithm = hmac_algorithm if hmac_algorithm else self.__default_hmac_algorithm
        self.__default_timezone = timezone if timezone else self.__default_timezone
        self.__default_datetime_format = datetime_format if datetime_format else self.__default_datetime_format

    def generate_iso8601_time_from_current(self) -> str:
        return datetime.now(tz=pytz.timezone(zone=self.__default_timezone)).strftime(self.__default_datetime_format)

    def generate_iso8601_time_from_datetime(self, time: datetime) -> str:
        return time.astimezone(tz=pytz.timezone(zone=self.__default_timezone)).strftime(self.__default_datetime_format)

    def convert_to_datetime(self, time_str: str) -> datetime:
        return datetime.strptime(time_str, self.__default_datetime_format).astimezone(
            pytz.timezone(zone=self.__default_timezone))

    def generate_hmac(
            self,
            secret_key: str,
            access_id: str,
            time_str: str,
            http_method: str,
            url: str,
            body: str | None = None
    ) -> bytes | None:
        """
        Generate HMAC.

        :param secret_key: Secret key for HMAC
        :param access_id: Access ID
        :param time_str: Current time (e.g., ISO8601 format)
        :param http_method: HTTP method Upper Case (e.g., GET, POST)
        :param url: Request URL With Query Params
        :param body: Request body (optional)
        :return: HMAC
        """
        body_cleaned = "" if body is None else body.replace("\r\n", "\n")
        data = f"{http_method} {url}\n{time_str}\n{access_id}\n{body_cleaned}"
        try:
            hmac_digest = hmac.new(
                secret_key.encode("utf-8"),
                data.encode("utf-8"),
                getattr(hashlib, self.__default_hmac_algorithm)
            ).digest()
            return hmac_digest
        except Exception as e:
            self.__logger.error(f"Error Generate HMAC: {e}")
            return None

    def encode_base64(self, target_bytes: bytes, url_safe=True) -> str:
        if url_safe:
            return base64.urlsafe_b64encode(target_bytes).decode("utf-8").rstrip("=")
        else:
            return base64.b64encode(target_bytes).decode("utf-8")

    def decode_base64(self, encoded_str: str, url_safe=True) -> bytes | None:
        try:
            missing_padding = len(encoded_str) % 4
            if missing_padding:
                encoded_str += "=" * (4 - missing_padding)
            encoded_bytes = encoded_str.encode("utf-8")
            decoded_bytes = base64.urlsafe_b64decode(encoded_bytes) if url_safe else base64.b64decode(encoded_bytes)
            return decoded_bytes
        except Exception as e:
            self.__logger.error(f"Error Decode Base64: {e}")
            return None

    @staticmethod
    def generate_access_id() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def generate_secret_key_fixed_for_sha256():
        return secrets.token_hex(32)

    @staticmethod
    def generate_secret_key_fixed_for_sha512():
        return secrets.token_hex(64)
