import time
import glob
import pandas as pd
import requests
import streamlit as st
from func.agent import tools
import matplotlib.pyplot as plt
from streamlit_webrtc import webrtc_streamer
import subprocess
import utils
import json
import os
from tqdm import tqdm

project_root = os.path.dirname(os.path.abspath(__file__))[:-2]

def get_properties():
    # File path
    file_path = "template/json/template.json"
    # Check whether the file exists
    if not os.path.exists(file_path):
        return {}
    with open(file_path, 'r', encoding='utf-8') as file:
        node_properties = json.load(file)
    return node_properties


def save_properties_to_file(properties):
    file_path = "template/json/template.json"
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump({}, file)
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(properties, file)

def create_form(data,key_path = []):
    for key, value in data.items():
        current_key_path = key_path + [key]
        if isinstance(value, str):
            if key == "default_model":
                from func.chat.chat_api import model_list
                data[key] = st.selectbox(key, model_list, index=0)
                continue
            user_input = st.text_input(
                ".".join(current_key_path),
                value=value,
                placeholder=value if value else "Enter a string...",
            )
            if user_input:
                data[key] = user_input
        elif isinstance(value, int):
            user_input = st.number_input(
                ".".join(current_key_path),
                value=value,
                placeholder=value if value else "Enter an integer...",
                step=1,
                format="%d",
            )
            if user_input is not None:
                data[key] = user_input
        elif isinstance(value, float):
            user_input = st.number_input(
                ".".join(current_key_path),
                value=value,
                placeholder=value if value else "Enter a decimal...",
            )
            if user_input is not None:
                data[key] = user_input
        elif isinstance(value, bool):
            data[key] = st.checkbox('.'.join(current_key_path), value)
        elif isinstance(value, list):
            # placeholder = "One item per line..." if not value else '\n'.join(map(str, value))
            # list_items = st.text_area('.'.join(current_key_path), value=value,placeholder=placeholder)
            # if list_items:
            #     data[key] = json.loads(list_items.split('\n'))
            pass
        elif isinstance(value, dict):
            # For dicts, create nested forms recursively
            create_form(value, current_key_path)
        else:
            st.write(f"Unsupported data type: {type(value)}")


def env_configuration(default_file_path="configs/json/config.json"):
    """
    Manage and install the runtime environment.
    Returns:

    """
    t1, t2 = st.tabs(["Virtual Environment", "VTuber Configuration"])
    with t1:
        e_select = st.selectbox(
            "Create or update environment:",
            ["Create a new environment", "Use an existing environment"],
            index=1,
        )
        if e_select == "Use an existing environment":
            folder_path = os.path.join(project_root, "requirements")
            file_names = os.listdir(folder_path)
            file_name_list = [file_name for file_name in file_names]
            selected_requirement = st.selectbox("Select requirements file:", file_name_list, index=0)
            mirror_source_list = [
                "https://pypi.tuna.tsinghua.edu.cn/simple/",
                "http://mirrors.aliyun.com/pypi/simple/",
                "https://pypi.mirrors.ustc.edu.cn/simple/",
                "http://pypi.hustunique.com/simple/",
                "https://mirror.sjtu.edu.cn/pypi/web/simple/",
                "http://pypi.douban.com/simple/"
            ]
            mirror_source = st.selectbox("Select PyPI mirror:", mirror_source_list, index=0)
            folder_contents = os.listdir("runtime\miniconda3\envs")
            envs_name = [f for f in folder_contents if os.path.isdir(os.path.join("runtime\miniconda3\envs", f))]
            env_name = st.selectbox("Select environment:", envs_name, index=0)
            if st.button("Install dependencies"):
                command = f"{project_root}\\runtime\\miniconda3\\envs\\{env_name}\\python.exe -m pip install -r {project_root}\\requirements\\{selected_requirement} -i {mirror_source}"
                subprocess.Popen(['start', 'cmd', '/k', command], shell=True)
                st.write(command)
            c = st.text_input("Install a specific package:", placeholder="pip install ...")
            if st.button("Install dependency", key=1):
                command = f"{project_root}\\runtime\\miniconda3\\envs\\{env_name}\\python.exe -m {c} -i {mirror_source}"
                subprocess.Popen(['start', 'cmd', '/k', command], shell=True)
                st.write(command)
        elif e_select == "Create a new environment":
            new_env_name = st.text_input("Environment name:")
            new_python_version = st.text_input("Python version:", placeholder="3.10")
            if st.button("Create environment"):
                command = f"{project_root}\\runtime\\miniconda3\\Scripts\\conda.exe create --name {new_env_name} python={new_python_version} -y"
                subprocess.Popen(['start', 'cmd', '/k', command], shell=True)
    with t2:
        s = st.selectbox("Select an action", ["Create config", "Edit config"], index=1)
        if s == "Create config":
            default_file_path="configs/json/config.example.json"
        try:
            data = utils.load_json(default_file_path)
            st.write(project_root)
            select_key = st.selectbox("Select a group to edit", list(data.keys()), index=0)
            with st.form("Config Editor"):
                st.write(select_key)
                create_form(data[select_key])
                if st.form_submit_button("Save"):
                    utils.write_json(data,"configs/json/config.json")
                    st.success("Saved successfully")
        except FileNotFoundError:
            st.error(f"Default file '{default_file_path}' not found.")
        except Exception as e:
            st.error(f"Error reading default file: {e}")



