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
    except requests.Timeout  as e:
        logger.error(f"URL: {xml_url}\nerror:\n{e}")
    if req and not req.ok:
        logger.debug(f"Failed to download: {xml_url}")
        return None
    return xmltodict.parse(req.text)
