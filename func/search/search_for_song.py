# -*- coding: utf-8 -*-
import io
import os
import re
import sys

from lxml import etree
import requests
import json
from concurrent.futures import ThreadPoolExecutor

#sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')

# Create thread pool
from pydub import AudioSegment

pool = ThreadPoolExecutor(max_workers=10)
# Request headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
}
def download(id, name):
    output_dir = "download"
    os.makedirs(output_dir, exist_ok=True)
    # Build download URL
    url = f'http://music.163.com/song/media/outer/url?id={id}'
    # Send download request
    response = requests.get(url=url, headers=headers).content
    # Write response content to file
    with open('download/' + name + '.wav', 'wb') as f:
        f.write(response)
    # Log download completion
    print(name, "downloaded.")


def get_id(url):
    # Fetch page content
    response = requests.get(url=url, headers=headers).text
    # Parse with XPath
    page_html = etree.HTML(response)
    # Extract song list
    id_list = page_html.xpath('//textarea[@id="song-list-pre-data"]/text()')[0]
    # Parse and enqueue downloads
    for i in json.loads(id_list):
        name = i['name']
        id = i['id']
        author = i['artists'][0]['name']
        pool.submit(download, id, name + '-' + author)
    # Close thread pool
    pool.shutdown()


def replace_special_characters(filename):
    # Special character replacements
    special_chars = {
        '/': '_',
        '\\': '_',
        ':': '-',
        '?': '',
        '？':'',
        '*': '',
        '"': '',
        ' ': '_',
        '<': '',
        '>': '',
        '|': '',
        '.': '',
        ',': '',
        '[': '',
        ']': '',
        '{': '',
        '}': '',
        '+': '',
        '=': '',
        '&': '',
        '%': '',
        '#': '',
        '@': '',
        '!': '',
        '^': '',
        '(': '',
        ')': '',
        '-':'_'
        # Add other special characters as needed...
    }

    # Replace using regex
    for char, replacement in special_chars.items():
        filename = re.sub(re.escape(char), replacement, filename)

    return filename

def search_in_wy(keyword):
    # Create thread pool
    pool = ThreadPoolExecutor(max_workers=10)
    # Request headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3741.400 QQBrowser/10.5.3863.400"
    }
    # Build search URL
    search_url = f'https://music.163.com/api/search/get/web?csrf_token=hlpretag=&hlposttag=&s={keyword}&type=1&offset=0&total=true&limit=5'
    # Send search request and fetch response
    response = requests.get(url=search_url, headers=headers).json()
    print(response)
    # Extract song list
    song_list = response['result']['songs']
    print(song_list)
    # Enqueue each song for download
    for song in song_list:
        name = song['name']
        name = replace_special_characters(name)
        id = song['id']
        author = song['artists'][0]['name']
        author = replace_special_characters(author)
        if os.path.exists("download/"+name + '-' + author+".wav"):
            file_size = os.path.getsize("download/"+name + '-' + author+".wav")
            file_size_kb = file_size / 1024
            if file_size_kb < 500:
                print(name + "-" + author + ".wav is VIP-only. Skipping...")
                continue
            else:
                print("The song is already downloaded.")
                pool.shutdown()
                return name + '-' + author

        pool.submit(download, id, name + '-' + author)
        # Close thread pool
        pool.shutdown()
        return name + '-' + author
    # Close thread pool
    pool.shutdown()
    return None

