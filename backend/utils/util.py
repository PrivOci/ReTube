import requests
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
    except requests.Timeout  as e:
        logger.error(f"URL: {xml_url}\nerror:\n{e}")
        return None
    if req and not req.ok:
        logger.debug(f"Failed to download: {xml_url}")
        return None
    return xmltodict.parse(req.text)

# 12:44 => number
def parsed_time_to_seconds(human_time):
    time_parts = human_time.split(":")
    sum = 0
    for count, part in enumerate(reversed(time_parts)):
        part = int(part)
        sum += part if count == 0 else part * pow(60, count)
    return sum