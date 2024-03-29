from itertools import count

import requests
import socket
import xmltodict
from loguru import logger


def get_xml_stream_as_json(xml_url, session=None):
    if not session:
        session = requests
    try:
        req = session.get(xml_url)
    except requests.ConnectionError as e:
        logger.error(f"URL: {xml_url}\nerror:\n{e}")
        return None
    except requests.Timeout as e:
        logger.error(f"URL: {xml_url}\nerror:\n{e}")
        return None
    if req and not req.ok:
        logger.debug(f"Failed to download: {xml_url}")
        return None
    return xmltodict.parse(req.text)


def parsed_time_to_seconds(human_time):
    """
    # 12:44 => number
    """
    if not human_time:
        return None
    time_parts = human_time.split(":")

    def part_to_seconds(part, order): return int(part) * pow(60, order)

    return sum(map(part_to_seconds, reversed(time_parts), count()))


def convert_str_to_number(x):
    total_stars = 0
    num_map = {'K': 1000, 'M': 1000000, 'B': 1000000000}
    x = x.replace(",", ".")
    if x.isdigit():
        total_stars = int(x)
    else:
        if len(x) > 1:
            total_stars = float(x[:-1]) * num_map.get(x[-1].upper(), 1)
    return int(total_stars)


def is_connected():
    REMOTE_SERVER = "one.one.one.one"
    try:
        # see if we can resolve the host name -- tells us if there is
        # a DNS listening
        host = socket.gethostbyname(REMOTE_SERVER)
        # connect to the host -- tells us if the host is actually
        # reachable
        s = socket.create_connection((host, 80), 2)
        s.close()
        return True
    except:
        pass
