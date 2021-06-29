import requests
import xmltodict
from loguru import logger


def get_xml_stream_as_json(xml_url, session=None):
    if not session:
        session = requests
    req = session.get(xml_url)
    if not req.ok:
        logger.debug(f"Failed to download: {xml_url}")
        return None
    return xmltodict.parse(req.text)
