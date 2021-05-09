from facebook_scraper import get_posts

async def get_facebook_page_source(page_name):
    """Gather videos from a FB page.
    Not stable, after several requests fails without cookies/auth.
    TODO: maybe optional FB account
    """
    try:
        posts_iterator = get_posts(page_name, page_limit=1)
    except:
        return None
    video_entries = []
    for post in posts_iterator:
        if post["video"] == None or post["is_live"]:
            continue
        video_entry = {
            "id": post["video_id"],
            "title": post["text"],
            "description": post["post_text"],
            "author": post["username"],
            "channelUrl": post["user_url"],
            # duration
            # viewCount
            "thumbnailUrl": post["video_thumbnail"],
            "createdAt": int(post["time"].timestamp()),
            "streamUrl": post["video"],
        }
        video_entries.append(video_entry)
    return video_entries if len(video_entries) else None