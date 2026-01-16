import asyncio
import datetime
import json
import os
import queue
import shutil
import subprocess
import threading
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from flask_apscheduler import APScheduler
import requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import utils

# Configuration initialization


project_root = os.path.dirname(os.path.abspath(__file__))


file_lock = threading.Lock()
QuestionList = queue.Queue(10)
QuestionName = queue.Queue(10)
AnswerList = queue.Queue()
tts_playList = queue.Queue()
song_lst = queue.Queue()
song_playList = queue.Queue()
song_search_playList = queue.Queue()
EmoteList = queue.Queue()
LogsList = queue.Queue()
web_captions_printer = queue.Queue()
find_wav_lst = []
history = []

if_check_blivedm_api_get = False

hps = utils.get_hparams_from_file('configs/json/config.json')
role_language_model = hps.ai_vtuber.language_model
role_speech_model = hps.ai_vtuber.speech_model
if_easy_ai_vtuber = hps.ai_vtuber.if_easy_ai_vtuber
if_agent = hps.ai_vtuber.if_agent
is_ai_ready = hps.bilibili.is_ai_ready
is_tts_ready = hps.bilibili.is_tts_ready
is_tts_play_ready = hps.bilibili.is_tts_play_ready
is_song_play_ready = hps.bilibili.is_song_play_ready
is_song_cover_ready = hps.bilibili.is_song_cover_ready
is_obs_ready = hps.bilibili.is_obs_ready
is_obs_play_ready = hps.bilibili.is_obs_play_ready
is_web_captions_printer_ready = hps.bilibili.is_web_captions_printer_ready
web_captions_printer_port = hps.api_path.web_captions_printer.port
easy_ai_vtuber_url = hps.api_path.easy_ai_vtuber.url
AudioCount = 0
AudioPlay = 0

sched1 = AsyncIOScheduler(timezone="Asia/Shanghai")
app = Flask(__name__)
CORS(app)

# Directory initialization
if os.path.exists(os.path.join(project_root, "song_output")):
    shutil.rmtree(os.path.join(project_root, "song_output"))
if os.path.exists(os.path.join(project_root, "logs/danmu")):
    shutil.rmtree(os.path.join(project_root, "logs/danmu"))
output_dir = "template/logs/danmu"
os.makedirs(os.path.join(project_root, "template/logs/danmu"), exist_ok=True)

@app.route('/AI_VTuber/DANMU_MSG',methods=['POST'])
def information_show():
    DANMU_response = request.json
    user_name = DANMU_response["audience_name"]
    content = DANMU_response["DANMU_MSG"]
    QuestionName.put(user_name)  # Store username in queue
    QuestionList.put(content)  # Store chat message in queue
    time1 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    LogsList.put(f"[{time1}] [{user_name}]: {content}")
    print(f"\033[35m[{time1}] [{user_name}]: {content}\033[0m")
    print("\033[32mSystem>>\033[0mAdded the chat message to the question queue.")
    return {"statue_code":200}

def Classifiers(content):
    """
    Classifier: routes chat content to different features.
    #chat: returns -1 for a chat task.
    #draw: returns 1 for SD prompt execution.
    #song: returns 1 for requests, supports #song0 + title or #song1 + BV id.
    #cover: returns 1 for cover list and #cover + number to sing.
    #sing: returns 1, use with #command and tags from the song library csv.
    #command: returns 1, select songs by index or ranges like #id 0,1,3,4,7-16.
    #repeat: returns 1 and repeats content for TTS testing.
    #playlist: returns 1 and prints upcoming songs (requests and sing features).
    Other messages return 0 and are filtered out.
    :param content:
    :return:
    """
    global songlist,song_lst
    if content.startswith("#chat"):
        return -1

    elif content.startswith("#repeat"):
        AnswerList.put(content[7:])
        return 1

    elif content.startswith("#playlist"):
        current_songs = list(song_lst.queue)
        print("Playlist:", current_songs)
        with file_lock:
            with open('configs/config.json', encoding="utf-8", mode='r') as config_file:
                config_data = json.load(config_file)
            config_data["songlist"] = current_songs
        current_songs_str = ",".join(current_songs)
        web_captions_printer.put("Playlist:" + current_songs_str)
        with file_lock:
            with open('configs/config.json', 'w', encoding='utf-8') as config_file:
                json.dump(config_data, config_file, indent=4, ensure_ascii=False)
        return 1

# LLM thread
async def check_answer():
    """
    Create a generation thread when the model is idle and questions are queued.
    :return:
    """
    global is_ai_ready
    if not QuestionList.empty() and is_ai_ready:
        is_ai_ready = 0
        answers_thread = threading.Thread(target=lambda: ai_response())
        answers_thread.start()

