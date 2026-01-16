# -*- coding: utf-8 -*-
import argparse
import asyncio
import requests
import tools.blivedm.blivedm as blivedm
import tools.blivedm.blivedm.models.open_live as open_models
import tools.blivedm.blivedm.models.web as web_models


async def main(ACCESS_KEY_ID, ACCESS_KEY_SECRET, APP_ID, ROOM_OWNER_AUTH_CODE):
    """
    Args:
        ACCESS_KEY_ID: Developer key from BiliBili Open Platform.
        ACCESS_KEY_SECRET: Developer secret from BiliBili Open Platform.
        APP_ID: Application ID created in BiliBili Open Platform.
        ROOM_OWNER_AUTH_CODE: Streamer authorization code.
    """
    await run_single_client(ACCESS_KEY_ID,ACCESS_KEY_SECRET,APP_ID,ROOM_OWNER_AUTH_CODE)


async def run_single_client(ACCESS_KEY_ID,ACCESS_KEY_SECRET,APP_ID,ROOM_OWNER_AUTH_CODE):
    """Listen to a single BiliBili live room."""
    client = blivedm.OpenLiveClient(
        access_key_id=ACCESS_KEY_ID,
        access_key_secret=ACCESS_KEY_SECRET,
        app_id=APP_ID,
        room_owner_auth_code=ROOM_OWNER_AUTH_CODE,
    )
    handler = MyHandler()
    client.set_handler(handler)

    client.start()
    try:
        # Example: stop after 70 seconds
        # await asyncio.sleep(70)
        # client.stop()

        await client.join()
    finally:
        await client.stop_and_close()


class MyHandler(blivedm.BaseHandler):
    def _on_heartbeat(self, client: blivedm.BLiveClient, message: web_models.HeartbeatMessage):
        print(f'[{client.room_id}] heartbeat')

    def _on_open_live_danmaku(self, client: blivedm.OpenLiveClient, message: open_models.DanmakuMessage):
        print(f'[{message.room_id}] {message.uname}: {message.msg}')
        DANMU_dict = {"audience_name": message.uname, "DANMU_MSG": message.msg}
        requests.post('http://localhost:9551/AI_VTuber/DANMU_MSG', json=DANMU_dict)

    def _on_open_live_gift(self, client: blivedm.OpenLiveClient, message: open_models.GiftMessage):
        coin_type = 'Gold Seeds' if message.paid else 'Silver Seeds'
        total_coin = message.price * message.gift_num
        print(
            f'[{message.room_id}] {message.uname} sent {message.gift_name}x{message.gift_num}'
            f' ({coin_type}x{total_coin})'
        )

    def _on_open_live_buy_guard(self, client: blivedm.OpenLiveClient, message: open_models.GuardBuyMessage):
        print(f'[{message.room_id}] {message.user_info.uname} bought Guard level={message.guard_level}')

    def _on_open_live_super_chat(
        self, client: blivedm.OpenLiveClient, message: open_models.SuperChatMessage
    ):
        print(f'[{message.room_id}] Super Chat ¥{message.rmb} {message.uname}: {message.message}')

    def _on_open_live_super_chat_delete(
        self, client: blivedm.OpenLiveClient, message: open_models.SuperChatDeleteMessage
    ):
        print(f'[{message.room_id}] Deleted Super Chat message_ids={message.message_ids}')

    def _on_open_live_like(self, client: blivedm.OpenLiveClient, message: open_models.LikeMessage):
        print(f'[{message.room_id}] {message.uname} liked')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='blivedm parameters')
    parser.add_argument('-AKI', '--ACCESS_KEY_ID', type=str)
    parser.add_argument('-AKS', '--ACCESS_KEY_SECRET', type=str)
    parser.add_argument('-AI', '--APP_ID', type=int)
    parser.add_argument('-ROAC', '--ROOM_OWNER_AUTH_CODE', type=str)
    args = parser.parse_args()
    ACCESS_KEY_ID = args.ACCESS_KEY_ID
    ACCESS_KEY_SECRET = args.ACCESS_KEY_SECRET
    APP_ID = args.APP_ID
    ROOM_OWNER_AUTH_CODE = args.ROOM_OWNER_AUTH_CODE
    asyncio.run(main(ACCESS_KEY_ID,ACCESS_KEY_SECRET,APP_ID,ROOM_OWNER_AUTH_CODE))
