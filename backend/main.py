from extract_details.bitchute import bitchute_video_details, bitchute_search_video
from extract_details.lbry import lbry_popular, lbry_video_details, lbry_search_videos, lbry_channel_details
from extract_details.youtube import youtube_search_videos, youtube_video_details

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import uvicorn

from pydantic import BaseModel

import requests
import xmltodict

from bs4 import BeautifulSoup

import optimize

import email.utils
from datetime import datetime
import dateparser
import time

app = FastAPI()


# optimize.DISABLE_CACHE = True

# testing
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://127.0.0.1",
    "*",
]

YOUTUBE_XML = "https://www.youtube.com/feeds/videos.xml"
BITCHUTE_XML = "https://www.bitchute.com/feeds/rss/channel/"

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


YOUTUBE = "yt"
LBRY = "lb"
BITCHUTE = "bc"


class request_details(BaseModel):
    platform: str
    id: str


class search_query(BaseModel):
    query: str
    max: int


LB_VIDEO_URL = "https://lbry.tv/"
YT_VIDEO_URL = "https://www.youtube.com/watch?v="
BT_VIDEO_URL = "https://www.bitchute.com/video/"


@app.post("/api/video/")
async def get_video(details: request_details) -> dict:
    details.id = details.id.strip().strip("/")
    return await optimize.optimized_request(dict(details), get_video_from_source, 5 if details.id == YOUTUBE else 72)


async def get_video_from_source(details: dict) -> dict:
    result = {}
    result['ready'] = False

    # prepare video_url
    video_url = None
    if details["platform"] == LBRY:
        video_url = LB_VIDEO_URL + details["id"]
    elif details["platform"] == YOUTUBE:
        video_url = YT_VIDEO_URL + details["id"]
    elif details["platform"] == BITCHUTE:
        video_url = BT_VIDEO_URL + details["id"]
    else:
        return result

    # our extractors
    if details["platform"] == YOUTUBE:
        result["content"] = youtube_video_details(video_url)
        result['ready'] = True
        result["platform"] = YOUTUBE
        return result
    elif details["platform"] == BITCHUTE:
        result["content"] = bitchute_video_details(video_url)
        result['ready'] = True
        result["platform"] = BITCHUTE
        return result
    elif details["platform"] == LBRY:
        result["content"] = lbry_video_details(video_url)
        result['ready'] = True
        result["platform"] = LBRY
        return result
    else:
        return result


# YouTube channel to JSON
@app.post("/api/youtube/c/")
async def get_youtube_channel(details: request_details) -> dict:
    details = dict(details)
    details["id"] = details["id"].strip().strip("/")
    details["channel"] = True
    return await optimize.optimized_request(
        dict(details),
        get_youtube_videos_source,
        1)


async def get_youtube_videos_source(details: dict) -> dict:
    data_dict = {}
    data_dict["platform"] = YOUTUBE
    yt_type = "?playlist_id=" if details.get(
        "playlist") == True else "?channel_id="
    popular_rss_url = f"{YOUTUBE_XML}{yt_type}{details['id']}"
    content = await get_xml_stream_as_json(popular_rss_url)
    video_entries = []
    content_list = []
    if not isinstance(content["feed"]["entry"], list):
        content_list.append(content["feed"]["entry"])
    else:
        content_list = content["feed"]["entry"]
    for entry in content_list:
        video_entry = {}
        video_entry["thumbSrc"] = entry["media:group"]["media:thumbnail"]["@url"]
        video_entry["title"] = entry["title"]
        video_entry["channel"] = entry["author"]["name"]
        video_entry["views"] = entry["media:group"]["media:community"]["media:statistics"]["@views"]
        video_entry["createdAt"] = int(time.mktime(
            datetime.fromisoformat(entry["published"]).timetuple())) * 1000

        video_entry["videoUrl"] = entry["link"]["@href"]
        video_entry["platform"] = YOUTUBE
        video_entries.append(video_entry)
    data_dict["content"] = video_entries
    data_dict["ready"] = True
    return data_dict


# YouTube playlist to JSON
@app.post("/api/youtube/p/")
async def get_youtube_playlist(details: request_details) -> dict:
    details = dict(details)
    details["id"] = details["id"].strip().strip("/")
    if details["id"] == "popular":
        details["id"] = "PLrEnWoR732-BHrPp_Pm8_VleD68f9s14-"
    details["playlist"] = True
    return await optimize.optimized_request(
        dict(details),
        get_youtube_videos_source,
        1)


# search youtube videos
@app.post("/api/youtube/search/")
async def youtube_search_results(search_query: search_query) -> dict:
    search_query = dict(search_query)
    search_query["platform"] = YOUTUBE
    result = await optimize.optimized_request(
        dict(search_query),
        youtube_search_videos,
        1)
    return result


# search bitchute videos
@app.post("/api/bitchute/search/")
async def bitchute_search_results(search_query: search_query) -> dict:
    search_query = dict(search_query)
    search_query["platform"] = BITCHUTE
    result = await optimize.optimized_request(
        dict(search_query),
        bitchute_search_video,
        1)
    return result


# search youtube videos
@app.post("/api/lbry/search/")
async def lbry_search_results(search_query: search_query) -> dict:
    search_query = dict(search_query)
    search_query["platform"] = LBRY
    result = await optimize.optimized_request(
        dict(search_query),
        lbry_search_videos,
        1)
    return result


# Lbry/Odysee channel to JSON
@app.post("/api/lbry/c/")
async def get_lbry_channel(details: request_details) -> dict:
    details = dict(details)
    details["id"] = details["id"].strip().strip("/")
    details["channel"] = True
    return await optimize.optimized_request(
        dict(details),
        get_lbry_channel_source,
        1)


async def get_lbry_channel_source(details: dict) -> dict:
    if details['id'] == "popular":
        return await lbry_popular()
    return lbry_channel_details(details['id'])


# BitChute channel to JSON
@app.post("/api/bitchute/c/")
async def get_bitchute_channel(details: request_details):
    details = dict(details)
    details["id"] = details["id"].strip().strip("/")
    details["channel"] = True
    return await optimize.optimized_request(
        dict(details),
        get_bitchute_channel_source,
        1)


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
        video_entry["thumbSrc"] = entry["enclosure"]["@url"]
        video_entry["title"] = entry["title"]
        video_entry["channel"] = details['id']
        video_entry["views"] = ""
        video_entry["createdAt"] = int(time.mktime(
            email.utils.parsedate(entry["pubDate"]))) * 1000
        video_entry[
            "videoUrl"] = f"https://www.bitchute.com/video/{entry['link'].split('/embed/')[1]}"
        video_entry["platform"] = BITCHUTE
        video_entries.append(video_entry)

    data_dict["ready"] = True
    data_dict["content"] = video_entries
    return data_dict


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

        video_entry["thumbSrc"] = block.find("img", src=True)[
            "data-src"].strip()

        video_entry["title"] = block.find(
            "p", {"class": "video-card-title"}).a.text.strip()
        video_entry["channel"] = block.find(
            "p", {"class": "video-card-channel"}).a.text.strip()
        video_entry["createdAt"] = dateparser.parse(block.find(
            "p", {"class": "video-card-published"}).text.strip()).timetuple()
        video_entry["videoUrl"] = "https://bitchute.com" + \
            block.find("a", href=True)["href"].strip()
        video_entry["platform"] = BITCHUTE
        video_entries.append(video_entry)

    data_dict["ready"] = True
    data_dict["content"] = video_entries

    return data_dict


async def get_xml_stream_as_json(xml_url):
    req = requests.get(xml_url)
    return xmltodict.parse(req.text)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