def ai_response():
    """
    Extract emotion keywords, compute updated emotion state, and queue the response for TTS.
    :return:
    """
    global is_ai_ready,emotion_state,emotion_score
    user_input = QuestionList.get()
    user_name = QuestionName.get()
    ques = LogsList.get()
    data_agent_to_do = {"content": user_input, "memory": True}
    res = requests.post(f'http://localhost:9550/agent_to_do', json=data_agent_to_do).json()
    bot_response = res.get("content")
    answer = f"Reply to {user_name}: {bot_response}"
    AnswerList.put(f"{user_input}" + "," + answer)
    current_question_count = QuestionList.qsize()
    print(f"\033[31m[AI-Vtuber]\033[0m{answer}")
    print(
        f"\033[32mSystem>>\033[0mQueued response for {user_name}. Remaining: {current_question_count}"
    )
    time1 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with file_lock:
        with open("template/logs/logs.txt", "a", encoding="utf-8") as f:
            f.write(
                f"{ques}\n[{time1}] {answer}\n========================================================\n"
            )
    is_ai_ready = 1

# TTS thread
async def check_tts():
    """
    Create a TTS thread when playback is idle and responses are queued.
    :return:
    """
    global is_tts_ready,AudioCount
    if not AnswerList.empty() and is_tts_ready:
        text = AnswerList.get()
        is_tts_ready = 0
        tts_thread = threading.Thread(target=lambda: tts_main(text))
        tts_thread.start()

def tts_main(text):
    '''
    Supported
    1.edge-tts+svc -> so-vits-svc
    2.gpt-sovits
    3.bert-vits2
    :param text: text to synthesize

    '''
    # Create output directory
    global AudioCount,is_tts_ready
    tts_plan = 1
    if role_speech_model == "edge-tts+svc":
        tts_plan = 1
    elif role_speech_model == "gpt-sovits":
        tts_plan = 2
    elif role_speech_model == "bert-vits2":
        tts_plan = 3
    data_tts = {"tts_plan": tts_plan, "text": text, "AudioCount": AudioCount}
    tts_path = requests.post('http://localhost:9550/tts', json=data_tts).json()["path"]
    tts_playList.put(tts_path)
    is_tts_ready = 1
    web_captions_printer.put(text)
    AudioCount += 1

async def check_tts_play():
    """
    Create a TTS playback thread when the playlist has items.
    :return:
    """
    global is_tts_play_ready,is_song_play_ready,if_easy_ai_vtuber
    if not tts_playList.empty() and is_tts_play_ready and is_song_play_ready:
        is_tts_play_ready = 0
        wav_path = tts_playList.get()
        if not if_easy_ai_vtuber:
            tts_thread = threading.Thread(target=lambda: mpv_play(wav_path) , daemon=True)
            tts_thread.start()
        else:
            easy_ai_vtuber_thread = threading.Thread(
                target=lambda: to_easy_ai_vtuber_api(
                    "speak",wav_path), daemon=False)
            easy_ai_vtuber_thread.start()


def mpv_play(path):
    """
    Play TTS audio.
    :param path: audio path
    :return:
    """
    duration = utils.get_duration_ffmpeg(path)
    global is_tts_play_ready
    # end: playback seconds; volume range 0-100
    subprocess.run(
        f'mpv.exe -vo null --volume=100 --start=0 --end={duration} "{path}" 1>nul',
        shell=False,
    )
    is_tts_play_ready = 1
    return

def to_easy_ai_vtuber_api(type,path):
    global is_tts_play_ready,is_song_play_ready,is_song_cover_ready
    data = {}
    if type == "speak":
        data = {
            "type": type,  # speech motion
            "speech_path": path,  # speech audio path
        }
    elif type == "rhythm":
        data = {
            "type": type,  # rhythm motion
            "music_path": path,  # song audio path
        }
    elif type == "sing":
        data = {
            "type": "sing",
            "music_path": path,  # original track path
            "voice_path": path,  # vocal track path
            "mouth_offset": 0.0,
        }
    response = requests.post(easy_ai_vtuber_url, json=data)
    if response.status_code == 200:
        print("\033[31mSuccessfully requested easy_ai_vtuber_api\033[0m")
    is_tts_play_ready = 1
    is_song_play_ready = 1
    is_song_cover_ready = 1

def app_server():
    app.run(host="0.0.0.0", port=9551)

async def main():
    app_thread = threading.Thread(target=app_server)
    app_thread.start()
    # Add scheduled tasks
    sched1.add_job(check_answer, "interval", seconds=1, id="llm_answer", max_instances=1)
    sched1.add_job(check_tts, "interval", seconds=1, id="tts", max_instances=4)
    sched1.add_job(check_tts_play, "interval", seconds=1, id="tts_play", max_instances=1)

    # Start scheduler
    sched1.start()
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        # Stop scheduler
        sched1.shutdown()


if __name__ == '__main__':
    asyncio.run(main())
