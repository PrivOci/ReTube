import youtube_dl as yt
from extract_details.bitchute import BitchuteProcessor
from extract_details.lbry import lbry_popular, lbry_video_details, lbry_search_videos, lbry_channel_details, lbry_channel_search
from extract_details.youtube import youtube_search_videos, youtube_channel_search, get_youtube_videos_source
from extract_details.facebook import get_facebook_page_source, facebook_video_details
from utils.spelling import ginger_check_sentence
import utils.optimize as optimize

from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from datetime import datetime

from loguru import logger

app = FastAPI()
bc_processor = BitchuteProcessor()

# optimize.DISABLE_CACHE = True

# testing
origins = [
    "http://localhost:3000",
    "http://localhost:3033",
    "http://localhost:8080",
]

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
FACEBOOK = "fb"


class request_details(BaseModel):
    platform: str
    id: str


class search_query(BaseModel):
    query: str
    max: int


class just_string(BaseModel):
    query: str


LB_VIDEO_URL = "https://odysee.com/"
YT_VIDEO_URL = "https://www.youtube.com/watch?v="
BT_VIDEO_URL = "https://www.bitchute.com/video/"
FB_VIDEO_URL = "https://www.facebook.com/"

# global list of channel URLs to prefetch them each hour.
# Only prefetched recently requested URLs
global_yt_urls = {}
global_lbry_urls = {}
global_bc_urls = {}
global_fb_urls = {}


async def prefetch_channels(platform, channels, source_function) -> None:
    """
    Prefetch channels requested within a day, remove rest.
    """
    details = {}
    details["platform"] = platform
    now = datetime.utcnow()
    for (id, req_date) in channels.items():
        details["id"] = id
        difference = now - req_date
        if difference.days != 0:
            del channels[id]
            continue
        logger.debug(f"prefetch: {details['id']} - {details['platform']}")
        await optimize.optimized_request(dict(details), source_function, 1, forced=True)


@app.on_event("startup")
@repeat_every(seconds=60 * 50)  # 50 mins
async def prefetch_yt_channels() -> None:
    await prefetch_channels(YOUTUBE, global_yt_urls, get_youtube_videos_source)


@app.on_event("startup")
@repeat_every(seconds=60 * 50)  # 50 mins
async def prefetch_lbry_channels() -> None:
    await prefetch_channels(LBRY, global_lbry_urls, get_lbry_channel_source)


@app.on_event("startup")
@repeat_every(seconds=60 * 50)  # 50 mins
async def prefetch_bc_channels() -> None:
    await prefetch_channels(BITCHUTE, global_bc_urls, bc_processor.channel_data)


@app.on_event("startup")
@repeat_every(seconds=60 * 50)  # 50 mins
async def prefetch_fb_channels() -> None:
    await prefetch_channels(FACEBOOK, global_fb_urls, get_facebook_page_source)


@app.post("/api/check")
async def check_sentence(just_string: just_string):
    return ginger_check_sentence(just_string.query)


@app.post("/api/video/")
async def get_video(details: request_details) -> dict:
    details.id = details.id.strip().strip("/")
    # YT video link expires
    if (details.id == YOUTUBE):
        return get_video_from_source(details)
    return await optimize.optimized_request(dict(details), get_video_from_source, 72)


def get_video_from_source(details: dict) -> dict:
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
    elif details["platform"] == FACEBOOK:
        video_url = FB_VIDEO_URL + details["id"]
    else:
        return result

    # our extractors
    if details["platform"] == YOUTUBE:
        # TODO: fix
        # result["content"] = youtube_video_details(video_url)
        ydl_opts = {
            'format': 'best'
        }
        with yt.YoutubeDL(ydl_opts) as ydl:
            meta = ydl.extract_info(
                video_url, download=False)

            result["content"] = {
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
                "channelUrl": f"{meta['channel_url']}",
            }
        result['ready'] = True
        result["platform"] = YOUTUBE
        return result
    elif details["platform"] == BITCHUTE:
        result["content"] = bc_processor.get_video_details(video_url)
        result['ready'] = True
        result["platform"] = BITCHUTE
        return result
    elif details["platform"] == LBRY:
        result["content"] = lbry_video_details(video_url)
        result['ready'] = False if result["content"] == None else True
        result["platform"] = LBRY
        return result
    elif details["platform"] == FACEBOOK:
        result["content"] = facebook_video_details(video_url)
        result['ready'] = False if result["content"] == None else True
        result["platform"] = FACEBOOK
        return result
    else:
        return result


# YouTube channel to JSON
@app.post("/api/youtube/c/")
async def get_youtube_channel(details: request_details) -> dict:
    details = dict(details)
    details["id"] = details["id"].strip().strip("/")
    details["channel"] = True
    global_yt_urls[details["id"]] = datetime.utcnow()
    return await optimize.optimized_request(
        dict(details),
        get_youtube_videos_source,
        1)


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


# search youtube channels
@app.post("/api/youtube/channels/")
async def youtube_search_channels(search_query: search_query) -> dict:
    search_query = dict(search_query)
    search_query["platform"] = YOUTUBE
    search_query["max"] = 3
    result = await optimize.optimized_request(
        dict(search_query),
        youtube_channel_search,
        1)
    return result


# search Lbry channels
@app.post("/api/lbry/channels/")
async def lbry_search_channels(search_query: search_query) -> dict:
    search_query = dict(search_query)
    search_query["platform"] = LBRY
    search_query["max"] = 3
    result = await optimize.optimized_request(
        dict(search_query),
        lbry_channel_search,
        1)
    return result


# search bitchute videos
@app.post("/api/bitchute/search/")
async def bitchute_search_results(search_query: search_query) -> dict:
    search_query = dict(search_query)
    search_query["platform"] = BITCHUTE
    result = await optimize.optimized_request(
        dict(search_query),
        bc_processor.search_video,
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
    global_lbry_urls[details["id"]] = datetime.utcnow()
    return await optimize.optimized_request(
        dict(details),
        get_lbry_channel_source,
        1)


def get_lbry_channel_source(details: dict) -> dict:
    if details['id'] == "popular":
        return lbry_popular()
    return lbry_channel_details(details['id'])


# BitChute channel to JSON
@app.post("/api/bitchute/c/")
async def get_bitchute_channel(details: request_details):
    details = dict(details)
    details["id"] = details["id"].strip().strip("/")
    details["channel"] = True
    global_bc_urls[details["id"]] = datetime.utcnow()
    return await optimize.optimized_request(
        dict(details),
        bc_processor.channel_data,
        1)


# Facebook page(channel) to JSON
@app.post("/api/facebook/c/")
async def get_facebook_channel(details: request_details):
    details = dict(details)
    details["id"] = details["id"].strip().strip("/")
    details["channel"] = True
    global_fb_urls[details["id"]] = datetime.utcnow()
    return await optimize.optimized_request(
        dict(details),
        get_facebook_page_source,
        1)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
