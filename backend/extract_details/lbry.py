import requests
import json
import urllib.parse
import datetime

LBRY = "lb"

_headers = {
    'authority': 'api.lbry.tv',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537 (KHTML, like Gecko) Chrome/89 Safari/537',
    'content-type': 'application/json-rpc',
    'accept': '*/*',
    'origin': 'https://odysee.com',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://odysee.com/',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
}


def _get_details(lbry_urls):
    # converted from Curl via https://github.com/NickCarneiro/curlconverter
    data = {
        "jsonrpc": "2.0",
        "method": "resolve",
        "params": {
            "urls": lbry_urls,
            "include_purchase_receipt": True,
            "include_is_my_output": True
        },
    }

    response = requests.post(
        'https://api.lbry.tv/api/v1/proxy?m=resolve', headers=_headers, data=json.dumps(data))
    data = response.json()
    json_details = data["result"]
    return json_details


def get_video_url(lbry_url):
    # get video url
    data = {
        "jsonrpc": "2.0",
        "method": "get",
        "params": {
            "uri": lbry_url,
            "save_file": False,
        },
    }
    response = requests.post(
        'https://api.lbry.tv/api/v1/proxy?m=get', headers=_headers, data=json.dumps(data))
    data = response.json()
    streaming_url = data["result"]["streaming_url"]
    return streaming_url


def normal_to_lbry_url(normal_url):
    # lbry/odysee URL to lbry api accessible format
    protocol = "lbry://@"
    channel_and_video = normal_url.split("/@")[1].replace(":", "#")
    return f"{protocol}{channel_and_video}"


def lbry_to_normal_url(lbry_url):
    protocol = "https://odysee.com/@"
    channel_and_video = lbry_url.split("/@")[1].replace("#", ":")
    return f"{protocol}{channel_and_video}"


async def lbry_search_videos(search_query):
    search_terms = search_query["query"]
    max_results = search_query["max"]
    encoded_query = urllib.parse.quote(search_terms)

    data_dict = {}
    data_dict["platform"] = LBRY
    data_dict["ready"] = False
    headers = {
        'Referer': 'https://odysee.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537 (KHTML, like Gecko) Chrome/89 Safari/537',
    }
    response = requests.get(
        f'https://lighthouse.lbry.com/search?s={encoded_query}&free_only=true&size={max_results}&from=0&nsfw=false', headers=headers)
    results_json = response.json()
    if not response.ok:
        # if no results
        return data_dict
    lbry_videos = [
        f"lbry://{lbry_video['name']}#{lbry_video['claimId']}" for lbry_video in results_json]
    video_details = _get_details(lbry_videos)
    video_entries = []
    for entry in video_details:
        entry = video_details[entry]
        video_entry = _parse_lbry_details(entry)
        if video_entry:
            video_entries.append(video_entry)

    data_dict["ready"] = True
    data_dict["content"] = video_entries
    return data_dict


def _parse_lbry_details(entry) -> dict:
    video_entry = {}
    if 'value' not in entry:
        return {}
    if 'thumbnail' not in entry["value"]:
        return {}
    video_entry["platform"] = LBRY

    if 'url' in entry["value"]["thumbnail"]:
        video_entry["thumbSrc"] = entry["value"]["thumbnail"]["url"]
    else:
        video_entry["thumbSrc"] = "https://user-images.githubusercontent.com/74614193/112720980-68bab700-8ef9-11eb-9319-0e79508b6e7e.png"
    if "title" in entry["value"]:
        video_entry["title"] = entry["value"]["title"]
    else:
        video_entry["title"] = entry["name"]
    if entry["value_type"] == "channel":
        video_entry["isChannel"] = True
        video_entry["channelUrl"] = lbry_to_normal_url(entry["canonical_url"])
    elif entry["value_type"] == "stream" and 'video' in entry["value"]:
        if 'value' not in entry["signing_channel"]:
            video_entry["channel"] = "Anonymous"
        else:
            video_entry["channel"] = entry["signing_channel"]["value"].get(
                "title", entry["signing_channel"]["name"])
        video_entry["duration"] =  entry["value"]["video"]["duration"]
        video_entry["views"] = ""
        video_entry["createdAt"] = int(entry["timestamp"]) * 1000
        video_entry["videoUrl"] = lbry_to_normal_url(entry["canonical_url"])
    else:
        return video_entry

    return video_entry


