from datetime import datetime


def message_formatter(*args) -> str:
    """
    Timestamps each log and converts it to a JSON.
    :param args: Tuples of keys and values
    :return:
    """
    now_val = datetime.now()
    to_log = "{ "
    to_log = to_log + "\"date_time\": \"" + now_val.strftime("%Y %m %d %H %M %S %f") + "\""
    for key, value in args:
        to_log += ", "
        to_log += f"\"{key}\": \"{value}\""
    to_log += "}"
    return to_log
