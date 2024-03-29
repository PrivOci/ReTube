import urllib.parse

import requests
from bs4 import BeautifulSoup
from loguru import logger

from utils.util import parsed_time_to_seconds, convert_str_to_number
import dateutil.parser as dp

# TODO: search for channels


class RumbleProcessor:
    """Class to process Rumble videos and channels."""
    PLATFORM = "rb"
    RUMBLE_BASE = "https://rumble.com"

    def __init__(self) -> None:
        self.session = requests.Session()

    def _get_video_entries(self, target_url, parse_channel_meta=False) -> list:
        res = self.session.get(target_url)
        if not res.ok:
            logger.debug(
                f"Failed to download rumble channel meta\nReason: {res.reason}")
            return []
        soup = BeautifulSoup(res.text, 'html.parser')
        constrained_section = soup.find("div", "constrained")
        list_html = constrained_section.find("ol")
        video_list_html = list_html.find_all("li", "video-listing-entry")

        # channel meta
        channel_meta = None
        if parse_channel_meta and not "rumble.com/videos" in target_url:
            title = constrained_section.find(
                "h1", {"class": "listing-header--title"}).text
            banner_src = constrained_section.find(
                "img", {"class": "listing-header--backsplash-img"})
            banner = banner_src["src"] if banner_src else None
            avatar_src = constrained_section.find(
                "img", {"class": "listing-header--thumb"})
            avatar = avatar_src["src"] if avatar_src else None
            # subscriber count
            subscriber_count = None
            subs_count_span = soup.find(
                "span", "subscribe-button-count")
            if subs_count_span:
                subs_count_str = subs_count_span.text.strip()
                subscriber_count = convert_str_to_number(subs_count_str)
            channel_meta = {
                "title": title,
                "channelUrl": target_url,
                "banner": banner,
                "avatar": avatar,
                "subscriberCount": subscriber_count
            }

        video_entries = []
        for block in video_list_html:
            video_entry = {}
            article = block.article

            # channel
            channel_id = article.find("a", {"rel": "author"})["href"]

            # duration
            duration_span = article.find(
                "span", {"class": "video-item--duration"})
            duration_span_value = duration_span["data-value"].strip(
            ) if duration_span else None

            is_live = False
            live_span = article.find("span", {"class": "video-item--live"})
            if live_span:
                is_live = True
            
            # views
            views_count = None
            if "video-item--meta video-item--views" in article.text:
                views_span = article.find(
                    "span", {"class": "video-item--meta video-item--views"})["data-value"].strip()
                views_count = int(views_span.replace(",", ""))

            # date
            date_span = article.find(
                "time", {"class": "video-item--meta video-item--time"})["datetime"].strip()
            parsed_time = dp.parse(date_span)
            time_in_seconds = int(parsed_time.timestamp()) * 1000

            # TODO(me): use utc bytes of str
            video_entry["title"] = article.h3.text.strip()
            video_entry["thumbnailUrl"] = article.a.img["src"]
            video_entry["videoUrl"] = f"{self.RUMBLE_BASE}{article.a['href']}"
            video_entry["author"] = article.footer.a.text.strip()
            video_entry["duration"] = parsed_time_to_seconds(
                duration_span_value) if duration_span_value else None
            video_entry["views"] = views_count
            video_entry["platform"] = self.PLATFORM
            video_entry["createdAt"] = time_in_seconds
            video_entry["channelUrl"] = f"{self.RUMBLE_BASE}{channel_id}"
            video_entry["isLive"] = is_live
            video_entries.append(video_entry)
        return video_entries, channel_meta

    def channel_data(self, details: dict) -> dict:
        data_dict = {
            "ready": False,
            "platform": self.PLATFORM
        }
        if details['id'] == "popular":
            channel_url = "https://rumble.com/videos?sort=views&date=today"
        else:
            channel_url = f"{self.RUMBLE_BASE}/{details['id']}"
        if not details["id"]:
            return {}
        data_dict["ready"] = True
        data_dict["content"], data_dict["channel_meta"] = self._get_video_entries(
            channel_url, parse_channel_meta=True)
        return data_dict

    def search_for_videos(self, search_query) -> dict:
        search_terms = search_query["query"]
        # max_results = search_query["max"]
        encoded_query = urllib.parse.quote(search_terms)

        data_dict = {
            "ready": False,
            "platform": self.PLATFORM
        }

        videos_url = f"{self.RUMBLE_BASE}/search/video?q={encoded_query}"
        data_dict["ready"] = True
        data_dict["content"], _ = self._get_video_entries(videos_url)
        return data_dict

    def get_video_details(self, video_url) -> dict:
        html_page = self.session.get(video_url).text
        video_id = html_page.split('"video":"')[1].split('","')[0]

        soup = BeautifulSoup(html_page, 'html.parser')
        # views
        heading_info_list = soup.find_all("span", "media-heading-info")
        views_count = None
        for info in heading_info_list:
            info_text = info.text.strip()
            if "Views" in info_text:
                views_count = info_text.split(" ")[0].replace(",", "")

        # description
        media_description_text = soup.find(
            "div", "container content media-description").text.strip()
        
        # "Rumble — " if no description
        if media_description_text == "Rumble\n —":
            video_description = None
        else:
            video_description = media_description_text.split(" — ")[1]
        
    
        # like count (rumbles count)
        count = int(soup.find("span", "rumbles-count").text.strip())

        # subscriber count
        subs_count = None
        subs_count_span = soup.find(
            "span", "subscribe-button-count")
        if subs_count_span:
            subs_count_str = subs_count_span.text.strip()
            subs_count = convert_str_to_number(subs_count_str)

        # get direct video source
        # https://rumble.com/embedJS/u3/?request=video&ver=2&v=video_id
        target_url = f"https://rumble.com/embedJS/u3/?request=video&ver=2&v={video_id}"
        res = self.session.get(target_url)
        if not res.ok:
            logger.debug(
                f"Failed to get rumble video source\nReason: {res.reason}")
            return {}
        meta_json = res.json()

        is_live = False
        if meta_json["live"] != 0:
            is_live = True

        parsed_time = dp.parse(meta_json["pubDate"])
        time_in_seconds = int(parsed_time.timestamp()) * 1000

        if is_live:
            video_format = "hls"
        else:
            video_format = "mp4"

        video_details = {
            "id": video_url.split(self.RUMBLE_BASE + "/")[1].strip().strip('.html'),
            "isLive": is_live,
            "title": meta_json["title"],
            "description": video_description,
            "author": meta_json["author"]["name"],
            "channelUrl": meta_json["author"]["url"],
            "duration": int(meta_json["duration"]),
            "views": views_count,
            "likeCount": count,
            # "dislikeCount": ,
            "subscriberCount": subs_count if subs_count else None,
            "thumbnailUrl": meta_json["i"],
            "createdAt": time_in_seconds,
            "streamUrl": meta_json["u"][video_format]["url"],
        }
        return video_details