def main_page(hps,role_hps):
    st.set_page_config(
        page_title='AI-Vtuber',
        layout="wide",
        page_icon='assets/icon/ComfyUI_00011_.png',
        initial_sidebar_state="expanded",
        menu_items={
            'Get help': "http://www.worldline-fantasy.top",
            'Report a bug': "https://github.com/whoiswennie/AI-Vtuber/issues",
            'About': "http://www.worldline-fantasy.top"
        }
    )
    with st.sidebar:
        gif_files = [
            "assets/icon/huan1.gif",
            "assets/icon/huan2.gif",
            "assets/icon/huan3.gif",
            "assets/icon/huan4.gif",
            "assets/icon/huan5.gif",
            "assets/icon/huan6.gif",
        ]
        if 'gif_index' not in st.session_state:
            st.session_state.gif_index = -1
        st.session_state.gif_index += 1
        current_index = int(st.session_state.get("gif_index", 0) % len(gif_files))
        current_gif = gif_files[current_index]
        st.sidebar.image(current_gif, caption="Project mascot: Huan", use_column_width=True)
        st.title('AI-VTuber')
        st.markdown("Project author: Tianhuan")
        st.markdown("[Official site](http://www.worldline-fantasy.top)")
        st.markdown("[GitHub repository](https://github.com/whoiswennie/AI-Vtuber)")
        st.markdown("[YouTube](https://www.youtube.com)")
        st.markdown("[Twitch](https://www.twitch.tv)")
        st.markdown('---')
        page = st.sidebar.radio("Navigation", ["Environment", "AI-VTuber", "Personalization"])
    if page == "Environment":
        env_configuration()
    elif page == "AI-VTuber":
        with st.expander("Quick-start script manager"):
            bats_path = None
            bat_select = st.selectbox("Select quick-start script:", ["Select services", "Configure scripts"], index=0)
            if bat_select == "Configure scripts":
                bat_select_2 = st.selectbox("Add/update or delete scripts:", ["Add or update", "Delete"], index=0)
                with open("configs/json/bat_start.json", 'r', encoding='utf-8') as file:
                    data = json.load(file)
                if bat_select_2 == "Add or update":
                    bat_names = [item['bat_name'] for item in data if "bat_name" in item]
                    bat_name_select = st.selectbox("Select a script:", bat_names, index=0)
                    if bat_name_select:
                        st.write([item["bat_path"] for item in data if item["bat_name"] == bat_name_select][0])
                    bat_name = st.text_input("Script display name:")
                    bat_path = st.text_input("Absolute path to bat script:", placeholder="e.g. D:/so-vits-svc/api.bat")
                    bat_dict = {"bat_name":bat_name,"bat_path":bat_path}
                    if st.button("Save"):
                        if bat_name in bat_names:
                            for item in data:
                                if item["bat_name"] == bat_name and bat_path != None:item["bat_path"] = bat_path
                            with open("configs/json/bat_start.json", 'w', encoding='utf-8') as file:
                                json.dump(data,file, ensure_ascii=False, indent=4)
                        else:
                            data.append(bat_dict)
                            with open("configs/json/bat_start.json", 'w', encoding='utf-8') as file:
                                json.dump(data,file, ensure_ascii=False, indent=4)
                        st.success("Saved successfully")
                elif bat_select_2 == "Delete":
                    d_bat_name = st.multiselect(
                        "Select scripts to delete:",
                        [item for item in data ]
                    )
                    if st.button("Delete"):
                        data = [item for item in data + d_bat_name if item not in data or item not in d_bat_name]
                        with open("configs/json/bat_start.json", 'w', encoding='utf-8') as file:
                            json.dump(data, file, ensure_ascii=False, indent=4)
                        st.success("Deleted successfully")
            elif bat_select == "Select services":
                with open("configs/json/bat_start.json", 'r', encoding='utf-8') as file:
                    data = json.load(file)
                bat_names = [item['bat_name'] for item in data if "bat_name" in item]
                bats_start = st.multiselect(
                    "Select services to start:",
                    bat_names
                )
                bats_path = [item["bat_path"] for item in data if item["bat_name"] in bats_start]
            st.markdown("---")
            col0, col1, col2, col3, col4 = st.columns(5)
            with col0:
                if st.button("Launch bat scripts"):
                    if bats_path is not None:
                        for p in bats_path:
                            print(p)
                            try:
                                command = f'cd /d "{os.path.dirname(p)}" && start "" "{p}"'
                                print(command)
                                subprocess.Popen(command, shell=True)
                                st.success(f"Started script: {p}")
                            except FileNotFoundError:
                                st.error(f"Script not found: {p}")
                            except subprocess.CalledProcessError as e:
                                st.error(f"Script error: {p}, exit code: {e.returncode}")
                            except Exception as e:
                                st.error(f"Unknown error starting script: {p}, error: {str(e)}")
                    else:
                        st.warning("No bat script paths available.")
            with col1:
                platform = st.selectbox(
                    "Streaming platform",
                    ["Twitch", "YouTube", "BiliBili (legacy)"],
                    index=0,
                )
                if platform == "Twitch":
                    twitch_username = st.text_input("Twitch username")
                    twitch_oauth = st.text_input("Twitch OAuth token (oauth:...)")
                    twitch_channel = st.text_input("Channel name")
                elif platform == "YouTube":
                    youtube_api_key = st.text_input("YouTube API key")
                    youtube_video_id = st.text_input("YouTube live video ID")
                else:
                    ACCESS_KEY_ID = hps.bilibili.blivedm.ACCESS_KEY_ID
                    ACCESS_KEY_SECRET = hps.bilibili.blivedm.ACCESS_KEY_SECRET
                    APP_ID = hps.bilibili.blivedm.APP_ID
                    ROOM_OWNER_AUTH_CODE = hps.bilibili.blivedm.ROOM_OWNER_AUTH_CODE
                if st.button("Start stream listeners"):
                    command_2 = f'{project_root}\\runtime\\miniconda3\\envs\\ai-vtuber\\python.exe bilibili_main.py'
                    if platform == "Twitch":
                        command_1 = (
                            f'{project_root}\\runtime\\miniconda3\\envs\\ai-vtuber\\python.exe '
                            f'twitch_main.py --username "{twitch_username}" --oauth-token "{twitch_oauth}" '
                            f'--channel "{twitch_channel}"'
                        )
                    elif platform == "YouTube":
                        command_1 = (
                            f'{project_root}\\runtime\\miniconda3\\envs\\ai-vtuber\\python.exe '
                            f'youtube_main.py --api-key "{youtube_api_key}" --video-id "{youtube_video_id}"'
                        )
                    else:
                        command_1 = (
                            f'{project_root}\\runtime\\miniconda3\\envs\\ai-vtuber\\python.exe blivedm_api.py '
                            f'-AKI {ACCESS_KEY_ID} -AKS {ACCESS_KEY_SECRET} -AI {APP_ID} '
                            f'-ROAC {ROOM_OWNER_AUTH_CODE}'
                        )
                    subprocess.Popen(['start', 'cmd', '/k', command_1], shell=True)
                    subprocess.Popen(['start', 'cmd', '/k', command_2], shell=True)
                    st.success("Stream listeners started.")
            with col2:
                if st.button("Stop mpv player"):
                    import psutil
                    import signal
                    # Find processes containing "mpv"
                    for proc in psutil.process_iter(['pid', 'name']):
                        if 'mpv' in proc.name():
                            mpv_pid = proc.pid
                            # Terminate the mpv process
                            proc.send_signal(signal.SIGTERM)
            with col3:
                if st.button("Start Flask backend"):
                    st.success("Flask backend started successfully.")
                    command = f'{project_root}\\runtime\\miniconda3\\envs\\ai-vtuber\\python.exe flask_ai_vtuber_api.py'
                    subprocess.Popen(['start', 'cmd', '/k', command], shell=True)
            with col4:
                if st.button("Check service ports"):
                    import socket
                    urls = [
                        {"Flask backend": "http://0.0.0.0:9550"},
                        {"so_vits_svc_api": hps.api_path.so_vits_svc.url},
                        {"bert_vits2_api": hps.api_path.bert_vits2.url},
                        {"gpt_sovits_api": hps.api_path.gpt_sovits.url},
                        {"easy_ai_vtuber_api": hps.api_path.easy_ai_vtuber.url},
                        {"neo4j_api": hps.api_path.neo4j.url}
                    ]

                    def is_port_in_use(host, port):
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            try:
                                s.bind((host, port))
                            except OSError:
                                return True
                            else:
                                return False

                    for url in urls:
                        api_name = next(iter(url.keys()), None)
                        api_url = next(iter(url.values()), None)
                        host, port = utils.extract_port_and_url(api_url)
                        if is_port_in_use(host, port):
                            st.success(f"{api_name} port {port} is running.")
                        else:
                            st.error(f"{api_name} port {port} is not running.")

        with st.expander("Stream tools"):
            empty_directory_list = ["downloads", "json", "stt", "tts", "img", "txt", "logs", "uploads", "uvr5_opt"]
            select_directory_list = st.multiselect("Select temp folders to clear", empty_directory_list)
            live_col1, live_col2, live_col3, live_col4 = st.columns(4)
            if live_col1.button("Clear temp folders"):
                formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                try:
                    st.success(f"Cleared: {select_directory_list}")
                    print(f"[{formatted_time}]INFO clearing temp folders {select_directory_list}...")
                    for i in select_directory_list:
                        utils.empty_directory(f"template/{i}")
                except FileNotFoundError as e:
                    pass

            if live_col2.button("Fetch playlist"):
                songlist = requests.post('http://localhost:9550/get_songlist')
                st.write(songlist.json())

            if live_col3.button("Clear audio playlist"):
                requests.post('http://localhost:9550/clear_songlist')
                st.success("Audio playlist cleared.")

            if live_col4.button("View runtime status"):
                show_data = requests.post('http://localhost:9550/show')
                st.write(show_data.json())

        with st.expander("Test AI-VTuber"):
            selected_options = st.multiselect(
                "Select modules to enable:",
                ["Voice", "Avatar Driver"]
            )
            s_m_1 = False
            s_m_2 = False
            easyaivtuber_img = None
            role_tts_emotion = None
            tts_plan = [0,1]
            action_type = "speak"
            st.write("Modules enabled:")
            for select_module in selected_options:
                st.success(select_module)
                if "Voice" == select_module:
                    s_m_1 = True
                    tts_plan = st.selectbox("Select TTS plan:", ["1.edge-tts+svc", "2.GPT-SoVITS"], index=1)
                elif "Avatar Driver" == select_module:
                    s_m_2 = True
            if s_m_2:
                action_type = st.radio("Choose an action:", ["speak", "rhythm", "sing"])
                st.write("Selected action:", action_type)
                webrtc_streamer(
                    key="video_streamer",
                    media_stream_constraints={
                        "video": {
                            "width": 1920,  # Video width
                            "height": 1080,  # Video height
                            "frameRate": 60,  # Frame rate
                            "aspectRatio": 1.777777778,  # Aspect ratio (16:9)
                            "deviceId": None  # Auto-select camera
                        },
                        "audio": False
                    }
                )
            role_keys_hps = utils.get_hparams_from_file("configs/json/role_setting.json").keys()
            role = st.selectbox("Select a chat persona template:", list(role_keys_hps), index=0)
            if s_m_1:
                if tts_plan == "2":
                    role_name = utils.load_json("configs/json/role_setting.json").get(role)["tts"]["plan_2"]["gpt_sovits"]
                    emotion_lst = requests.get(hps.api_path.gpt_sovits.url+"/character_list").json().get(role_name)
                    if emotion_lst:
                        role_tts_emotion = st.selectbox("Select speaking emotion", emotion_lst)
            if s_m_2:
                easyaivtuber_img_dir_path = role_hps.get(role).easyaivtuber_dir_path
                if easyaivtuber_img_dir_path:
                    png_files = [f for f in os.listdir(easyaivtuber_img_dir_path) if f.endswith('.png')]
                    easyaivtuber_img = st.selectbox("Select avatar image", png_files, index=0)
            knowledge_database = hps.ai_vtuber.knowledge_database
            select_databases = st.multiselect("Select reference knowledge bases", knowledge_database)
            if st.button("Apply this persona template"):
                data_role = {"role_key":role,"tts_plan":int(tts_plan[0]),"role_tts_emotion":role_tts_emotion,"easyaivtuber_img":easyaivtuber_img,"knowledge_databases":[database_dict["name"] for database_dict in select_databases]}
                res = requests.post('http://localhost:9550/switch_role', json=data_role)
                if res.status_code == 200:
                    st.success("Persona template switched.")
            st.write("---")
            st.write("Conversation")
            if_memory = st.checkbox("Enable AI-VTuber memory")
            if not if_memory:if_memory = False
            user_input = st.text_input("Enter your message:", "")
            if 'memory_list' not in st.session_state:
                st.session_state.memory_list = [{"query":"","answer":""}]
            if st.button("Send"):
                with st.spinner("Running task..."):
                    status_placeholder = st.empty()
                    data_agent_to_do = {"content": user_input,"memory":if_memory}
                    res = requests.post(f'http://localhost:9550/agent_to_do', json=data_agent_to_do).json()
                    st.write("Reference info:", res["refer_information"])
                    st.session_state.memory_list.append({"query":user_input,"answer":res["content"]})
                    stream_bar = st.progress(0)
                    placeholder = st.empty()
                    # Simulate streaming output
                    status_placeholder.text("Streaming output...")
                    for i in range(len(res["content"])):
                        # Update the placeholder text
                        placeholder.text_area("AI-Vtuber:", value=res["content"][:i + 1], key=i)
                        stream_bar.progress((i+1)/len(res["content"]))
                        time.sleep(0.01)
                    if res["songlist"]:
                        st.write("Current playlist:", res["songlist"])
                    if s_m_1:
                        data_tts = {"tts_plan": int(tts_plan[0]), "text": res["content"], "AudioCount": 1}
                        response = requests.post('http://localhost:9550/tts', json=data_tts).json()
                        status_placeholder.text("TTS request sent.")
                        data_tts_play = {"wav_path": response["path"]}
                        if s_m_2:
                            data_action = {"type": action_type, "speech_path": data_tts_play["wav_path"]}
                            response = requests.post("http://127.0.0.1:7888/alive", json=data_action)
                            status_placeholder.text("Avatar motion request sent.")
                            if response.status_code == 200:
                                st.success("INFO: easy_ai_vtuber_api request succeeded.")
                        else:
                            requests.post('http://localhost:9550/mpv_play', json=data_tts_play)
            memory_list_choose = st.sidebar.selectbox("Select chat history:", st.session_state.memory_list, index=0)
            if memory_list_choose:
                st.write("---")
                st.write("Previous reply")
                placeholder_user = st.empty()
                placeholder_vtuber = st.empty()
                for i in range(len(memory_list_choose["query"])):
                    placeholder_user.text_area("user:", value=memory_list_choose["query"][:i + 1], key=f"user_{i}")
                    time.sleep(0.001)
                for j in range(len(memory_list_choose["answer"])):
                    placeholder_vtuber.text_area("AI-Vtuber:", value=memory_list_choose["answer"][:j + 1], key=f"AI-Vtuber_{j}")
                    time.sleep(0.001)
        with st.expander("Utilities"):
            t1, t2, t3, t4, t5, t6, t7 = st.tabs(
                [
                    "Downloader",
                    "Speech-to-Text",
                    "Vocal Separation",
                    "Text-to-Speech",
                    "Voice Conversion",
                    "AI Art",
                    "Background Removal",
                ]
            )
            with t1:
                st.caption("Download audio/video files from a provided link.")
                st.write("---")
                if "download_files" not in st.session_state:
                    st.session_state.download_files = None
                c1,c2,c3 =st.columns(3)
                d_url,d_index,d_format,download_list = None,1,"wav",None
                with c1:
                    d_url = st.text_input(
                        "Enter a URL (required):",
                        placeholder="https://www.youtube.com/watch?v=example",
                    )
                with c2:
                    d_index = st.text_input(
                        "Segment index (optional):",
                        placeholder="For multi-part videos; defaults to first part.",
                    )
                with c3:
                    d_format = st.selectbox("File type", ["wav", "mp4"], index=0)
                if st.button("Start download"):
                    if d_url:
                        download_data = {"url":d_url,"index":d_index,"format":d_format}
                        st.write("Request payload:", download_data)
                        download_list = requests.post('http://localhost:9550/tool/download_from_url', json=download_data).json()
                        if download_list:
                            st.session_state.download_files = download_list
                if st.session_state.download_files:
                    if d_format == "wav":
                        select_audio = st.selectbox("Selected audio", st.session_state.download_files, index=0)
                        st.audio(select_audio)
                        if st.button("Delete audio"):
                            if os.path.exists(select_audio):
                                os.remove(select_audio)
                                st.session_state.download_files = None
                                st.success(f"File {select_audio} deleted.")
                            else:
                                st.warning(f"File {select_audio} not found.")
                    elif d_format == "mp4":
                        select_video = st.selectbox("Selected video", st.session_state.download_files, index=0)
                        st.video(select_video)
                        if st.button("Delete video"):
                            if os.path.exists(select_video):
                                os.remove(select_video)
                                st.session_state.download_files = None
                                st.success(f"File {select_video} deleted.")
                            else:
                                st.warning(f"File {select_video} not found.")
                if st.button("Open cache folder"):
                    subprocess.run(['explorer', os.path.abspath(os.path.join(project_root, "template/downloads"))])
            with t2:
                try:
                    audio_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "flac"])
                    if audio_file is not None:
                        st.audio(audio_file.read(), format=audio_file.type)
                        language = st.selectbox("Language", ["Auto", "zh", "en", "ja"], index=0)
                        if language == "Auto":
                            language = None
                        file_path = os.path.join("template/uploads", audio_file.name)
                        with open(file_path, "wb") as f:
                            f.write(audio_file.getbuffer())
                        if st.button("Transcribe"):
                            with st.spinner("Transcribing, please wait..."):
                                data = {"input_path": file_path,"language":language}
                                res = requests.post(f'http://localhost:9550/tool/faster_whisper', json=data)
                                st.write(res.json()["text"])
                except Exception as e:
                    st.error(e)
            with t3:
                try:
                    folder_contents = os.listdir("runtime\miniconda3\envs")
                    envs_name = [f for f in folder_contents if
                                 os.path.isdir(os.path.join("runtime\miniconda3\envs", f))]
                    uvr5_name = st.selectbox("Select environment:", envs_name, index=len(envs_name)-1)
                    device = st.selectbox("Device:", ["cuda", "cpu"])
                    is_half_precision = st.selectbox("Half precision:", [True, False])
                    port = st.number_input("Port:", value=9660)
                    if_share = st.selectbox("Share public link:", [True, False], index=1)
                    b_col1,b_col2 = st.columns(2)
                    if b_col1.button("Open UVR5 web UI"):
                        command = f"{project_root}\\runtime\\miniconda3\\envs\\{uvr5_name}\\python.exe tools/uvr5/webui.py {device} {is_half_precision} {port} {if_share}"
                        subprocess.Popen(['start', 'cmd', '/k', command], shell=True)
                    if b_col2.button("Open UVR5 output folder"):
                        subprocess.run(['explorer', os.path.abspath(os.path.join(project_root, "template/uvr5_opt"))])
                except Exception as e:
                    st.error(e)
            with t4:
                try:
                    tts_plan = st.selectbox("Select TTS plan:", ["1.edge-tts+svc", "2.GPT-SoVITS"], index=1, key="tts")
                    text = st.text_input("Text to synthesize:")
                    is_stream = False
                    if int(tts_plan[0]) == 2:
                        is_stream = st.checkbox("Enable streaming synthesis")
                    if st.button("Synthesize", key=f"tts_{1}"):
                        if not is_stream:
                            data_tts = {"tts_plan": int(tts_plan[0]), "text": text, "AudioCount": 1}
                            response = requests.post('http://localhost:9550/tts', json=data_tts).json()
                            st.audio(response["path"], format='audio/wav')
                        else:
                            import io
                            import pyaudio
                            p = pyaudio.PyAudio()
                            stream = p.open(format=p.get_format_from_width(2),
                                            channels=1,
                                            rate=32000,
                                            output=True)
                            audio_buffer = io.BytesIO()
                            hps = utils.get_hparams_from_file("configs/json/config.json")
                            url = hps.api_path.gpt_sovits.url + "/tts"
                            url += f"?text={text}&stream=true"
                            response = requests.get(url, stream=True)
                            for data in response.iter_content(chunk_size=1024):
                                stream.write(data)
                                audio_buffer.write(data)
                            audio_buffer.seek(0)  # Reset buffer pointer
                            st.audio(audio_buffer, format='audio/wav')
                            stream.stop_stream()
                            stream.close()
                            p.terminate()
                except Exception as e:
                    st.error(e)
            with t5:
                st.caption("Upload an audio clip for voice conversion.")
                audio_file = st.file_uploader("Upload audio file", type=["wav", "mp3", "ogg"])
                if audio_file is not None:
                    file_content = audio_file.read()
                    file_path = os.path.join("template/uploads", audio_file.name)
                    with open(file_path, "wb") as file:
                        file.write(file_content)
                    st.audio(f"template/uploads/{audio_file.name}")
                    if st.button("Run voice conversion"):
                        from func.tts import svc_api_request
                        svc_api_request.request_api(project_root,os.path.join(project_root,f"template/uploads/{audio_file.name}"),"vc")
                        st.success("Voice conversion succeeded.")
                    if os.path.exists(f"template/tts/vc.wav"):
                        st.audio(f"template/tts/vc.wav", format="audio/wav")
            with t6:
                from func.t2img import sd_api
                try:
                    sd_ui = st.selectbox("Select SD UI", ["webui", "comfyui"])
                    with open("configs/json/bat_start.json", 'r', encoding='utf-8') as file:
                        data = json.load(file)
                    bat_names = [item['bat_name'] for item in data if "bat_name" in item]
                    sd_env = st.selectbox("Select the SD launch script", bat_names)
                    sd_path = [item["bat_path"] for item in data if item["bat_name"] in [sd_env]]
                    directory_path = os.path.dirname(os.path.abspath(sd_path[0]))
                    st.write(directory_path)
                    sd_models_path = os.path.join(directory_path,"models/Stable-diffusion")
                    models_names = [os.path.basename(file_path) for file_path in glob.glob(os.path.join(sd_models_path, '*.safetensors'))]
                    if 'prompt' not in st.session_state:
                        st.session_state.prompt = [""]
                    d_col1,d_col2 = st.columns(2)
                    text = d_col1.text_input("Describe what to draw")
                    e_prompt = d_col2.text_input("Extra prompt", placeholder="Optional extra prompt")
                    p_col1,p_col2 = st.columns(2)
                    if p_col1.button("Auto-translate prompt"):
                        payload = json.dumps({
                            "model": "model",
                            "messages": [
                                {
                                    "role": "system",
                                    "content": (
                                        "Convert the user request into concise English prompt tokens. "
                                        "Example output: a girl,pink hair,black shoes,long hair,young,lovely. "
                                        "Output English words only, no extra text."
                                    )
                                },
                                {
                                    "role": "user",
                                    "content": text
                                }
                            ]
                        })
                        headers = {
                            'Accept': 'application/json',
                            'Authorization': '',
                            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
                            'Content-Type': 'application/json'
                        }
                        response = requests.request("POST", "http://localhost:9550/llm_chat",headers=headers,data=payload)
                        st.success(response)
                        st.session_state.prompt.append(json.loads(response.text)['choices'][0]['message']['content'] + e_prompt)
                    if e_prompt != st.session_state.prompt[-1]:
                        st.session_state.prompt.append(f",{e_prompt}")
                    if st.session_state.prompt:
                        st.write(f"Positive prompt: {st.session_state.prompt}")
                    if p_col2.button("Clear prompt cache"):
                        st.session_state.prompt = [""]
                    if sd_ui == "webui":
                        draw_cols1,draw_cols2,draw_cols3 = st.columns(3)
                        draw_cols4,draw_cols5,draw_cols6 = st.columns(3)
                        img_name = draw_cols1.text_input("Image filename", placeholder="test", key="test")
                        mode = draw_cols2.selectbox("Render mode", sd_api.mode_list)
                        sd_model_checkpoint = draw_cols3.selectbox("Base model", models_names)
                        negative_prompt = draw_cols4.text_input("Negative prompt", placeholder=sd_api.negative_prompt, key=sd_api.negative_prompt)
                        steps = draw_cols5.number_input("Steps", min_value=0, max_value=100, value=sd_api.steps)
                        sampler_name = draw_cols6.selectbox("Sampler", sd_api.sampler_name)
                        if st.button("Generate"):
                            code = sd_api.sd_webui_generate_image("".join(st.session_state.prompt), img_name, mode, negative_prompt, steps, sampler_name, sd_model_checkpoint)
                            if code == 200:
                                st.image(f"template/img/{img_name}.png", caption="AI generated", use_column_width=True)
                                st.session_state.prompt = [""]
                            else:
                                st.error(code)
                    elif sd_ui == "comfyui":
                        uploaded_file = st.file_uploader("Upload a JSON file", type="json")
                        if uploaded_file is not None:
                            file_content = uploaded_file.getvalue()
                            json_string = file_content.decode('utf-8')
                            data = json.loads(json_string)
                            if st.button("Generate"):
                                images_name_list = sd_api.sd_comfyui_generate_image("".join(st.session_state.prompt),data)
                                st.image(f"{images_name_list[0]}", caption="AI generated", use_column_width=True)
                        else:
                            st.write("Please upload a JSON file.")
                except Exception as e:
                    st.error(e)
            with t7:
                uploaded_file = st.file_uploader("Upload an image...", type=["jpg", "png"])
                if uploaded_file is not None:
                    file_bytes = uploaded_file.read()
                    save_path = 'template/img'
                    if not os.path.exists(save_path):
                        os.makedirs(save_path)
                    save_path_file = os.path.join(save_path, uploaded_file.name)
                    with open(save_path_file, 'wb') as file:
                        file.write(file_bytes)
                    try:
                        if st.button("Remove background"):
                            url = "http://localhost:7000/api/remove"
                            with open(save_path_file, 'rb') as file:
                                response = requests.post(url, files={'file': file})
                            with open(os.path.join(save_path,"rembg.png"), 'wb') as output_file:
                                output_file.write(response.content)
                            st.success("Background removed.")
                            st.image(os.path.join(save_path,"rembg.png"), caption='rembg', use_column_width=True)
                    except Exception as e:
                        st.error(f"Ensure the service is running: {e}")

    elif page == "Personalization":
        choose = st.selectbox("Personalization focus:", ["Knowledge", "Features"], index=0)
        if choose == "Knowledge":
            y_please = st.selectbox("Select:", ["Persona", "Neo4j Console (requires Neo4j)"], index=0)
            st.write("---")
            if y_please == "Persona":
                t1, t2 = st.tabs(["Config file", "Knowledge base"])
                with t1:
                    col_1, col_2 = st.columns(2)
                    role_keys_hps = role_hps.keys()
                    if_del = col_1.selectbox("Delete a persona template?", [True, False], index=1)
                    if if_del:
                        role_del = col_2.selectbox("Select a template to delete:", list(role_keys_hps), index=0)
                        if role_del == "Default Template":
                            st.error("The default template cannot be deleted.")
                        else:
                            if st.button("Delete persona template") and role_del != "Default Template":
                                role_mod = utils.load_json("configs/json/role_setting.json")
                                del role_mod[role_del]
                                utils.write_json(role_mod, "configs/json/role_setting.json")
                                st.success("Persona template deleted.")
                    edge_tts_voice, so_vits_svc_model, so_vits_svc_config, gpt_sovits_model = "", "", "", ""
                    from func.tts import tts_voices
                    col1, col2, col3, col4 = st.columns(4)
                    name_input = col1.text_input("Name", placeholder="Default Template")
                    if not name_input:
                        name_input = "Default Template"
                    if role_hps.get(name_input) == None:
                        role_json = utils.get_hparams_from_dict(role_hps.get("Default Template"))
                    else:
                        role_json = utils.get_hparams_from_dict(role_hps.get(name_input))
                    sex_input = col2.text_input("Gender", placeholder=role_json.sex)
                    age_input = col3.text_input("Age", placeholder=role_json.age)
                    emotion_input = col4.text_input("Emotion score", placeholder=role_json.emotion)
                    setting_input = st.text_input("Persona description", placeholder=role_json.setting)
                    emo_col1, emo_col2, emo_col3, emo_col4, emo_col5 = st.columns(5)
                    emotional_display_prompt_list = role_json.emotional_display
                    emotional_display_prompt_list[0] = emo_col1.text_input("0. Sad", placeholder=role_json.emotional_display[0])
                    emotional_display_prompt_list[1] = emo_col2.text_input("1. Anxious", placeholder=role_json.emotional_display[1])
                    emotional_display_prompt_list[2] = emo_col3.text_input("2. Calm", placeholder=role_json.emotional_display[2])
                    emotional_display_prompt_list[3] = emo_col4.text_input("3. Happy", placeholder=role_json.emotional_display[3])
                    emotional_display_prompt_list[4] = emo_col5.text_input("4. Excited", placeholder=role_json.emotional_display[4])
                    tts_plan = st.selectbox("Select TTS plan", ["plan_1:edge-tts+svc", "plan_2:gpt-sovits"], index=0)[0:6]
                    if tts_plan == "plan_1":
                        col5, col6 = st.columns(2)
                        edge_tts_voice = role_json.tts.plan_1.edge_tts
                        if edge_tts_voice in tts_voices.SUPPORTED_LANGUAGES:
                            default_index = tts_voices.SUPPORTED_LANGUAGES.index(edge_tts_voice)
                        else:
                            default_index = 0
                        edge_tts_voice = col5.selectbox("Edge TTS voice:", tts_voices.SUPPORTED_LANGUAGES, index=default_index)
                        text = col6.text_input("Test phrase:", "")
                        if st.button("Test edge-tts voice"):
                            tts_voices.to_edge_tts(text,edge_tts_voice,"template/tts/demo.mp3")
                            st.audio("template/tts/demo.mp3", format='audio/mp3')
                        col7, col8 = st.columns(2)
                        so_vits_svc_model = col7.text_input("so-vits-svc model path", placeholder=role_json.tts.plan_1.so_vits_svc)
                        so_vits_svc_config = col8.text_input("so-vits-svc config path", placeholder=role_json.tts.plan_1.so_vits_svc_config)
                    elif tts_plan == "plan_2":
                        res = requests.get(hps.api_path.gpt_sovits.url+"/character_list")
                        gpt_sovits_model = st.selectbox("Select gpt-sovits model", list(res.json().keys()))
                    easyaivtuber_img_dir_path = role_json.easyaivtuber_dir_path
                    easyaivtuber_img_path = st.text_input("EasyAIVtuber avatar image path (.png)", placeholder=easyaivtuber_img_dir_path)
                    if not sex_input:sex_input=role_json.sex
                    if not age_input:age_input=role_json.age
                    if not emotion_input:emotion_input=role_json.emotion
                    if not setting_input:setting_input=role_json.setting
                    if not edge_tts_voice:edge_tts_voice=role_json.tts.plan_1.edge_tts
                    if not so_vits_svc_model:so_vits_svc_model=role_json.tts.plan_1.so_vits_svc
                    if not so_vits_svc_config:so_vits_svc_config=role_json.tts.plan_1.so_vits_svc_config
                    if not gpt_sovits_model:gpt_sovits_model=role_json.tts.plan_2.gpt_sovits
                    if not easyaivtuber_img_path:easyaivtuber_img_path=role_json.easyaivtuber_dir_path
                    st.write("---")
                    if st.button("Save persona settings"):
                        st.write(name_input)
                        if name_input != "Default Template":
                            role_hps = utils.load_json("configs/json/role_setting.json")
                            role_hps.get("Default Template")["name"] = name_input
                            role_hps.get("Default Template")["setting"] = setting_input
                            role_hps.get("Default Template")["sex"] = sex_input
                            role_hps.get("Default Template")["age"] = age_input
                            role_hps.get("Default Template")["emotional_display"] = emotional_display_prompt_list
                            role_hps.get("Default Template")["emotion"] = emotion_input
                            role_hps.get("Default Template")["tts"]["plan_1"]["edge_tts"] = edge_tts_voice
                            role_hps.get("Default Template")["tts"]["plan_1"]["so_vits_svc"] = so_vits_svc_model
                            role_hps.get("Default Template")["tts"]["plan_1"]["so_vits_svc_config"] = so_vits_svc_config
                            role_hps.get("Default Template")["tts"]["plan_2"]["gpt_sovits"] = gpt_sovits_model
                            role_hps.get("Default Template")["easyaivtuber_dir_path"] = easyaivtuber_img_path
                            role_dict = utils.load_json("configs/json/role_setting.json")
                            role_dict[name_input] = role_hps.get("Default Template")
                            utils.write_json(role_dict,"configs/json/role_setting.json")
                            st.success("Persona settings updated.")
                        else:
                            st.error("The default template cannot be modified.")
                with t2:
                    st.write("**Restart the Flask backend after updating knowledge bases to reload configs.**")
                    st.write("---")
                    knowledge_databases = hps.ai_vtuber.knowledge_database
                    select_database = st.selectbox("Select knowledge base:", knowledge_databases, index=0)
                    if select_database:
                        st.info(f"Current knowledge base: {select_database.get('name', None)}")
                    introduction = st.text_input("Add a description for this knowledge base:")
                    d_col1, d_col_2 = st.columns(2)
                    if d_col1.button("Save configuration"):
                        config_data = utils.load_json("configs/json/config.json")
                        config_data["ai_vtuber"]["knowledge_database"] = [
                            {k: introduction if k == f'{list(select_database.keys())[0]}' else v for k, v in d.items()}
                            for d in config_data["ai_vtuber"]["knowledge_database"]
                        ]
                        utils.write_json(config_data, "configs/json/config.json")
                        st.success("Knowledge base updated.")
                    with st.expander("Song library"):
                        try:
                            data = pd.read_csv("configs/csv/song_library.csv", encoding="gbk")
                            edited_data = st.data_editor(data)
                            if st.button("Save changes"):
                                edited_csv = edited_data.to_csv(index=False)
                                st.download_button(
                                    label="Download updated song library CSV",
                                    data=edited_csv,
                                    file_name="edited_song_library.csv",
                                    mime="text/csv"
                                )
                            introduction = st.text_input("Song library description:", key="introduction")
                            if st.button("Update song library (requires Neo4j)"):
                                with st.spinner("Running task..."):
                                    from func.Neo4j_Database import make_n4j_database
                                    from func.Neo4j_Database import to_neo4j
                                    neo = to_neo4j.Neo4jHandler("configs/json/config.json")
                                    neo.connect_neo4j_database()
                                    neo.delete_nodes_for_label("Song Library")
                                    make_n4j_database.song_dict_to_neo4j(song_dict_path="data/json/song_dict.json",
                                                                         song_csv_path="configs/csv/song_library.csv",
                                                                         config_path="configs/json/config.json")
                                    config_data = utils.load_json("configs/json/config.json")
                                    config_data["ai_vtuber"]["knowledge_database"].append(
                                        {"name": "Song Library", "introduction": introduction, "plan": 0})
                                    utils.write_json(config_data, "configs/json/config.json")
                                    st.success("Updated successfully.")
                        except Exception as e:
                            st.error(e)

                    with st.expander("CSV to Neo4j"):
                        uploaded_file = st.file_uploader("Upload a CSV file to edit", type="csv")
                        if uploaded_file is not None:
                            data = pd.read_csv(uploaded_file, encoding="gbk")
                            edited_data = st.data_editor(data)
                            if st.button("Save Edited CSV"):
                                edited_csv = edited_data.to_csv(index=False)
                                st.download_button(
                                    label="Download Edited CSV",
                                    data=edited_csv,
                                    file_name="edited_data.csv",
                                    mime="text/csv"
                                )
                        if st.button("Convert CSV to Neo4j"):
                            from func.Neo4j_Database import make_n4j_database
                            make_n4j_database.cognition_to_neo4j(cognition_dict_path = "data/json/cognition.json",cognition_csv_path = "configs/csv/cognition.csv",config_path = "configs/json/config.json")
                            st.success("Knowledge base created.")

                    with st.expander("TXT to Neo4j/Chroma"):
                        uploaded_file = st.file_uploader("Upload a TXT file", type="txt")
                        if uploaded_file is not None:
                            if not os.path.exists(os.path.join("template/txt", uploaded_file.name)):
                                with open(os.path.join("template/txt", uploaded_file.name), "wb") as f:
                                    f.write(uploaded_file.getbuffer())
                            file_content = uploaded_file.read().decode("utf-8")
                            d_select = st.selectbox("Select knowledge base method:", ["Knowledge Graph", "Vector Database"], index=0)
                            if d_select == "Knowledge Graph":
                                s_select = st.selectbox("Select segmentation method", ["By length", "By QA lines"])
                                if s_select == "By length":
                                    segment_number = st.slider("Choose a number:", 0, 1000, value=100)
                                    segments = utils.split_text_by_length(file_content, segment_number)
                                elif s_select == "By QA lines":
                                    segments = utils.read_qa_from_txt(os.path.join("template/txt", uploaded_file.name))
                                    segments = [segment['question']+segment['answer'] for segment in segments]
                                st.write("Segments:", segments)
                                information_extraction = []
                                node_name_col1,introduction_col2 = st.columns(2)
                                node_name = node_name_col1.text_input("Learning label:", key="node_name")
                                if st.button("Start extraction"):
                                    if not introduction:introduction = ""
                                    t_ = 0  # Success count
                                    e_ = 0  # Error count
                                    total_segments = len(segments)
                                    progress = st.progress(0)
                                    for i, segment in enumerate(segments, 1):
                                        flag,res = tools.information_extraction(segment)
                                        res = [res]
                                        res.insert(0, node_name)
                                        if flag == "success":
                                            tools.information_to_neo4j(res)
                                            t_ += 1
                                        else:
                                            e_ += 1
                                            information_extraction.append(segment)
                                            st.write(res)
                                        progress.progress(i / total_segments)
                                    config_data = utils.load_json("configs/json/config.json")
                                    config_data["ai_vtuber"]["knowledge_database"].append({"name":f"{node_name}", "introduction":introduction,"plan":0})
                                    utils.write_json(config_data, "configs/json/config.json")
                                    error_log_json_string = json.dumps(information_extraction)
                                    with open('template/json/error_log.json', 'w', encoding='utf-8') as f:
                                        f.write(error_log_json_string)
                                    with open('template/txt/error_log.txt', 'a', encoding='utf-8') as f:
                                        if s_select == "By QA lines":
                                            for qa in information_extraction:
                                                f.write(qa)
                                        else:
                                            for qa in information_extraction:
                                                f.write(qa)
                                    st.write(f"Processed {t_} segments successfully, {e_} failed.")
                            elif d_select == "Vector Database":
                                segment_number = st.slider("Choose a number:", 0, 1000, value=100)
                                segments = utils.split_text_by_length(file_content, segment_number)
                                st.write("Segments:", segments)
                                node_name_col1, introduction_col2 = st.columns(2)
                                node_name = node_name_col1.text_input("Learning label:", key="node_name")
                                if st.button("Generate vector database"):
                                    data_dict = {"uploaded_file_name":uploaded_file.name,"node_name":node_name,"segment_number":segment_number,"introduction":introduction}
                                    response = requests.post('http://localhost:9550/tool/information_to_chroma', json=data_dict).json()
                                    if response["status_code"] == 200:
                                        st.success("Stored successfully.")
                                    else:
                                        st.error("An error occurred.")

                        else:
                            st.text("Please upload a TXT file.")
                    expander_del = st.expander("Delete knowledge base (label group)")
                    expander_del.header("Delete knowledge base (label group)")
                    label_name = expander_del.text_input("Label to delete:")
                    if expander_del.button("Delete knowledge base"):
                        from func.Neo4j_Database import to_neo4j
                        neo = to_neo4j.Neo4jHandler("configs/json/config.json")
                        neo.connect_neo4j_database()
                        neo.delete_nodes_for_label(label_name)
                        config_data = utils.load_json("configs/json/config.json")
                        config_data["ai_vtuber"]["knowledge_database"] = [d for d in config_data["ai_vtuber"]["knowledge_database"] if label_name != d["name"]]
                        utils.write_json(config_data, "configs/json/config.json")
                        st.success("Deleted successfully.")
                    with st.expander("Test"):
                        uploaded_file = st.file_uploader("Upload test TXT file", type="txt")
                        if uploaded_file is not None:
                            question_numbers = []
                            similarities_used = []
                            similarities_unused = []
                            if os.path.exists(os.path.join("template/txt", uploaded_file.name)):
                                with open(os.path.join("template/txt", uploaded_file.name), "wb") as f:
                                    f.write(uploaded_file.getbuffer())
                            segments = utils.read_qa_from_txt(os.path.join("template/txt", uploaded_file.name))
                            if st.button("Run test"):
                                save_json = []
                                progress_bar = st.progress(0)
                                with tqdm(total=len(segments), desc="Testing", unit="question", ascii=False, ncols=80) as pbar:
                                    for index, segment in enumerate(segments):
                                        query = segment["question"]
                                        answer = segment["answer"]
                                        data_search_in_neo4j = {"content": query}
                                        res = requests.post('http://localhost:9550/search_in_neo4j',
                                                            json=data_search_in_neo4j)
                                        data_chat = {"query": query, "reference_text": str(res.json())}
                                        bot_response = requests.post('http://localhost:9550/chat', json=data_chat).text
                                        similarity_used = tools.qa_judge(answer, bot_response)
                                        similarities_used.append(similarity_used)

                                        data_chat_without_reference = {"query": query}
                                        bot_response_without_reference = requests.post('http://localhost:9550/chat',
                                                                                       json=data_chat_without_reference).text
                                        similarity_unused = tools.qa_judge(answer, bot_response_without_reference)
                                        similarities_unused.append(similarity_unused)

                                        question_numbers.append(index)
                                        save_dict = {
                                            "question": query,
                                            "answer": answer,
                                            "reply_used": bot_response,
                                            "similarity_used": similarity_used,
                                            "reply_unused": bot_response_without_reference,
                                            "similarity_unused": similarity_unused,
                                        }
                                        save_json.append(save_dict)
                                        pbar.update(1)
                                        progress = (index + 1) / len(segments)
                                        progress_bar.progress(progress)
                                save_json_string = json.dumps(save_json)
                                with open('template/json/save_log.json', 'w', encoding='utf-8') as f:
                                    f.write(save_json_string)
                                plt.figure(figsize=(10, 5))
                                plt.plot(question_numbers, similarities_used, 'go-', label='With Reference')
                                plt.plot(question_numbers, similarities_unused, 'ro-', label='Without Reference')
                                plt.title('Answer Similarity')
                                plt.xlabel('Question Number')
                                plt.ylabel('Similarity')
                                plt.legend()
                                plt.grid(True)
                                st.pyplot(plt)
                                plt.savefig("template/imgs/chart.png")
                        if st.button("Show test logs"):
                            st.image("template/imgs/chart.png")
                            with open('template/json/save_log.json', 'r', encoding='utf-8') as f:
                                save_log = json.load(f)
                            count = sum(
                                1
                                for item in save_log
                                if abs(item["similarity_used"] - item["similarity_unused"]) <= 5
                                or item["similarity_used"] >= item["similarity_unused"]
                            )
                            st.write(
                                "Share of cases where similarity_used is higher or within 5 points: "
                                f"{(count/len(save_log))*100}%"
                            )
                            st.write(save_log)

            elif y_please == "Neo4j Console (requires Neo4j)":
                p = st.text_input("[Auth] Type the phrase below:", placeholder="CLEAR_GRAPH_DB")
                neo4j_url = hps.api_path.neo4j.url
                url, port = utils.extract_port_and_url(neo4j_url)
                if st.button("Clear graph database (stop Neo4j first)"):
                    if not utils.check_port(url, port) and (p == "CLEAR_GRAPH_DB"):
                        import shutil
                        try:
                            shutil.rmtree("tools/neo4j-chs-community-4.2.2-windows/data/databases/neo4j")
                            shutil.rmtree("tools/neo4j-chs-community-4.2.2-windows/data/transactions/neo4j")
                            print(f"Folder 'tools/neo4j-chs-community-4.2.2-windows/data/databases/neo4j' has been deleted.")
                        except FileNotFoundError:
                            print(f"Folder 'tools/neo4j-chs-community-4.2.2-windows/data/transactions/neo4j' does not exist.")
                        except Exception as e:
                            print(f"An error occurred while deleting : {e}")
                        st.success("Graph database cleared.")
                    else:
                        st.error("Stop Neo4j first.")
                if utils.check_port(url, port):
                    from func.Neo4j_Database import to_neo4j
                    neo_db = to_neo4j.Neo4jHandler("configs/json/config.json")
                    neo_db.connect_neo4j_database()
                    if st.button("Open Neo4j Browser"):
                        st.write("[Open Neo4j Browser](http://localhost:7474/browser/)")
                    please = st.selectbox(
                        "Select action:",
                        ["Add Node", "Set Relationship", "Query Node", "Query Related Nodes", "Update Node", "Delete Node"],
                        index=0,
                    )
                    if please == "Add Node":
                        input_node_name = st.text_input("Node name:", "")
                        input_node_properties_name = st.text_input("Property name:")
                        input_node_properties_value = st.text_input("Property value:")
                        node_properties = get_properties()
                        if st.button("Add property"):
                            if input_node_properties_name and input_node_properties_value:
                                node_properties[input_node_properties_name] = input_node_properties_value
                                save_properties_to_file(node_properties)
                                st.success("Property added.")
                            else:
                                st.error("Enter both property name and value.")

                        selected_properties = st.multiselect("Select properties to edit:", list(node_properties.keys()),
                                                             default=list(node_properties.keys()))
                        if st.button("Delete property"):
                            for property_name in selected_properties:
                                del node_properties[property_name]
                            save_properties_to_file(node_properties)
                            st.success("Property deleted.")
                        st.write("Current properties:", get_properties())
                        if st.button("Add node"):
                            node_properties = get_properties()
                            neo_db.add_node(input_node_name,node_properties)
                            st.success("Node created.")
                    elif please == "Set Relationship":
                        node1_name = st.text_input("Node 1 name:", "")
                        node1_list = neo_db.search_node(node1_name) if node1_name else []
                        node2_name = st.text_input("Node 2 name:", "")
                        node2_list = neo_db.search_node(node2_name) if node2_name else []
                        nodes1 = st.selectbox("Select node 1:", json.loads(json.dumps(node1_list)), index=0)
                        nodes2 = st.selectbox("Select node 2:", json.loads(json.dumps(node2_list)), index=0)
                        relationship_name = st.text_input("Relationship name:", "")
                        relationship_properties = st.text_input("Relationship properties", "")
                        if not relationship_properties: relationship_properties = "{}"
                        if st.button("Create relationship (node1 -> node2)"):
                            nodes1 = neo_db.search_node(node1_name,nodes1["node"])
                            nodes2 = neo_db.search_node(node2_name,nodes2["node"])
                            neo_db.set_relationship(nodes1[0]["node"], nodes2[0]["node"], relationship_name, properties=json.loads(relationship_properties))
                            st.success("Relationship created.")
                    elif please == "Query Node":
                        query_type = st.selectbox("Select query type:", ["By name", "By name + property"], index=0)
                        input_node_name = st.text_input("Node name:", "")
                        if query_type == "By name":
                            nodes = neo_db.search_node(input_node_name) if input_node_name else None
                            nodes_list = to_neo4j.nodes_to_json(nodes) if nodes else []
                            select_node = st.selectbox("Select node", nodes_list, index=0)
                            if st.button("Query"):
                                print(select_node)
                                query_node = to_neo4j.json_to_nodes(input_node_name,[select_node],config_path="configs/json/config.json")
                                st.write(query_node)
                        elif query_type == "By name + property":
                            input_node_properties_name = st.text_input("Property name:")
                            input_node_properties_value = st.text_input("Property value:")
                            node_properties = get_properties()
                            if st.button("Add property"):
                                if input_node_properties_name and input_node_properties_value:
                                    node_properties[input_node_properties_name] = input_node_properties_value
                                    save_properties_to_file(node_properties)

                                    st.success("Property added.")
                                else:
                                    st.error("Enter both property name and value.")
                            selected_properties = st.multiselect(
                                "Select properties to edit:",
                                list(node_properties.keys()),
                                                                 default=list(node_properties.keys()))
                            if st.button("Delete property"):
                                for property_name in selected_properties:
                                    del node_properties[property_name]
                                save_properties_to_file(node_properties)
                                st.success("Property deleted.")
                            if st.button("Query"):
                                result = neo_db.search_node(input_node_name, node_properties)
                                st.write(result)

                    elif please == "Query Related Nodes":
                        input_node_name = st.text_input("Node name:", "")
                        input_node_relationship_type = st.text_input("Relationship type:", "")
                        nodes = neo_db.search_node(input_node_name) if input_node_name else None
                        nodes_list = to_neo4j.nodes_to_json(nodes) if nodes else []
                        select_node = st.selectbox("Select node", nodes_list, index=0)
                        if st.button("Query related nodes"):
                            query_node = to_neo4j.json_to_nodes(input_node_name, [select_node],
                                                                config_path="configs/json/config.json")
                            result = neo_db.find_related_nodes(query_node[0]["node"], input_node_relationship_type)
                            st.write(result)


                    elif please == "Delete Node":
                        node_name = st.text_input("Node name to delete:", "")
                        node_list = neo_db.search_node(node_name) if node_name else []
                        del_node = st.selectbox("Select node to delete:", json.loads(json.dumps(node_list)), index=0)
                        if st.button("Delete node"):
                            del_node = neo_db.search_node(node_name, del_node["node"])
                            st.write(del_node[0])
                            neo_db.delete_node(del_node[0]["node"])
                            st.success("Node deleted.")
            else:
                input_keyword = st.text_input("Keyword:", "")
                st.write(input_keyword)

        elif choose == "Features":
            t1 = st.checkbox("Customize so-vits-svc voice model")
            if t1:
                command = f"{project_root}\\runtime\\miniconda3\\envs\\ai-vtuber\\python.exe -m streamlit run UI/to_sovits_ui.py"
                subprocess.Popen(['start', 'cmd', '/k', command], shell=True)


def main():
    # Initialization
    folder_path_list = ['template/img','template/tts','template/txt','template/downloads','template/json','template/uploads','template/uvr5_opt']
    for folder_path in folder_path_list:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
    hps = utils.get_hparams_from_file("configs/json/config.json")
    role_hps = utils.get_hparams_from_file("configs/json/role_setting.json")
    main_page(hps,role_hps)

if __name__ == '__main__':
    main()
