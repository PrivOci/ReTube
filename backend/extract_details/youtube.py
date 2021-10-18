import dateparser
import pytube
import requests
from youtubesearchpython import VideosSearch, ChannelsSearch
from loguru import logger

from utils.util import parsed_time_to_seconds, convert_str_to_number, is_connected


class YoutubeProcessor:
    """Class to process YouTube videos and channels."""
    YOUTUBE = "yt"

    def __init__(self) -> None:
        self.session = requests.Session()

    def get_video_details(self, video_url) -> dict:
        return self._get_video_details_pytube(video_url)

    def _get_video_details_pytube(self, video_url) -> dict:
        """
        Extract video meta using pytube
        """

        # TODO: cache data until video url expires
        yt_object = pytube.YouTube(video_url)

        is_live = False
        try:
            yt_object.check_availability()
        except pytube.exceptions.LiveStreamError as e:
            is_live = True

        if is_live:
            # TODO: live stream url
            video_url = None
        else:
            video_url_obj = yt_object.streams.filter(
                progressive=True, file_extension='mp4').order_by("resolution").desc().first()
            video_url = video_url_obj.url

        video_details = {
            "id": yt_object.video_id,
            "title": yt_object.title,
            "streamUrl": video_url,
            "description": yt_object.description,
            "author": yt_object.author,
            "duration": yt_object.length,
            "views": yt_object.views,
            "thumbnailUrl": yt_object.thumbnail_url,
            "channelUrl": yt_object.channel_url,
            "createdAt": yt_object.publish_date.timestamp() * 1000,
        }
        return video_details

    def search_video(self, search_query):
        search_words = search_query["query"]
        max_results = search_query["max"]

        results_json = VideosSearch(search_words, limit=max_results)
        data_dict = {"platform": self.YOUTUBE}

        video_entries = []
        for video in results_json.result()["result"]:
            video_entry = {}
            video_entry["thumbnailUrl"] = video["thumbnails"][0]["url"].split("?sqp")[
                0]
            video_entry["title"] = video["title"]
            video_entry["author"] = video["channel"]["name"]
            video_entry["channelUrl"] = video["channel"]["link"]
            video_entry["views"] = ""  # TODO: video["viewCount"]["text"]
            # date
            video_time = video["publishedTime"]
            if video_time:
                # None if still streaming
                if "Streamed" in video_time:
                    video_time = video_time.split("Streamed ")[1]
                date_formatted = dateparser.parse(video_time)
                video_entry["createdAt"] = date_formatted.timestamp() * 1000
            # duration
            video_entry["duration"] = parsed_time_to_seconds(video["duration"])
            video_entry["videoUrl"] = video["link"]
            video_entry["platform"] = self.YOUTUBE
            video_entries.append(video_entry)

        data_dict["content"] = video_entries
        data_dict["ready"] = True
        return data_dict

    def search_for_channels(self, search_query):
        """Searches for channels in YouTube.

        Args:
            search_query (str): search query.
        """
        search_words = search_query["query"]
        max_results = search_query["max"]
        search_result = ChannelsSearch(
            search_words, limit=max_results).result()
        data_dict = {"platform": self.YOUTUBE}
        channel_entries = []
        for channel in search_result["result"]:
            channel_entry = {}
            if channel["subscribers"]:
                sub_count_str = channel["subscribers"].split(" ")[0]
                channel_entry["subscriberCount"] = convert_str_to_number(
                    sub_count_str)
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

    def channel_data(self, details) -> dict:
        """
        Extracts video list from a channel id and playlist id
        """
        # access mobile version: https://m.youtube.com/?persist_app=1&app=m
        is_it_playlist = details.get("playlist") == True
        if is_it_playlist:
            channel_url = f"https://m.youtube.com/playlist?list={details['id']}"
            taget_url = f"{channel_url}&pbj=1"
        else:
            channel_url = f"https://m.youtube.com/channel/{details['id']}".strip(
                "/")
            taget_url = f'{channel_url}/videos?pbj=1'
        data_dict = {}
        data_dict["platform"] = self.YOUTUBE
        headers = {
            'authority': 'm.youtube.com',
            'x-youtube-sts': '18892',
            'x-youtube-device': 'cbr=Edge+Chromium&cbrand=google&cbrver=93.0.961.52&ceng=WebKit&cengver=537.36&cmodel'
                                '=pixel+2+xl&cos=Android&cosver=8.0.0&cplatform=MOBILE&cyear=2017',
            'x-youtube-page-label': 'youtube.mobile.web.client_20210923_00_RC00',
            'sec-ch-ua-arch': '',
            'sec-ch-ua-platform-version': '"8.0.0"',
            'x-youtube-page-cl': '398415020',
            'x-spf-referer': channel_url,
            'x-youtube-utc-offset': '60',
            'sec-ch-ua-model': '"Pixel 2 XL"',
            'x-youtube-time-zone': 'Europe/London',
            'sec-ch-ua-platform': '"Android"',
            'sec-ch-ua-mobile': '?1',
            'user-agent': 'Mozilla/5.0 (Linux; Android 8.0.0; Pixel 2 XL Build/OPD1.170816.004) AppleWebKit/537.36 ('
                          'KHTML, like Gecko) Chrome/93.0.4577.82 Mobile Safari/537.36 Edg/93.0.961.52',
            'sec-ch-ua-full-version': '"93.0.961.52"',
            'x-youtube-client-name': '2',
            'x-youtube-client-version': '2.20210923.00.00',
            'sec-ch-ua': '"Microsoft Edge";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
            'accept': '*/*',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': channel_url,
            'accept-language': 'en-GB,en;q=0.9',
        }
        response = requests.get(taget_url, headers=headers)
        if not response.ok:
            data_dict["ready"] = False
            return data_dict
        resp_json = response.json()

        # header
        if not is_it_playlist:
            header = resp_json["response"]["header"]["c4TabbedHeaderRenderer"]
            subscriber_count = None
            if "subscriberCountText" in header:
                sub_count_str = header["subscriberCountText"]["runs"][0]["text"].split(" ")[
                    0]
                subscriber_count = convert_str_to_number(sub_count_str)

            data_dict["channel_meta"] = {
                "title": header["title"],
                "channelUrl": f"https://youtube.com/channel/{header['channelId']}",
                "banner": header["banner"]["thumbnails"][0]["url"] if "banner" in header else None,
                "avatar": header["avatar"]["thumbnails"][0]["url"],
                "subscriberCount": subscriber_count
            }

        # tab 1 - is for videos
        videos_index = 0 if is_it_playlist else 1
        videos = resp_json["response"]["contents"]["singleColumnBrowseResultsRenderer"]["tabs"][videos_index]
        content = videos["tabRenderer"]["content"]["sectionListRenderer"]["contents"]
        video_meta_list = content[0]["itemSectionRenderer"]["contents"]

        if not is_it_playlist:
            channel_name = resp_json["response"]["metadata"]["channelMetadataRenderer"]["title"]
            channel_url = resp_json["response"]["metadata"]["channelMetadataRenderer"]["channelUrl"]
        else:
            channel_name = None

        renderer_key = "playlistVideoRenderer" if is_it_playlist else "compactVideoRenderer"
        if is_it_playlist:
            video_meta_list = video_meta_list[0]["playlistVideoListRenderer"]["contents"]

        video_entries = []
        for entry in video_meta_list:
            video_entry = {}
            # the last item
            if "continuationItemRenderer" in entry:
                continue
            video_meta = entry[renderer_key]
            if is_it_playlist:
                channel_name = video_meta["shortBylineText"]["runs"][0]["text"]
                channel_id = video_meta["shortBylineText"]["runs"][0]["navigationEndpoint"]["browseEndpoint"][
                    "browseId"]
                channel_url = f"https://youtube.com/channel/{channel_id}"

            video_entry["title"] = video_meta["title"]["runs"][0]["text"]
            # there are 4 different sizes
            video_entry["thumbnailUrl"] = video_meta["thumbnail"]["thumbnails"][1]["url"]
            if not is_it_playlist:
                video_entry["channelThumbnail"] = video_meta["channelThumbnail"]["thumbnails"][0]["url"]
            if "publishedTimeText" in video_meta:
                date_str = video_meta["publishedTimeText"]["runs"][0]["text"].lower(
                )
                date_str = date_str.replace("streamed", "").strip()
                video_entry["createdAt"] = int(
                    dateparser.parse(date_str).timestamp()) * 1000
            if "viewCountText" in video_meta:
                # 2,403 views
                views_str = video_meta["viewCountText"]["runs"][0]["text"].split(" ")[
                    0]
                # No views
                if views_str == "No":
                    views_str = "0"
                video_entry["views"] = int(views_str.replace(',', ''))
            video_entry["videoUrl"] = f"https://www.youtube.com/watch?v={video_meta['videoId']}"
            # 16:33
            if "lengthText" in video_meta:
                duration_str = video_meta["lengthText"]["runs"][0]["text"]
                video_entry["duration"] = parsed_time_to_seconds(duration_str)
            else:
                video_entry["duration"] = None

            video_entry["channelUrl"] = channel_url
            video_entry["author"] = channel_name

            video_entry["platform"] = self.YOUTUBE
            video_entries.append(video_entry)
        data_dict["content"] = video_entries
        data_dict["ready"] = True
        return data_dict
