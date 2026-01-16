import argparse

from func.streaming.twitch_chat import TwitchChatListener


def main() -> None:
    parser = argparse.ArgumentParser(description="Twitch chat listener")
    parser.add_argument("--username", required=True, help="Twitch username (login name).")
    parser.add_argument("--oauth-token", required=True, help="OAuth token (format: oauth:xxxx).")
    parser.add_argument("--channel", required=True, help="Channel name to join.")
    parser.add_argument(
        "--relay-url",
        default="http://localhost:9551/AI_VTuber/DANMU_MSG",
        help="Local relay endpoint for chat messages.",
    )
    args = parser.parse_args()
    listener = TwitchChatListener(
        username=args.username,
        oauth_token=args.oauth_token,
        channel=args.channel,
        relay_url=args.relay_url,
    )
    listener.listen_forever()


if __name__ == "__main__":
    main()
