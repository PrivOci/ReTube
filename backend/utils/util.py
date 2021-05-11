import requests
import xmltodict


def get_xml_stream_as_json(xml_url):
    req = requests.get(xml_url)
    if not req.ok:
        return None
    return xmltodict.parse(req.text)
