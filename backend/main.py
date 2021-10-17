from datetime import datetime

import uvicorn
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.tasks import repeat_every
from loguru import logger
from pydantic import BaseModel

import utils.optimize as optimize
from extract_details.bitchute import BitchuteProcessor
from extract_details.lbry import LbryProcessor
from extract_details.rumble import RumbleProcessor
from extract_details.youtube import YoutubeProcessor
from utils.spelling import ginger_check_sentence

app = FastAPI()
bc_processor = BitchuteProcessor()
yt_processor = YoutubeProcessor()
lbry_processor = LbryProcessor()
rb_processor = RumbleProcessor()


def debugger_is_active() -> bool:
    """Return if the debugger is currently active"""
    gettrace = getattr(sys, 'gettrace', lambda: None)
    return gettrace() is not None


# Disable caching when debugged
optimize.DISABLE_CACHE = debugger_is_active()

ALLOWED_HOSTS = None
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

YOUTUBE = "yt"
LBRY = "lb"
BITCHUTE = "bc"
RUMBLE = "rb"


class RequestDetails(BaseModel):
    platform: str
    id: str


class SearchQuery(BaseModel):
    query: str
    max: int


class JustString(BaseModel):
    query: str


LB_VIDEO_URL = "https://odysee.com/"
YT_VIDEO_URL = "https://www.youtube.com/watch?v="
BT_VIDEO_URL = "https://www.bitchute.com/video/"
RB_VIDEO_URL = "https://rumble.com/"

# global list of channel URLs to prefetch them each hour.
# Only prefetched recently requested URLs
global_yt_urls = {}
global_lbry_urls = {}
global_bc_urls = {}
global_rb_urls = {}


async def prefetch_channels(platform, channels, source_function) -> None:
    """
    Prefetch channels requested within a day, remove rest.
    """
    details = {"platform": platform}
    now = datetime.utcnow()
    for (channel_id, req_date) in channels.items():
        details["id"] = channel_id
        difference = now - req_date
        if difference.days != 0:
            del channels[channel_id]
            continue
        logger.debug(
            f"prefetch: {details['channel_id']} - {details['platform']}")
        await optimize.optimized_request(dict(details), source_function, 1, forced=True)


@app.on_event("startup")
@repeat_every(seconds=60 * 50)  # 50 mins
async def prefetch_yt_channels() -> None:
    await prefetch_channels(YOUTUBE, global_yt_urls, yt_processor.channel_data)


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
async def prefetch_rb_channels() -> None:
    await prefetch_channels(RUMBLE, global_rb_urls, rb_processor.channel_data)


@app.post("/api/check")
async def check_sentence(just_string: JustString):
    return ginger_check_sentence(just_string.query)


@app.post("/api/video/")
async def get_video(details: RequestDetails) -> dict:
    details.id = details.id.strip().strip("/")
    # YT video link expires
    if details.platform == YOUTUBE:
        return get_video_from_source(dict(details))
    return await optimize.optimized_request(dict(details), get_video_from_source, 72)


def get_video_from_source(details: dict) -> dict:
    result = {'ready': False}

    # prepare video_url
    video_url = None
    if details["platform"] == LBRY:
        video_url = LB_VIDEO_URL + details["id"]
    elif details["platform"] == YOUTUBE:
        video_url = YT_VIDEO_URL + details["id"]
    elif details["platform"] == BITCHUTE:
        video_url = BT_VIDEO_URL + details["id"]
    elif details["platform"] == RUMBLE:
        video_url = RB_VIDEO_URL + details["id"] + ".html"
    else:
        return result

    # our extractors
    if details["platform"] == YOUTUBE:
        result["platform"] = YOUTUBE
        result["content"] = yt_processor.get_video_details(video_url)
        result['ready'] = result["content"] is not None
        return result
    elif details["platform"] == BITCHUTE:
        result["platform"] = BITCHUTE
        result["content"] = bc_processor.get_video_details(video_url)
        result['ready'] = result["content"] is not None
        return result
    elif details["platform"] == LBRY:
        result["platform"] = LBRY
        result["content"] = lbry_processor.get_video_details(video_url)
        result['ready'] = result["content"] is not None
        return result
    elif details["platform"] == RUMBLE:
        result["platform"] = RUMBLE
        result["content"] = rb_processor.get_video_details(video_url)
        result['ready'] = result["content"] is not None
        return result
    else:
        return result


