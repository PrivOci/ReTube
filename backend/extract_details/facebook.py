import facebook_scraper
import os.path
from loguru import logger


class FacebookProcessor:
    """Class to process Facebook videos and pages."""
    FACEBOOK = "fb"

    def __init__(self) -> None:
        self.global_video_details_url = {}
        curr_path = os.path.dirname(os.path.realpath(__file__))
        credentials_file = f"{curr_path}/credentials"
        self.username = None
        self.password = None
        # Make sure there is no ":" symbol in a password
        if os.path.isfile(credentials_file):
            with open(credentials_file, 'r') as f:
                for curr_line in f:
                    if curr_line.startswith("fb:"):
                        self.username, self.password = curr_line.removeprefix(
                            "fb:").split(":")
                        break
        else:
            logger.debug(
                f"Failed to locate credentials file: {credentials_file}\n")

    def channel_data(self, details: dict):
        """Gather videos from a FB page.
        Not stable, after several requests fails without cookies/auth.
        TODO: maybe optional FB account
        """
        page_name = details["id"]
        data_dict = {}
        data_dict["ready"] = False
        data_dict["platform"] = self.FACEBOOK

        if self.username and self.password:
            try:
                posts_iterator = facebook_scraper.get_posts(
                    page_name, page_limit=3, credentials=(r"{}".format(self.username), r"{}".format(self.password)))
            except facebook_scraper.exceptions.LoginError as err:
                logger.debug(
                    f"failed to login Facebook\nerr: {err}\nUsername: {self.username}\n")
                posts_iterator = facebook_scraper.get_posts(
                    page_name, page_limit=3)
        else:
            posts_iterator = facebook_scraper.get_posts(
                page_name, page_limit=3)

        video_entries = []
        try:
            for post in posts_iterator:
                if not post["video"] or post["is_live"]:
                    continue
                video_entry = {
                    "platform": self.FACEBOOK,
                    "id": details["id"],
                    "title": post["text"][:100] if post["text"]
                    else post["time"].strftime("%d/%m/%Y"),
                    "author": post["username"],
                    "channelUrl": post["user_url"].split("?")[0],
                    "thumbnailUrl": post["video_thumbnail"],
                    "createdAt": int(post["time"].timestamp()) * 1000,
                    "videoUrl": post["post_url"],
                    "duration": post["video_duration_seconds"],
                    "views": post["video_watches"],
                }

                video_url = video_entry["videoUrl"].split("facebook.com/")[1]
                self.global_video_details_url[video_url] = video_entry
                self.global_video_details_url[video_url]["description"] = post["post_text"]
                self.global_video_details_url[video_url]["streamUrl"] = post["video"]

                video_entries.append(video_entry)
        except:
            return data_dict
        if not video_entries:
            return data_dict
        data_dict["ready"] = True
        data_dict["content"] = video_entries if len(video_entries) else None
        return data_dict

    def get_video_details(self, video_url):
        video_url = video_url.split("facebook.com/")[1]
        if video_url in self.global_video_details_url:
            return self.global_video_details_url[video_url]
        return None
