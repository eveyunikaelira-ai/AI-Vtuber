import argparse

from func.streaming.youtube_live_chat import listen_live_chat


def main() -> None:
    parser = argparse.ArgumentParser(description="YouTube live chat listener")
    parser.add_argument("--api-key", required=True, help="YouTube Data API v3 key.")
    parser.add_argument("--video-id", required=True, help="YouTube live video ID.")
    parser.add_argument(
        "--relay-url",
        default="http://localhost:9551/AI_VTuber/DANMU_MSG",
        help="Local relay endpoint for chat messages.",
    )
    args = parser.parse_args()
    listen_live_chat(api_key=args.api_key, video_id=args.video_id, relay_url=args.relay_url)


if __name__ == "__main__":
    main()
