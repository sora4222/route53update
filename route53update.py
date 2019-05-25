#!/bin/python3
"""
This module is to create a python version of the
:author: Jesse Ross
"""
import boto.route53
import boto.route53.record
from config.yaml import Config
from logging_dec import message_formatter
import logging
from urllib.request import urlopen
import dns.resolver
import re
import sys
from typing import Tuple


def is_ip_address(to_test: str):
    return re.match("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", to_test)


def get_external_ip() -> str:
    """
    Obtains the external ip address
    :return: the external ip address as a string
    """
    try:
        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = ["208.67.222.222", "208.67.220.220"]

        ip = str(resolver.query('myip.opendns.com')[0])

        logging.info(message_formatter(("Level", "Info"),
                                       ("External ip", ip)))

        # This checks it is a matching ipv4
        if not is_ip_address(ip):
            ip_backup = urlopen('http://ip.42.pl/raw').read()
            logging.error(message_formatter(
                ("Level", "Error"),
                ("Message", "The ip address obtained was not valid"),
                ("Opendns ip address", ip)))
            if not is_ip_address(ip_backup):
                logging.error(message_formatter(("Level", "Error"),
                                                ("Message", "The backup ip-address was not valid"),
                                                ("Ip.42.pl ip address", ip_backup)
                                                ))
            return ip_backup
        return ip
    except dns.exception.Timeout as exc:
        logging.error(message_formatter(("Level", "Error"),
                                        ("Message", "The DNS has had a timeout exception"),
                                        ("Error", str(exc))))
        exit(1)


def update_record(recordname: str, ip_external: str, zone_id: str):
    """
    Updates A type records to the ip address that is passed in
    with the zone id that the record is assigned to.
    :param recordname:The record name to be passed in must be FQDN like example.com.
    :param ip_external:The ip-address as a string
    :param zone_id:The id of the zone for the hosted zone
    :return:
    """
    try:
        route53_conn = boto.route53.connect_to_region("ap-southeast-2")
        change_record = boto.route53.record.ResourceRecordSets(
            connection=route53_conn, hosted_zone_id=zone_id)
        changes = change_record.add_change(action="UPSERT", name=recordname, type="A")
        changes.add_value(ip_external)
        change_record.commit()
    except (boto.exception.BotoClientError, boto.exception.AWSConnectionError) as exc:
        logging.critical(message_formatter(("Message", "An exception occured setting the update_record"),
                                           ("Error", str(exc)),
                                           ("Level", "Critical")
                                           ))
        exit(1)


def is_ip_same_as_previous(new_ip: str, ip_log_location: str) -> bool:
    """
    Compares the ip address from within the file to the ip address
    given
    :param new_ip: The ip-address
    :param ip_log_location: The location of the ip-address log
    :return: The boolean value on whether the
    """
    try:
        with open(ip_log_location, mode="r") as ip_file:
            previous_ip = ip_file.read()
            logging.info(message_formatter(("Previous ip", previous_ip),
                                           ("Level", "Info")
                                           ))
            return previous_ip == new_ip
    # If the file hasn't been found it will be made later
    except FileNotFoundError as exc:
        logging.warning(message_formatter(
            ("Level", "Warning"),
            ("Message", "Ip address log not found"),
            ("Error", str(exc)),
            ("Ignorable", "True")
        ))
        return False


def write_ip_address_to_file(ip_log_location: str, ip: str):
    try:
        with open(ip_log_location, "w") as ip_file:
            ip_file.write(ip)
            logging.info(message_formatter(
                ("Level", "Info"),
                ("Message", "The file has been written"),
                ("File location", ip_log_location)
            ))
    except OSError as exc:
        logging.critical(message_formatter(
            ("Level", "Critical"),
            ("Message", "The file could not be written"),
            ("File location", ip_log_location),
            ("Error", str(exc))
        ))


def extract_arguments() -> str:
    config_location: str = ""
    try:
        config_location = sys.argv[1]
    except IndexError:
        print("Expected the script to be given the location of the config file")
        exit(1)
    return config_location


if __name__ == '__main__':
    config_location = extract_arguments()
    config = Config(config_location)

    logging.basicConfig(filename=config.logging_location,
                        format='%(message)s',
                        level=logging.INFO)
    logging.info(message_formatter(("Action", "Starting process")))

    record: str
    ip: str = get_external_ip()
    # Only run this if the ip-address has changed
    if not is_ip_same_as_previous(ip, config.ip_log_location):
        for record in config.records:
            logging.info(message_formatter(("Level", "Info"),
                                           ("Action", f"starting update record: {record}")))
            update_record(record, ip, config.hosted_zone_id)
            logging.info(message_formatter(("Level", "Info"),
                                           ("Action", f"finished update record: {record}")))
        write_ip_address_to_file(config.ip_log_location, ip)
    else:
        logging.info(message_formatter(("Level", "Info"),
                                       ("Message", "The ip-address has not changed.")))
