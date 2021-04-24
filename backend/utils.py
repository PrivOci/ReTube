import requests
import xmltodict

async def get_xml_stream_as_json(xml_url):
    req = requests.get(xml_url)
    return xmltodict.parse(req.text)