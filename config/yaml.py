import yaml
import logging
from logging_dec import message_formatter
from typing import List

"""
Tries to make it easy for a configuration to be setup.
"""


class Config(object):
    """
    Loads a configuration into this object.
    """

    def __init__(self, location: str):
        try:
            self.config_location = location
            loader = yaml.safe_load(open(location, 'rb').read())

            self.logging_location: str = loader["logging_location"]
            self.ip_log_location: str = loader["ip_log_location"]
            self.hosted_zone_id: str = loader["hosted_zone_id"]

            # Each of these needs to be fully qualified domain name
            self.records: List[str] = loader["recordset"]

        except KeyError as error:
            print(message_formatter(("message", f"the configuration file is not valid"),
                                    ("error_message", error)))
            exit(1)
        except OSError as error:
            print(message_formatter(("message", f"A problem with the configuration"),
                                    ("error_message", error)))
