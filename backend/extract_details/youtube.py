from youtubesearchpython import VideosSearch
from pytube import YouTube

YOUTUBE = "yt"


async def youtube_search_videos(search_query):
    search_words = search_query["query"]
    max_results = search_query["max"]

    results_json = VideosSearch(search_words, limit=max_results)
    data_dict = {}
    data_dict["platform"] = YOUTUBE
    video_entries = []
    for video in results_json.result()["result"]:
        video_entry = {}
        video_entry["thumbSrc"] = video["thumbnails"][0]["url"].split("?sqp")[
            0]
        video_entry["title"] = video["title"]
        video_entry["channel"] = video["channel"]["name"]
        video_entry["channelUrl"] = video["channel"]["link"]
        video_entry["views"] = ""  # TODO: video["viewCount"]["text"]
        video_entry["createdAt"] = ""  # TODO: video["publishedTime"]
        video_entry["videoUrl"] = video["link"]
        video_entry["platform"] = YOUTUBE
        video_entries.append(video_entry)

    data_dict["content"] = video_entries
    data_dict["ready"] = True
    return data_dict


def youtube_video_details(video_url):
    yt = YouTube(video_url)
    stream_url = yt.streams.filter(progressive=True, file_extension='mp4').order_by(
        'resolution').desc().first().url
    video_details = {
        "id": yt.video_id,
        "title": yt.title,
        "description": yt.description,
        "author": yt.author,
        "duration": yt.length,
        "view_count": yt.views,
        "average_rating": yt.rating,
        "like_count": "",
        "dislike_count": "",
        "thumbnail": yt.thumbnail_url,
        "stream_url": stream_url,
        # "channel_url": f"{meta['channel_url']}",

    }
    return video_details
