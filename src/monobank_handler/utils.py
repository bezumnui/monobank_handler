import time
from datetime import datetime


def to_timestamp(dtime):
    "Converts datetime to utc timestamp"
    return int(time.mktime(dtime.timetuple()))


def get_utc():
    return int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds())
