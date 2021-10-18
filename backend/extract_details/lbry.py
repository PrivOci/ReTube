import datetime
import json
import urllib.parse

import requests


class LbryProcessor:
    """Class to process Lbry/Odysee videos and channels."""

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

    def __init__(self) -> None:
        self.session = requests.Session()

    def _get_details(self, lbry_urls):
        data = {
            "jsonrpc": "2.0",
            "method": "resolve",
            "params": {
                "urls": lbry_urls,
                "include_purchase_receipt": True,
                "include_is_my_output": True
            },
        }

        response = self.session.post(
            'https://api.lbry.tv/api/v1/proxy?m=resolve', headers=self._headers, data=json.dumps(data))
        data = response.json()
        json_details = data["result"]
        return json_details

    def _get_video_url(self, lbry_url):
        # get video url
        data = {
            "jsonrpc": "2.0",
            "method": "get",
            "params": {
                "uri": lbry_url,
                "save_file": False,
            },
        }
        response = self.session.post(
            'https://api.lbry.tv/api/v1/proxy?m=get', headers=self._headers, data=json.dumps(data))
        data = response.json()
        return data["result"]["streaming_url"] if "result" in data else None

    def _normal_to_lbry_url(self, normal_url):
        # lbry/odysee URL to lbry api accessible format
        protocol = "lbry://"
        channel_and_video = normal_url.split(
            "odysee.com/")[1].replace(":", "#")
        return f"{protocol}{channel_and_video}"

    def _lbry_to_normal_url(self, lbry_url):
        protocol = "https://odysee.com/"
        channel_and_video = lbry_url.split("lbry://")[1].replace("#", ":")
        return f"{protocol}{channel_and_video}"

    def search_video(self, search_query) -> dict:
        search_terms = search_query["query"]
        max_results = search_query["max"]
        encoded_query = urllib.parse.quote(search_terms)

        data_dict = {
            "platform": self.LBRY,
            "ready": False
        }
        headers = {
            'Referer': 'https://odysee.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537 (KHTML, like Gecko) Chrome/89 '
                          'Safari/537',
        }
        response = self.session.get(
            f'https://lighthouse.lbry.com/search?s={encoded_query}&mediaType=video&free_only=true&size={max_results}&from=0&nsfw=false',
            headers=headers)
        results_json = response.json()
        if not response.ok:
            # if no results
            return data_dict
        lbry_videos = [
            f"lbry://{lbry_video['name']}#{lbry_video['claimId']}" for lbry_video in results_json]
        video_details = self._get_details(lbry_videos)
        video_entries = []
        for entry in video_details:
            entry = video_details[entry]
            video_entry = self._parse_lbry_details(entry)
            if video_entry:
                video_entries.append(video_entry)

        data_dict["ready"] = True
        data_dict["content"] = video_entries
        return data_dict

    def _parse_lbry_details(self, entry) -> dict:
        video_entry = {}
        if 'value' not in entry:
            return {}
        if 'thumbnail' not in entry["value"]:
            return {}
        video_entry["platform"] = self.LBRY

        if 'url' in entry["value"]["thumbnail"]:
            video_entry["thumbnailUrl"] = entry["value"]["thumbnail"]["url"]
        else:
            video_entry[
                "thumbnailUrl"] = "https://user-images.githubusercontent.com/74614193/112720980-68bab700-8ef9-11eb" \
                                  "-9319-0e79508b6e7e.png "
        if "title" in entry["value"]:
            video_entry["title"] = entry["value"]["title"]
        else:
            video_entry["title"] = entry["name"]
        if entry["value_type"] == "channel":
            video_entry["isChannel"] = True
            video_entry["channelUrl"] = self._lbry_to_normal_url(
                entry["canonical_url"])
        elif entry["value_type"] == "stream" and 'video' in entry["value"]:
            if 'value' not in entry["signing_channel"]:
                video_entry["author"] = "Anonymous"
            else:
                video_entry["author"] = entry["signing_channel"]["value"].get(
                    "title", entry["signing_channel"]["name"])
                video_entry["channelUrl"] = self._lbry_to_normal_url(
                    entry["signing_channel"]["short_url"])
            video_entry["duration"] = entry["value"]["video"]["duration"]
            video_entry["views"] = ""
            video_entry["createdAt"] = int(entry["timestamp"]) * 1000
            video_entry["videoUrl"] = self._lbry_to_normal_url(
                entry["canonical_url"])
        else:
            return video_entry

        return video_entry

    def get_video_details(self, video_url):
        video_url = urllib.parse.unquote(video_url)
        lbry_url = self._normal_to_lbry_url(video_url)

        video_url = self._get_video_url(lbry_url)
        if not video_url:
            return None
        json_details = self._get_details([lbry_url])[lbry_url]
        claim_id = json_details["claim_id"]
        view_count = self._get_view_count(claim_id)

        video_details = self._parse_lbry_details(json_details)
        video_details["id"] = claim_id
        video_details["views"] = view_count
        video_details["streamUrl"] = video_url
        video_details["description"] = json_details["value"].get(
            "description", "")

        return video_details

    def _get_view_count(self, claim_id):
        # get auth_token cookie
        # session = requests.Session()
        # session.get('https://odysee.com/$/help')
        # cookies = session.cookies.get_dict()
        # TODO: remove the hardcoded value
        # cookies["auth_token"]
        auth_token = "5v4AcLe2fxSQ9Vxf1TV8bi4jKoxjj8Ut"

        response = self.session.get(
            f'https://api.lbry.com/file/view_count?auth_token={auth_token}&claim_id={claim_id}', headers=self._headers)
        data = response.json()
        if "success" in data and data["success"] == True:
            return data["data"][0]
        else:
            return 0

    def channel_data(self, channel_id) -> dict:
        channel_url = f"https://odysee.com/@{channel_id}"
        lbry_url = self._normal_to_lbry_url(channel_url)
        channel_details = self._get_details([lbry_url])[lbry_url]
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

        response = self.session.post(
            'https://api.lbry.tv/api/v1/proxy?m=claim_search', headers=self._headers, data=json.dumps(data))

        data = response.json()

        data_dict = {"platform": self.LBRY}

        data_dict["channel_meta"] = {
            "title": channel_details["value"]["title"],
            "channelUrl": channel_url,
            "banner": channel_details["value"]["cover"]["url"],
            "avatar": channel_details["value"]["thumbnail"]["url"],
            "subscriberCount": None
        }

        video_entries = []
        for entry in data["result"]["items"]:
            video_entry = self._parse_lbry_details(entry)
            if video_entry:
                video_entries.append(video_entry)

        data_dict["content"] = video_entries
        data_dict["ready"] = True
        return data_dict

    def get_popular(self) -> dict:
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

        response = self.session.post(
            'https://api.lbry.tv/api/v1/proxy?m=claim_search', headers=self._headers, data=json.dumps(data))
        if not response.ok:
            return {}
        results_json = response.json()

        data_dict = {"platform": self.LBRY}
        video_entries = []
        for entry in results_json["result"]["items"]:
            video_entry = self._parse_lbry_details(entry)
            if video_entry:
                video_entries.append(video_entry)

        data_dict["content"] = video_entries
        data_dict["ready"] = True
        return data_dict

    def search_for_channels(self, search_query):
        """Searches for channels in Lbry.

        Args:
            search_query (str): search query.
        """
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

        response = self.session.post(
            'https://api.lbry.tv/api/v1/proxy?m=resolve', headers=self._headers, data=json.dumps(data))
        data = response.json()

        data_dict = {"platform": self.LBRY}
        video_entries = []
        for entry in data["result"]:
            current_entry = data["result"][entry]
            if "error" in current_entry:
                continue
            video_entry = self._parse_lbry_details(current_entry)
            if video_entry:
                video_entries.append(video_entry)

        data_dict["content"] = video_entries
        data_dict["ready"] = True
        return data_dict
