from typing import Dict
from youtubesearchpython import VideosSearch, ChannelsSearch
import youtube_dl as yt
from youtube_dl.utils import DownloadError
from utils.util import get_xml_stream_as_json
import time
from datetime import datetime


class YoutubeProcessor:
    """Class to process YouTube videos and channels."""
    YOUTUBE = "yt"
    YOUTUBE_XML = "https://www.youtube.com/feeds/videos.xml"
    ydl_opts = {
        'format': 'best',
    }

    def __init__(self) -> None:
        self.ydl = yt.YoutubeDL(self.ydl_opts)

    def get_video_details(self, video_url) -> dict:
        try:
            meta = self.ydl.extract_info(
                video_url, download=False)
        except DownloadError as err:
            print(err)
            return None
        if meta["is_live"]:
            return None


        video_details = {
            "id": f"{meta['id']}",
            "description": f"{meta['description']}",
            "author": f"{meta['uploader']}",
            "duration": f"{meta['duration']}",
            "views": int(meta['view_count']),
            "likeCount": f"{meta['like_count']}" if "like_count" in meta else "",
            "dislikeCount": f"{meta['dislike_count']}" if "dislike_count" in meta else "",
            "title": f"{meta['title']}",
            "thumbnailUrl": f"{meta['thumbnail']}",
            "streamUrl": f"{meta['url']}",
            "createdAt": int(datetime.strptime(meta["upload_date"], '%Y%m%d').timestamp()) * 1000,
            "channelUrl": f"{meta['channel_url']}",
        }
        # post-processing
        return video_details

    def search_video(self, search_query):
        search_words = search_query["query"]
        max_results = search_query["max"]

        results_json = VideosSearch(search_words, limit=max_results)
        data_dict = {}
        data_dict["platform"] = self.YOUTUBE
        video_entries = []
        for video in results_json.result()["result"]:
            video_entry = {}
            video_entry["thumbnailUrl"] = video["thumbnails"][0]["url"].split("?sqp")[
                0]
            video_entry["title"] = video["title"]
            video_entry["author"] = video["channel"]["name"]
            video_entry["channelUrl"] = video["channel"]["link"]
            video_entry["views"] = ""  # TODO: video["viewCount"]["text"]
            video_entry["createdAt"] = ""  # TODO: video["publishedTime"]
            video_entry["videoUrl"] = video["link"]
            video_entry["platform"] = self.YOUTUBE
            video_entries.append(video_entry)

        data_dict["content"] = video_entries
        data_dict["ready"] = True
        return data_dict

    def search_for_channels(self, search_query):
        '''Searches for channels in YouTube.

        Args:
            search_terms (str): search query.
        '''
        search_words = search_query["query"]
        max_results = search_query["max"]
        search_result = ChannelsSearch(
            search_words, limit=max_results).result()
        data_dict = {}
        data_dict["platform"] = self.YOUTUBE
        channel_entries = []
        for channel in search_result["result"]:
            channel_entry = {}
            channel_entry["isChannel"] = True
            channel_entry["id"] = channel["id"]
            thumb = channel["thumbnails"][-1]["url"]
            if thumb.startswith("//"):
                thumb = f"https:{thumb}"
            channel_entry["thumbnailUrl"] = thumb
            channel_entry["title"] = channel["title"]
            channel_entry["author"] = channel["title"]
            channel_entry["channelUrl"] = channel["link"]
            channel_entry["videoCount"] = channel["videoCount"]
            channel_entry["platform"] = self.YOUTUBE
            channel_entries.append(channel_entry)

        data_dict["content"] = channel_entries
        data_dict["ready"] = True
        return data_dict

    def channel_data(self, details: dict) -> dict:
        data_dict = {}
        data_dict["platform"] = self.YOUTUBE
        yt_type = "?playlist_id=" if details.get(
            "playlist") == True else "?channel_id="
        popular_rss_url = f"{self.YOUTUBE_XML}{yt_type}{details['id']}"
        content = get_xml_stream_as_json(popular_rss_url)
        if not content:
            data_dict["ready"] = False
            return data_dict
        video_entries = []
        content_list = []
        if not isinstance(content["feed"]["entry"], list):
            content_list.append(content["feed"]["entry"])
        else:
            content_list = content["feed"]["entry"]
        for entry in content_list:
            video_entry = {}
            video_entry["thumbnailUrl"] = entry["media:group"]["media:thumbnail"]["@url"]
            video_entry["title"] = entry["title"]
            video_entry["author"] = entry["author"]["name"]
            video_entry["views"] = entry["media:group"]["media:community"]["media:statistics"]["@views"]
            video_entry["createdAt"] = int(time.mktime(
                datetime.fromisoformat(entry["published"]).timetuple())) * 1000

            video_entry["videoUrl"] = entry["link"]["@href"]
            video_entry["channelUrl"] = f"https://www.youtube.com/channel/{entry['yt:channelId']}"
            video_entry["platform"] = self.YOUTUBE
            video_entries.append(video_entry)
        data_dict["content"] = video_entries
        data_dict["ready"] = True
        return data_dict
