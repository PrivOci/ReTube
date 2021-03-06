from extract_details.youtube import YoutubeProcessor
from extract_details.bitchute import BitchuteProcessor
from extract_details.lbry import LbryProcessor
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
yt_processor = YoutubeProcessor()
lbry_processor = LbryProcessor()

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

# global list of channel URLs to prefetch them each hour.
# Only prefetched recently requested URLs
global_yt_urls = {}
global_lbry_urls = {}
global_bc_urls = {}


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
    await prefetch_channels(YOUTUBE, global_yt_urls, yt_processor.channel_data)


@app.on_event("startup")
@repeat_every(seconds=60 * 50)  # 50 mins
async def prefetch_lbry_channels() -> None:
    await prefetch_channels(LBRY, global_lbry_urls, get_lbry_channel_source)


@app.on_event("startup")
@repeat_every(seconds=60 * 50)  # 50 mins
async def prefetch_bc_channels() -> None:
    await prefetch_channels(BITCHUTE, global_bc_urls, bc_processor.channel_data)


@app.post("/api/check")
async def check_sentence(just_string: just_string):
    return ginger_check_sentence(just_string.query)


@app.post("/api/video/")
async def get_video(details: request_details) -> dict:
    details.id = details.id.strip().strip("/")
    # YT video link expires
    if (details.platform == YOUTUBE):
        return get_video_from_source(dict(details))
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
    else:
        return result

    # our extractors
    if details["platform"] == YOUTUBE:
        result["platform"] = YOUTUBE
        result["content"] = yt_processor.get_video_details(video_url)
        result['ready'] = result["content"] != None
        return result
    elif details["platform"] == BITCHUTE:
        result["platform"] = BITCHUTE
        result["content"] = bc_processor.get_video_details(video_url)
        result['ready'] = result["content"] != None
        return result
    elif details["platform"] == LBRY:
        result["platform"] = LBRY
        result["content"] = lbry_processor.get_video_details(video_url)
        result['ready'] = result["content"] != None
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
        yt_processor.channel_data,
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
        yt_processor.channel_data,
        1)


# search youtube videos
@app.post("/api/youtube/search/")
async def youtube_search_results(search_query: search_query) -> dict:
    search_query = dict(search_query)
    search_query["platform"] = YOUTUBE
    result = await optimize.optimized_request(
        dict(search_query),
        yt_processor.search_video,
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
        yt_processor.search_for_channels,
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
        lbry_processor.search_for_channels,
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
        lbry_processor.search_video,
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
        return lbry_processor.get_popular()
    return lbry_processor.channel_data(details['id'])


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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
