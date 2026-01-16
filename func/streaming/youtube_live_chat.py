import time
from typing import Dict, List, Optional, Tuple

import requests


YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"


def get_live_chat_id(api_key: str, video_id: str) -> Optional[str]:
    response = requests.get(
        f"{YOUTUBE_API_BASE}/videos",
        params={"part": "liveStreamingDetails", "id": video_id, "key": api_key},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    items = data.get("items", [])
    if not items:
        return None
    return items[0].get("liveStreamingDetails", {}).get("activeLiveChatId")


def fetch_live_chat_messages(
    api_key: str, live_chat_id: str, page_token: Optional[str] = None
) -> Tuple[List[Dict[str, str]], Optional[str], int]:
    params = {
        "part": "snippet,authorDetails",
        "liveChatId": live_chat_id,
        "key": api_key,
    }
    if page_token:
        params["pageToken"] = page_token
    response = requests.get(f"{YOUTUBE_API_BASE}/liveChat/messages", params=params, timeout=10)
    response.raise_for_status()
    payload = response.json()
    messages = []
    for item in payload.get("items", []):
        author = item.get("authorDetails", {}).get("displayName", "YouTube Viewer")
        content = item.get("snippet", {}).get("displayMessage", "")
        messages.append({"audience_name": author, "DANMU_MSG": content})
    return messages, payload.get("nextPageToken"), payload.get("pollingIntervalMillis", 2000)


def listen_live_chat(
    api_key: str,
    video_id: str,
    relay_url: str = "http://localhost:9551/AI_VTuber/DANMU_MSG",
) -> None:
    live_chat_id = get_live_chat_id(api_key, video_id)
    if not live_chat_id:
        raise ValueError("No active live chat found. Make sure the video is live.")
    page_token = None
    while True:
        messages, page_token, interval_ms = fetch_live_chat_messages(api_key, live_chat_id, page_token)
        for message in messages:
            try:
                requests.post(relay_url, json=message, timeout=3)
            except requests.RequestException:
                continue
        time.sleep(interval_ms / 1000)
