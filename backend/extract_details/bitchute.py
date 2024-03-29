import re
import urllib.parse
from datetime import datetime

import cloudscraper
import dateparser
from bs4 import BeautifulSoup
from loguru import logger

from utils.util import get_xml_stream_as_json, parsed_time_to_seconds


class BitchuteProcessor:
    """Class to process Bitchute videos and channels."""
    BITCHUTE = "bc"
    BITCHUTE_BASE = "https://www.bitchute.com"
    BITCHUTE_XML = f"{BITCHUTE_BASE}/feeds/rss/channel/"

    _headers = {
        'authority': 'www.bitchute.com',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90"',
        'accept': '*/*',
        'dnt': '1',
        'x-requested-with': 'XMLHttpRequest',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) Ubuntu/14.04.6 '
                      'Chrome/81.0.3990.0 Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.bitchute.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'accept-language': 'en-US,en-GB;q=0.9,en;q=0.8',
    }

    def __init__(self) -> None:
        # self.session = requests.Session()
        self.session = cloudscraper.create_scraper()  # returns a CloudScraper instance
        self.cookies = {}
        # get csrftoken
        res = self.session.get(
            f'{self.BITCHUTE_BASE}/help-us-grow/', headers=self._headers)
        if res.ok:
            self.cookies = self.session.cookies.get_dict()
        if not self.cookies or not 'csrftoken' in self.cookies:
            self.cookies["csrftoken"] = "lTJ0imXW23ycznfCjFy8rwqJxbtYZMJPgCbm2WHYF3l1454XjvkXTjvUvTsdtPCt"
        self._headers["cookie"] = f'csrftoken={self.cookies["csrftoken"]}'

    def get_video_details(self, video_url) -> dict:
        req = self.session.get(video_url)
        if not req.ok:
            return {}
        soup = BeautifulSoup(req.text, 'html.parser')

        data = {
            'csrfmiddlewaretoken': self.cookies["csrftoken"]
        }

        self._headers['referer'] = video_url
        count_req = self.session.post(
            f'{video_url.strip("/")}/counts/', data=data, headers=self._headers)
        if count_req.ok:
            count_json = count_req.json()
        else:
            count_json = None

        publish_date = soup.find(
            "div", {"class": "video-publish-date"}).text.strip()
        splited_date = publish_date.split(" on ")[1].split()
        date_result = f"{splited_date[0]} {re.sub('[^0-9]', '', splited_date[1])} {splited_date[2]}"
        publish_date = datetime.strptime(date_result, '%B %d %Y.').timestamp()

        video_details = {
            "id": video_url.split("/video/")[1].strip().strip('/'),
            "title": soup.find("h1", {"id": "video-title"}).text,
            "description": soup.find(id="video-description").text,
            "author": soup.find("p", {"class": "owner"}).a.text,
            "channelUrl": "https://bitchute.com" +
                          soup.find("p", {"class": "name"}).a["href"],
            "duration": "",
            "views": count_json["view_count"] if count_json else None,
            "likeCount": count_json["like_count"] if count_json else None,
            "dislikeCount": count_json["dislike_count"] if count_json else None,
            "subscriberCount": count_json["subscriber_count"] if count_json else None,
            "thumbnailUrl": soup.find("video", {"id": "player"})["poster"],
            "createdAt": int(publish_date) * 1000,
            "streamUrl": soup.find("video", {"id": "player"}).source["src"],
        }
        return video_details

    def _parse_bitchute_details(self, entry) -> dict:
        video_entry = {
            "thumbnailUrl": entry["images"]["thumbnail"],
            "title": entry["name"],
            "author": entry["channel_name"],
            "views": entry["views"]
        }
        date_formatted = dateparser.parse(entry["published"])
        video_entry["createdAt"] = date_formatted.timestamp() * 1000
        video_entry["videoUrl"] = f"https://bitchute.com{entry['path']}"
        video_entry["duration"] = entry["duration"]

        video_entry["platform"] = self.BITCHUTE
        return video_entry

    def search_video(self, search_query) -> dict:
        search_terms = search_query["query"]
        max_results = search_query["max"]
        encoded_query = urllib.parse.quote(search_terms)

        data_dict = {
            "platform": self.BITCHUTE,
            "ready": False
        }

        data = {
            'csrfmiddlewaretoken': self.cookies['csrftoken'],
            'query': encoded_query,
            'kind': 'video',
            'duration': '',
            'sort': '',
            'page': '0'
        }

        response = self.session.post(
            'https://www.bitchute.com/api/search/list/', headers=self._headers, data=data)
        if not response.ok:
            return data_dict
        response_json = response.json()
        if "success" not in response_json or response_json["success"] != True:
            return data_dict

        video_entries = []
        for entry in response_json["results"][:max_results]:
            video_entry = self._parse_bitchute_details(entry)
            if video_entry:
                video_entries.append(video_entry)

        data_dict["content"] = video_entries
        data_dict["ready"] = True

        return data_dict

    def channel_data(self, details: dict) -> dict:
        if details['id'] == "popular":
            return self.get_popular()
        data_dict = {
            "ready": False,
            "platform": self.BITCHUTE
        }
        channel_rss = f"{self.BITCHUTE_XML}{details['id']}"
        content = get_xml_stream_as_json(channel_rss, session=self.session)
        if not content:
            return data_dict

        channel_json = content["rss"]["channel"]
        data_dict["channel_meta"] = {
            "title": channel_json["title"],
            "channelUrl": channel_json["link"],
            "banner": None,
            "avatar": None,
            "subscriberCount": None,
        }

        video_entries = []
        for entry in channel_json["item"]:
            video_entry = {
                "thumbnailUrl": entry["enclosure"]["@url"],
                "title": entry["title"],
                "author": details['id'],
                "views": "",
                "createdAt": int(
                    dateparser.parse(entry["pubDate"]).timestamp()) * 1000,
                "videoUrl": f"https://www.bitchute.com/video/{entry['link'].split('/embed/')[1]}",
                "platform": self.BITCHUTE,
                "channelUrl": f"https://www.bitchute.com/channel/{details['id']}"
            }
            video_entries.append(video_entry)

        data_dict["ready"] = True
        data_dict["content"] = video_entries if len(video_entries) else None
        return data_dict

    # Parse Bitchute "listing-popular" section

    def get_popular(self) -> dict:
        data_dict = {
            "ready": False,
            "platform": self.BITCHUTE
        }
        res = self.session.get(self.BITCHUTE_BASE, headers=self._headers)
        if not res.ok:
            logger.debug(
                f"Failed to download bitchute popular\nReason: {res.reason}")
            return data_dict
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
            channel_id = block.find(
                "p", {"class": "video-card-channel"}).a["href"]
            video_entry["channelUrl"] = f"{self.BITCHUTE_BASE}{channel_id}"
            video_entry["createdAt"] = dateparser.parse(block.find(
                "p", {"class": "video-card-published"}).text.strip()).timestamp() * 1000
            video_entry["videoUrl"] = f'{self.BITCHUTE_BASE}{block.find("a", href=True)["href"].strip()}'
            video_entry["platform"] = self.BITCHUTE
            video_entries.append(video_entry)

        data_dict["ready"] = True
        data_dict["content"] = video_entries

        return data_dict
