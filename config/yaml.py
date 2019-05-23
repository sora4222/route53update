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
            self.zone_id = loader["zone_id"]
            self.ttl = loader["recordset"]
            self.record_type = loader["record_type"]
            self.records: List[str] = [key for key in loader.keys() if key.startswith("recordset")]
            self.ip_log_location: str = loader["ip_log_location"]

        except KeyError as error:
            logging.critical(message_formatter(("message", f"the configuration file is not valid"),
                                               ("error_message", error)))
            exit(1)
        except OSError as error:
            logging.critical(message_formatter(("message", f"A problem with the configuration"),
                                               ("error_message", error)))
