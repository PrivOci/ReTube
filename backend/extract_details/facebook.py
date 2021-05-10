from facebook_scraper import get_posts

global_video_details_url = {}

FACEBOOK = "fb"


async def get_facebook_page_source(details: dict):
    """Gather videos from a FB page.
    Not stable, after several requests fails without cookies/auth.
    TODO: maybe optional FB account
    """
    page_name = details["id"]
    try:
        posts_iterator = get_posts(page_name, page_limit=3)
    except:
        return None
    data_dict = {}
    data_dict["ready"] = False
    data_dict["platform"] = FACEBOOK
    video_entries = []
    for post in posts_iterator:
        if post["video"] == None or post["is_live"]:
            continue
        video_entry = {
            "platform": FACEBOOK,
            "id": details["id"],
            "title": post["text"][:100] if post["text"]
            else post["time"].strftime("%d/%m/%Y"),
            "author": post["username"],
            "channelUrl": post["user_url"].split("?")[0],
            "thumbnailUrl": post["video_thumbnail"],
            "createdAt": int(post["time"].timestamp()) * 1000,
            "videoUrl": post["post_url"],
        }

        video_url = video_entry["videoUrl"].split("facebook.com/")[1]
        global_video_details_url[video_url] = video_entry
        global_video_details_url[video_url]["description"] = post["post_text"]
        global_video_details_url[video_url]["streamUrl"] = post["video"]
        # global_video_details_url[video_url]["views"] =
        # global_video_details_url[video_url]["duration"] =

        video_entries.append(video_entry)
    data_dict["ready"] = True
    data_dict["content"] = video_entries if len(video_entries) else None
    return data_dict


def facebook_video_details(video_url):
    video_url = video_url.split("facebook.com/")[1]
    if video_url in global_video_details_url:
        return global_video_details_url[video_url]
    return None
