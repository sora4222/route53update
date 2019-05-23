#!/bin/python3
"""
This module is to create a python version of the
:author: Jesse Ross
"""
import boto3
from config.yaml import Config
from logging_dec import message_formatter
import logging
from urllib.request import urlopen
import dns.resolver
import re


def is_ip_address(to_test: str):
    return re.match("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", to_test)


def get_external_ip() -> str:
    """
    Obtains the external ip address
    :return: the external ip address as a string
    """
    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = ["208.67.222.222", "208.67.220.220"]

    ip = str(resolver.query('myip.opendns.com')[0])

    logging.info(message_formatter(("external ip", ip)))

    # This checks it is a matching ipv4
    if not is_ip_address():
        ip_backup = urlopen('http://ip.42.pl/raw').read()
        logging.error(("message", "The ip address obtained was not valid"),
                      ("opendns ip address", ip))
        if not is_ip_address():
            logging.error(("message", "The backup ip-address was not valid"),
                          ("ip.42.pl ip address", ip_backup))
        return ip_backup
    return ip


def update_record(recordname: str, ip_external: str):
    route_53_client = boto3.client("route53")
    response = route_53_client.change_resource_record_sets(
        HostedZoneId
    )


def is_ip_same_as_previous(new_ip: str, ip_log_location: str) -> bool:
    try:
        with open(ip_log_location) as ip_file:
            previous_ip = ip_file.read()
            logging.info(("previous ip", previous_ip))
            return previous_ip == new_ip
    # If the file hasn't been found it will be made later
    except FileExistsError or FileNotFoundError as exc:
        logging.warning(("Message", "Ip address log not found"),
                        ("Error", str(exc)),
                        ("Ignorable", "True"))
        return False


if __name__ == '__main__':
    logging.info(message_formatter(("action", "starting process")))
    config = Config("route53update.yaml")

    record: str
    ip: str = get_external_ip()
    # Only run this if the ip-address has changed
    if is_ip_same_as_previous(config.ip_log_location):
        for record in config.records:
            logging.info(message_formatter(("action", f"starting record: {record}")))
            update_record(record, ip)
            logging.info(message_formatter(("action", f"finished record: {record}")))
    else:
        logging.info(message_formatter(("message", "The ip-address has not changed.")))