def search_bilibili(bv):
    headers = {
        "Cookie":"buvid3=941E52D9-89A7-0431-5AB8-BDE4F9BD6A7689091infoc; b_nut=1681183089; i-wanna-go-back=-1; _uuid=529106944-9F34-C598-742C-616939BDDCB560391infoc; DedeUserID=287906485; DedeUserID__ckMd5=30dae07d6a8b1db5; b_ut=5; buvid4=69DC937C-16C8-9A29-E1DF-2387ED39770D90173-023041111-eyNZ9J%2BmeuO%2BHQK9QZtt3A%3D%3D; nostalgia_conf=-1; CURRENT_PID=0fddbca0-d81b-11ed-8c9e-fd0639642c74; rpdid=|(YuJm~u~)~0J'uY)uu)RYkY; buvid_fp_plain=undefined; hit-new-style-dyn=1; hit-dyn-v2=1; LIVE_BUVID=AUTO9216819022212944; FEED_LIVE_VERSION=V_SIDE_CARD_REFRESH; enable_web_push=DISABLE; header_theme_version=CLOSE; fingerprint=4c9564a334a08bd54a93a9c35a0ed065; CURRENT_FNVAL=16; is-2022-channel=1; CURRENT_QUALITY=80; SESSDATA=1967a629%2C1721613383%2Ca9495%2A12CjAQcW9SQS2Vxhdfp6PaTQzsSq-xwHiIj-h_Kz-v2Z5uJlIoTQqW6QXfR32RIjTRHCQSVkxIblp2XzE5dkdxT240aDZVdmw0a3NzdHk2dUg0NEJOeHQ5cUxjQUt6WV9rM3BhSVRiU2owRmxianRHeHpISGJfZTJuYWNsRXVKZFVRWURqaU40QVBBIIEC; bili_jct=51de9c5af22d513902098779c98391bc; sid=5jyj5863; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDYzNDc1ODEsImlhdCI6MTcwNjA4ODMyMSwicGx0IjotMX0.7IA9sFsIrOPwf7unZkUW4-xhybz6WoMJFTJy0I3roNY; bili_ticket_expires=1706347521; b_lsid=F72AA451_18D3AD83029; bp_article_offset_287906485=890135661478150217; buvid_fp=4c9564a334a08bd54a93a9c35a0ed065; bp_video_offset_287906485=890140081030955015; home_feed_column=4; browser_resolution=184-838; PVID=10",
        "Referer":"https://www.bilibili.com/",
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
    }

    url_path = "https://www.bilibili.com/video/"+bv
    response = requests.get(url=url_path,headers=headers)
    if response.status_code == 200:
        html = response.text
        title = re.findall('<h1 title="(.*?)" class="video-title"',html)[0]
        title = replace_special_characters(title)
        video_info = re.findall('<script>window.__playinfo__(.*?)</script>',html)[0][1:]
        json_data = json.loads(video_info)
        audio_url = json_data["data"]["dash"]["audio"][0]["baseUrl"]
        audio_content = requests.get(url=audio_url,headers=headers).content
        with open("download/"+title+".wav",mode="wb")as audio:
            audio.write(audio_content)
        print(bv, "downloaded.")
        return title
    else:
        print("Invalid BV ID. Please try again.")
        return None


def search_bilibili_mp4(bv):
    headers = {
        "Cookie": "your_cookie_here",
        "Referer": "https://www.bilibili.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
    }

    url_path = "https://www.bilibili.com/video/" + bv
    response = requests.get(url=url_path, headers=headers)
    if response.status_code == 200:
        html = response.text
        title = re.findall('<h1 title="(.*?)" class="video-title"', html)[0]
        title = replace_special_characters(title)
        video_info = re.findall('<script>window.__playinfo__(.*?)</script>', html)[0][1:]
        json_data = json.loads(video_info)
        video_url = json_data["data"]["dash"]["video"][0]["baseUrl"]
        audio_url = json_data["data"]["dash"]["audio"][0]["baseUrl"]
        # Create folder for downloaded videos
        os.makedirs("download", exist_ok=True)
        # Download video
        video_content = requests.get(url=video_url, headers=headers).content
        with open(f"download/{title}.mp4", mode="wb") as video_file:
            video_file.write(video_content)

        # Download audio
        audio_content = requests.get(url=audio_url, headers=headers).content
        with open(f"download/{title}.wav", mode="wb") as audio:
            audio.write(audio_content)
        print(f"Video {title} downloaded.")
        print(f"Audio {title} downloaded.")
        merge_video_audio(f"download/{title}.mp4",f"download/{title}.wav","download/merged_video.mp4")
        return title
    else:
        print("Invalid BV ID. Please try again.")
        return None


def merge_video_audio(video_file, audio_file, output_file):
    # Build ffmpeg command
    command = f'ffmpeg -i {video_file} -i {audio_file} -c:v copy -c:a aac -strict experimental -loglevel error -y {output_file}'

    # Execute command
    os.system(command)

    # Remove source files
    os.remove(video_file)
    os.remove(audio_file)


def search_youtube_title(video_id: str):
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        response = requests.get(
            "https://www.youtube.com/oembed",
            params={"url": video_url, "format": "json"},
            timeout=10,
        )
        response.raise_for_status()
        return response.json().get("title")
    except requests.RequestException:
        return None

if __name__ == '__main__':

    search_bilibili_mp4("BV1Hw411z7Dy")
    # search_in_wy("Example song")
    #search_bilibili("BV1ru4y1M7fj")
