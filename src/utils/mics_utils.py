import datetime


def format_time(time_seconds: float) -> str:
    return str(datetime.datetime.fromtimestamp(time_seconds))