def lbry_video_details(video_url):
    lbry_url = normal_to_lbry_url(video_url)

    json_details = _get_details([lbry_url])[lbry_url]
    video_url = get_video_url(lbry_url)
    claim_id = json_details["claim_id"]
    view_count = get_view_count(claim_id)

    video_details = {
        "id": claim_id,
        "title": json_details["value"]["title"],
        "description": json_details["value"].get(
            "description", ""),
        "author": json_details["signing_channel"]["value"].get(
            "title", json_details["signing_channel"]["name"]),
        "channelUrl":
            json_details["signing_channel"]["short_url"].replace(
                "lbry://", "https://odysee.com/").replace("#", ":"),
        "duration": json_details["value"]["video"]["duration"],
        "viewCount": view_count,
        "averageRating": "",
        "likeCount": "",
        "dislikeCount": "",
        "thumbnail": json_details["value"]["thumbnail"]["url"],
        "createdAt":int(json_details["timestamp"]) * 1000,
        "streamUrl": video_url,
    }
    return video_details


def get_view_count(claim_id):
    # get auth_token cookie
    # session = requests.Session()
    # session.get('https://odysee.com/$/help')
    # cookies = session.cookies.get_dict()
    # TODO: remove the hardcoded value
    auth_token = "7TCpVMwB4AYWsoihB2Emaj7G5pEZZ8zE"  # cookies["auth_token"]

    response = requests.get(
        f'https://api.lbry.com/file/view_count?auth_token={auth_token}&claim_id={claim_id}', headers=_headers)
    data = response.json()
    if "success" in data and data["success"] == True:
        return data["data"][0]
    else:
        return 0


def lbry_channel_details(channel_id):
    channel_url = f"https://odysee.com/@{channel_id}"
    lbry_url = normal_to_lbry_url(channel_url)
    channel_details = _get_details([lbry_url])[lbry_url]
    channel_id = channel_details["claim_id"]

    data = {
        "jsonrpc": "2.0",
        "method": "claim_search",
        "params": {
            "page_size": 20,
            "page": 1,
            "no_totals": True,
            "not_channel_ids": [],
            "not_tags": [],
            "order_by": [
                "release_time"
            ],
            "fee_amount": ">=0",
            "channel_ids": [
                channel_id
            ],
            "stream_types": [
                "video"
            ],
            "include_purchase_receipt": True
        },
    }

    response = requests.post(
        'https://api.lbry.tv/api/v1/proxy?m=claim_search', headers=_headers, data=json.dumps(data))

    data = response.json()

    data_dict = {}
    data_dict["platform"] = LBRY
    video_entries = []
    for entry in data["result"]["items"]:
        video_entry = _parse_lbry_details(entry)
        if video_entry:
            video_entries.append(video_entry)

    data_dict["content"] = video_entries
    data_dict["ready"] = True
    return data_dict


async def lbry_popular():
    week_ago_date = int(
        (datetime.datetime.now() - datetime.timedelta(days=7)).timestamp())

    data = {
        "jsonrpc": "2.0",
        "method": "claim_search",
        "params": {
            "page_size": 20,
            "page": 1,
            "claim_type": [
                "stream"
            ],
            "no_totals": True,
            "not_channel_ids": [],
            "not_tags": [],
            "order_by": [
                "effective_amount"
            ],
            "limit_claims_per_channel": 1,
            "fee_amount": "<=0",
            "release_time": f">{week_ago_date}",
            "stream_types": [
                "video"
            ],
            "include_purchase_receipt": True
        },
    }

    response = requests.post(
        'https://api.lbry.tv/api/v1/proxy?m=claim_search', headers=_headers, data=json.dumps(data))
    if not response.ok:
        return {}
    results_json = response.json()

    data_dict = {}
    data_dict["platform"] = LBRY
    video_entries = []
    for entry in results_json["result"]["items"]:
        video_entry = _parse_lbry_details(entry)
        if video_entry:
            video_entries.append(video_entry)

    data_dict["content"] = video_entries
    data_dict["ready"] = True
    return data_dict


async def lbry_channel_search(search_query):
    '''Searches for channels in Lbry.

    Args:
        search_terms (str): search query.
    '''
    channel_name = search_query["query"]
    max_results = search_query["max"]
    channel_name = channel_name.replace(" ", "").replace("+", "")
    channel_name = f"lbry://@{channel_name}"
    data = {
        "jsonrpc": "2.0",
        "method": "resolve",
        "params": {
            "urls": [
                channel_name
            ],
            "include_purchase_receipt": True
        }
    }

    response = requests.post(
        'https://api.lbry.tv/api/v1/proxy?m=resolve', headers=_headers, data=json.dumps(data))
    data = response.json()

    data_dict = {}
    data_dict["platform"] = LBRY
    video_entries = []
    for entry in data["result"]:
        current_entry = data["result"][entry]
        if "error" in current_entry:
            continue
        video_entry = _parse_lbry_details(current_entry)
        if video_entry:
            video_entries.append(video_entry)

    data_dict["content"] = video_entries
    data_dict["ready"] = True
    return data_dict
