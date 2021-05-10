import requests
from bs4 import BeautifulSoup
import urllib.parse
import dateparser
from utils import get_xml_stream_as_json
import time
from datetime import datetime
import email.utils
import re

BITCHUTE = "bc"
BITCHUTE_XML = "https://www.bitchute.com/feeds/rss/channel/"


def bitchute_video_details(video_url) -> dict:
    req = requests.get(video_url)
    soup = BeautifulSoup(req.text, 'html.parser')

    # grab cfduid and csrftoken
    # TODO: extract as a class
    session = requests.Session()
    response = session.get('https://www.bitchute.com/help-us-grow/')
    cookies = session.cookies.get_dict()
    cfduid = cookies["__cfduid"]
    csrftoken = cookies["csrftoken"]

    headers = {
        'authority': 'www.bitchute.com',
        'accept': '*/*',
        'dnt': '1',
        'x-requested-with': 'XMLHttpRequest',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.116 Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.bitchute.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': f'{video_url}',
        'accept-language': 'en-US,en-GB;q=0.9,en;q=0.8',
        'cookie': f'__cfduid={cfduid}; csrftoken={csrftoken}; registration=on;',
    }

    data = {
        'csrfmiddlewaretoken': f'{csrftoken}'
    }

    count_req = requests.post(
        'https://www.bitchute.com/video/6uhZnVIkzWyr/counts/', headers=headers, data=data)
    count_json = count_req.json()

    publish_date = soup.find(
        "div", {"class": "video-publish-date"}).text.strip()
    splited_date = publish_date.split(" on ")[1].split()
    date_result = f"{splited_date[0]} {re.sub('[^0-9]','', splited_date[1])} {splited_date[2]}"
    publish_date = datetime.strptime(date_result, '%B %d %Y.').timestamp()

    video_details = {
        "id": video_url.split("/video/")[1].strip().strip('/'),
        "title": soup.find("h1", {"id": "video-title"}).text,
        "description": soup.find("meta", {"name": "description"})["content"],
        "author": soup.find("p", {"class": "owner"}).a.text,
        "channelUrl": "https://bitchute.com" +
        soup.find("p", {"class": "owner"}).a["href"],
        "duration": "",
        "views": count_json["view_count"],
        "average_rating": "",
        "likeCount": count_json["like_count"],
        "dislikeCount": count_json["dislike_count"],
        "subscriberCount": count_json["subscriber_count"],
        "thumbnailUrl": soup.find("video", {"id": "player"})["poster"],
        "createdAt": int(publish_date) * 1000,
        "streamUrl": soup.find("video", {"id": "player"}).source["src"],
    }
    return video_details


def _parse_bitchute_details(entry) -> dict:
    video_entry = {}
    video_entry["thumbnailUrl"] = entry["images"]["thumbnail"]
    video_entry["title"] = entry["name"]
    video_entry["author"] = entry["channel_name"]
    video_entry["views"] = entry["views"]
    video_entry["createdAt"] = ""
    video_entry["videoUrl"] = f"https://bitchute.com{entry['path']}"

    video_entry["platform"] = BITCHUTE
    return video_entry


async def bitchute_search_video(search_query):
    search_terms = search_query["query"]
    max_results = search_query["max"]
    encoded_query = urllib.parse.quote(search_terms)

    data_dict = {}
    data_dict["platform"] = BITCHUTE
    data_dict["ready"] = False
    session = requests.Session()
    # grab cfduid and csrftoken
    response = session.get('https://www.bitchute.com/help-us-grow/')
    cookies = session.cookies.get_dict()
    cfduid = cookies["__cfduid"]
    csrftoken = cookies["csrftoken"]

    headers = {
        'authority': 'www.bitchute.com',
        'accept': '*/*',
        'dnt': '1',
        'x-requested-with': 'XMLHttpRequest',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537 (KHTML, like Gecko) Chrome/89 Safari/537 Edg/89',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.bitchute.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': f'https://www.bitchute.com/search/?query={encoded_query}&kind=video',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': f'__cfduid={cfduid}; csrftoken={csrftoken}; registration=on;',
    }

    data = {
        'csrfmiddlewaretoken': f'{csrftoken}',
        'query': f'{encoded_query}',
        'kind': 'video',
        'duration': '',
        'sort': '',
        'page': '0'
    }

    response = requests.post(
        'https://www.bitchute.com/api/search/list/', headers=headers, data=data)
    response_json = response.json()
    if not response.ok or "success" not in response_json or response_json["success"] != True:
        return data_dict

    video_entries = []
    for entry in response_json["results"]:
        video_entry = _parse_bitchute_details(entry)
        if video_entry:
            video_entries.append(video_entry)

    data_dict["content"] = video_entries
    data_dict["ready"] = True

    return data_dict


async def get_bitchute_channel_source(details: dict) -> dict:
    if details['id'] == "popular":
        return await get_bitchute_popular()
    data_dict = {}
    data_dict["platform"] = BITCHUTE
    popular_rss_url = f"{BITCHUTE_XML}{details['id']}"
    content = await get_xml_stream_as_json(popular_rss_url)
    video_entries = []
    for entry in content["rss"]["channel"]["item"]:
        video_entry = {}
        video_entry["thumbnailUrl"] = entry["enclosure"]["@url"]
        video_entry["title"] = entry["title"]
        video_entry["author"] = details['id']
        video_entry["views"] = ""
        video_entry["createdAt"] = int(time.mktime(
            email.utils.parsedate(entry["pubDate"]))) * 1000
        video_entry[
            "videoUrl"] = f"https://www.bitchute.com/video/{entry['link'].split('/embed/')[1]}"
        video_entry["platform"] = BITCHUTE
        video_entry["channelUrl"] = f"https://www.bitchute.com/channel/{details['id']}"
        video_entries.append(video_entry)

    data_dict["ready"] = True
    data_dict["content"] = video_entries if len(video_entries) else None
    return data_dict


def parsed_time_to_seconds(human_time):
    time_parts = human_time.split(":")
    sum = 0
    for count, part in enumerate(reversed(time_parts)):
        part = int(part)
        sum += part if count == 0 else part * pow(60, count)
    return sum


# Parse Bitchute "listing-popular" section
async def get_bitchute_popular():
    data_dict = {}
    data_dict["ready"] = False
    data_dict["platform"] = BITCHUTE
    target_url = "https://www.bitchute.com"
    res = requests.get(target_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    content_section = soup.find("div", {"id": "listing-popular"}).div

    video_entries = []
    for block in content_section:
        video_entry = {}
        if not hasattr(block, 'div'):
            continue

        video_entry["thumbnailUrl"] = block.find("img", src=True)[
            "data-src"].strip()

        video_entry["title"] = block.find(
            "p", {"class": "video-card-title"}).a.text.strip()
        video_entry["author"] = block.find(
            "p", {"class": "video-card-channel"}).a.text.strip()
        video_entry["duration"] = parsed_time_to_seconds(
            block.find("span", {"class": "video-duration"}).text.strip())

        video_entry["createdAt"] = dateparser.parse(block.find(
            "p", {"class": "video-card-published"}).text.strip()).timestamp() * 1000
        video_entry["videoUrl"] = "https://bitchute.com" + \
            block.find("a", href=True)["href"].strip()
        video_entry["platform"] = BITCHUTE
        video_entries.append(video_entry)

    data_dict["ready"] = True
    data_dict["content"] = video_entries

    return data_dict
