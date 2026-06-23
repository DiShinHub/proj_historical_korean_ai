from datetime import datetime

import pytz
from sqlalchemy import inspect

from app.constant.app_properties import app_properties


class SqlTool:

    @staticmethod
    def base_to_dict(obj):
        if obj is None:
            return None
        serialized_data = {}
        for column in inspect(obj).mapper.column_attrs:
            value = getattr(obj, column.key)
            if isinstance(value, datetime):
                serialized_data[column.key] = value.astimezone(pytz.timezone(app_properties.TIMEZONE)).isoformat()
            else:
                serialized_data[column.key] = value
        return serialized_data
