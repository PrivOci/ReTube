from youtubesearchpython import VideosSearch, ChannelsSearch
from pytube import YouTube
from utils.util import get_xml_stream_as_json
import time
from datetime import datetime

YOUTUBE = "yt"
YOUTUBE_XML = "https://www.youtube.com/feeds/videos.xml"

def youtube_search_videos(search_query):
    search_words = search_query["query"]
    max_results = search_query["max"]

    results_json = VideosSearch(search_words, limit=max_results)
    data_dict = {}
    data_dict["platform"] = YOUTUBE
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
        video_entry["platform"] = YOUTUBE
        video_entries.append(video_entry)

    data_dict["content"] = video_entries
    data_dict["ready"] = True
    return data_dict


# def youtube_video_details(video_url):
#     yt = YouTube(video_url)
#     streamUrl = yt.streams.filter(progressive=True, file_extension='mp4').order_by(
#         'resolution').desc().first().url
#     video_details = {
#         "id": yt.video_id,
#         "title": yt.title,
#         "description": yt.description,
#         "author": yt.author,
#         "duration": yt.length,
#         "views": yt.views,
#         "averageRating": yt.rating,
#         "likeCount": "",
#         "dislikeCount": "",
#         "thumbnailUrl": yt.thumbnail_url,
#         "streamUrl": streamUrl,
#         # "channelUrl": f"{meta['channel_url']}",

#     }
#     return video_details


def youtube_channel_search(search_query):
    '''Searches for channels in YouTube.

    Args:
        search_terms (str): search query.
    '''
    search_words = search_query["query"]
    max_results = search_query["max"]
    search_result = ChannelsSearch(search_words, limit=max_results).result()
    data_dict = {}
    data_dict["platform"] = YOUTUBE
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
        channel_entry["platform"] = YOUTUBE
        channel_entries.append(channel_entry)

    data_dict["content"] = channel_entries
    data_dict["ready"] = True
    return data_dict


# Get channel/playlist videos
def get_youtube_videos_source(details: dict) -> dict:
    data_dict = {}
    data_dict["platform"] = YOUTUBE
    yt_type = "?playlist_id=" if details.get(
        "playlist") == True else "?channel_id="
    popular_rss_url = f"{YOUTUBE_XML}{yt_type}{details['id']}"
    content = get_xml_stream_as_json(popular_rss_url)
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
        video_entry["platform"] = YOUTUBE
        video_entries.append(video_entry)
    data_dict["content"] = video_entries
    data_dict["ready"] = True
    return data_dict
