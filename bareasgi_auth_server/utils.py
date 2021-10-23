"""Utilities"""

from datetime import datetime, timezone
from json import JSONEncoder


class JSONEncoderEx(JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime):
            return o.astimezone(timezone.utc).isoformat()
        return JSONEncoder.default(self, o)
