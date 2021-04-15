import requests
from bs4 import BeautifulSoup
import urllib.parse

BITCHUTE = "bc"




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

    video_details = {
        "id": video_url.split("/video/")[1].strip().strip('/'),
        "title": soup.find("div", {"class": "title"}).text,
        "description": soup.find("meta", {"name": "description"})["content"],
        "author": soup.find("p", {"class": "video-card-channel"}).a.text,
        "channel_url": "https://bitchute.com" +
        soup.find("p", {"class": "video-card-channel"}).a["href"],
        "duration": "",
        "view_count": count_json["view_count"],
        "average_rating": "",
        "like_count": count_json["like_count"],
        "dislike_count": count_json["dislike_count"],
        "subscriber_count": count_json["subscriber_count"],
        "thumbnail": soup.find("video", {"id": "player"})["poster"],
        "stream_url": soup.find("video", {"id": "player"}).source["src"],
    }
    return video_details


def _parse_bitchute_details(entry) -> dict:
    video_entry = {}
    video_entry["thumbSrc"] = entry["images"]["thumbnail"]
    video_entry["title"] = entry["name"]
    video_entry["channel"] = entry["channel_name"]
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
