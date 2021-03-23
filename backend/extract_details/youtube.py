from youtube_search import YoutubeSearch

YOUTUBE = "yt"

async def youtube_search_videos(search_query):
    search_words = search_query["query"]
    max_results = search_query["max"]
    
    results_json = YoutubeSearch(search_words, max_results=max_results)
    data_dict = {}
    data_dict["platform"] = YOUTUBE
    video_entries = []
    for video in results_json.videos:
        video_entry = {}
        video_entry["thumbSrc"] = video["thumbnails"][0].split("?sqp")[0]
        video_entry["title"] = video["title"]
        video_entry["channel"] = video["channel"]
        video_entry["views"] = ""
        video_entry["createdAt"] = ""
        video_entry["videoUrl"] = f"https://youtube.com{video['url_suffix']}"
        video_entry["platform"] = YOUTUBE
        video_entries.append(video_entry)

    data_dict["content"] = video_entries
    data_dict["ready"] = True
    return data_dict