# YouTube channel to JSON
@app.post("/api/youtube/c/")
async def get_youtube_channel(details: RequestDetails) -> dict:
    details = dict(details)
    details["id"] = details["id"].strip().strip("/")
    details["channel"] = True
    global_yt_urls[details["id"]] = datetime.utcnow()
    return await optimize.optimized_request(
        dict(details),
        yt_processor.channel_data,
        1)


# YouTube playlist to JSON
@app.post("/api/youtube/p/")
async def get_youtube_playlist(details: RequestDetails) -> dict:
    details = dict(details)
    details["id"] = details["id"].strip().strip("/")
    if details["id"] == "popular":
        details["id"] = "PLrEnWoR732-BHrPp_Pm8_VleD68f9s14-"
    details["playlist"] = True
    return await optimize.optimized_request(
        dict(details),
        yt_processor.channel_data,
        1)


# search youtube videos
@app.post("/api/youtube/search/")
async def youtube_search_results(search_query: SearchQuery) -> dict:
    search_query = dict(search_query)
    search_query["platform"] = YOUTUBE
    result = await optimize.optimized_request(
        dict(search_query),
        yt_processor.search_video,
        1)
    return result


# search youtube channels
@app.post("/api/youtube/channels/")
async def youtube_search_channels(search_query: SearchQuery) -> dict:
    search_query = dict(search_query)
    search_query["platform"] = YOUTUBE
    search_query["max"] = 3
    result = await optimize.optimized_request(
        dict(search_query),
        yt_processor.search_for_channels,
        1)
    return result


# search Lbry channels
@app.post("/api/lbry/channels/")
async def lbry_search_channels(search_query: SearchQuery) -> dict:
    search_query = dict(search_query)
    search_query["platform"] = LBRY
    search_query["max"] = 3
    result = await optimize.optimized_request(
        dict(search_query),
        lbry_processor.search_for_channels,
        1)
    return result


# search bitchute videos
@app.post("/api/bitchute/search/")
async def bitchute_search_results(search_query: SearchQuery) -> dict:
    search_query = dict(search_query)
    search_query["platform"] = BITCHUTE
    result = await optimize.optimized_request(
        dict(search_query),
        bc_processor.search_video,
        1)
    return result


# search youtube videos
@app.post("/api/lbry/search/")
async def lbry_search_results(search_query: SearchQuery) -> dict:
    search_query = dict(search_query)
    search_query["platform"] = LBRY
    result = await optimize.optimized_request(
        dict(search_query),
        lbry_processor.search_video,
        1)
    return result


# search rumble videos
@app.post("/api/rumble/search/")
async def rb_search_results(search_query: SearchQuery) -> dict:
    search_query = dict(search_query)
    search_query["platform"] = RUMBLE
    result = await optimize.optimized_request(
        dict(search_query),
        rb_processor.search_for_videos,
        1)
    return result


# Lbry/Odysee channel to JSON
@app.post("/api/lbry/c/")
async def get_lbry_channel(details: RequestDetails) -> dict:
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
        return lbry_processor.get_popular()
    return lbry_processor.channel_data(details['id'])


# Rumble channel to JSON
@app.post("/api/rumble/c/")
async def get_lbry_channel(details: RequestDetails) -> dict:
    details = dict(details)
    details["id"] = details["id"].strip().strip("/")
    global_rb_urls[details["id"]] = datetime.utcnow()
    return await optimize.optimized_request(
        dict(details),
        rb_processor.channel_data,
        1)


# BitChute channel to JSON
@app.post("/api/bitchute/c/")
async def get_bitchute_channel(details: RequestDetails):
    details = dict(details)
    details["id"] = details["id"].strip().strip("/")
    details["channel"] = True
    global_bc_urls[details["id"]] = datetime.utcnow()
    return await optimize.optimized_request(
        dict(details),
        bc_processor.channel_data,
        1)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
