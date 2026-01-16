import socket
import ssl
import time
from typing import Optional

import requests


TWITCH_IRC_HOST = "irc.chat.twitch.tv"
TWITCH_IRC_PORT = 6697


class TwitchChatListener:
    def __init__(
        self,
        username: str,
        oauth_token: str,
        channel: str,
        relay_url: str = "http://localhost:9551/AI_VTuber/DANMU_MSG",
        reconnect_delay_s: int = 5,
    ) -> None:
        self.username = username
        self.oauth_token = oauth_token
        self.channel = channel.lstrip("#")
        self.relay_url = relay_url
        self.reconnect_delay_s = reconnect_delay_s
        self._socket: Optional[socket.socket] = None

    def _connect(self) -> socket.socket:
        raw_socket = socket.create_connection((TWITCH_IRC_HOST, TWITCH_IRC_PORT))
        secure_socket = ssl.create_default_context().wrap_socket(raw_socket, server_hostname=TWITCH_IRC_HOST)
        secure_socket.sendall(f"PASS {self.oauth_token}\r\n".encode("utf-8"))
        secure_socket.sendall(f"NICK {self.username}\r\n".encode("utf-8"))
        secure_socket.sendall(f"JOIN #{self.channel}\r\n".encode("utf-8"))
        self._socket = secure_socket
        return secure_socket

    def _send_pong(self, message: str) -> None:
        if not self._socket:
            return
        response = message.replace("PING", "PONG")
        self._socket.sendall(f"{response}\r\n".encode("utf-8"))

    def _handle_privmsg(self, message: str) -> None:
        if "PRIVMSG" not in message:
            return
        prefix, trailing = message.split(" PRIVMSG ", 1)
        username = prefix.split("!", 1)[0].lstrip(":")
        chat_message = trailing.split(" :", 1)[-1]
        payload = {"audience_name": username, "DANMU_MSG": chat_message}
        try:
            requests.post(self.relay_url, json=payload, timeout=3)
        except requests.RequestException:
            pass

    def listen_forever(self) -> None:
        while True:
            try:
                sock = self._connect()
                buffer = ""
                while True:
                    data = sock.recv(2048).decode("utf-8", errors="ignore")
                    if not data:
                        raise ConnectionError("Disconnected from Twitch IRC.")
                    buffer += data
                    while "\r\n" in buffer:
                        line, buffer = buffer.split("\r\n", 1)
                        if line.startswith("PING"):
                            self._send_pong(line)
                            continue
                        self._handle_privmsg(line)
            except (OSError, ConnectionError):
                time.sleep(self.reconnect_delay_s)
