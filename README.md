# AI-VTUBER

<a href="//github.com/whoiswennie/AI-Vtuber/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/whoiswennie/AI-Vtuber?color=%09%2300BFFF&style=flat-square"></a>   <a href="//github.com/whoiswennie/AI-Vtuber/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/whoiswennie/AI-Vtuber?color=Emerald%20green&style=flat-square"></a>   <a href="//github.com/whoiswennie/AI-Vtuber/network"><img alt="GitHub forks" src="https://img.shields.io/github/forks/whoiswennie/AI-Vtuber?color=%2300BFFF&style=flat-square"></a>   <a href="//www.python.org"><img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="python"></a>


---
## Overview

**A fully customizable, end-to-end AI VTuber platform built for live streaming on Twitch, YouTube, and other major creator platforms. The system is powered by a large language model backend and features advanced intent recognition, along with both short-term and long-term memory systems (including direct memory and associative memory), allowing the VTuber to develop personality continuity and contextual awareness over time. Creators can build structured knowledge bases and music libraries, and seamlessly integrate state-of-the-art voice conversion, text-to-speech, image generation, and real-time virtual avatar animation technologies. All functionality is managed through an intuitive client application designed for smooth live operation, rapid customization, and creator-friendly workflows.**

Highlights:

- 1. Runs on modest GPUs; any system that can run Stable Diffusion should be sufficient.
- 2. The full deployment footprint can be large (~20GB+ plus third-party projects) due to virtual environments.
- 3. Bundled Miniconda3 environment management for easy extension.
- 4. Streamlit client for environment management, VTuber customization, auto-starting extensions, utilities, stream backend monitoring, and graph database editing.
- 5. End-to-end so-vits-svc 4.1 training + inference workflow.
- 6. Backend API server that exposes most services via GET/POST.
- 7. Persona template management with real-time switching.
- 8. Integrated open-source projects include: so-vits-svc 4.1 (voice conversion), GPT-SoVITS (speech synthesis), UVR5 (vocal separation), fast-whisper (ASR), Stable Diffusion WebUI/ComfyUI (image generation), EasyAIVtuber (avatar driving), rembg (background removal).
- 9. Utility tools: video/audio downloader, speech recognition, vocal separation, TTS, voice conversion, AI art, background removal.
- 10. Persona building via prompt templates, graph-based knowledge bases, and vector search (see author docs/blog for details).

---

## Resources

[Docs (WIP)](https://www.yuque.com/alipayxxda4itl6o/xgcgm6) | [Demo video (legacy)](https://www.youtube.com) | [Author portfolio](https://www.worldline-fantasy.top) | [Download bundle](https://pan.quark.cn/s/c029ea988d38)


## Usage Notes

Release builds and integration bundles are provided.


---
## Current Feature Set

- [x] **Available features:**
  - [x] Twitch and YouTube live chat listeners (new)
  - [x] Legacy BiliBili open platform listener
  - [x] edge-tts + svc for customized speech synthesis
  - [x] GPT-SoVITS support
  - [x] Zhipu API support
  - [x] Graph database for flexible local song library search
  - [x] Knowledge bases via vector DB + knowledge graph
  - [x] Automated knowledge graph tooling
  - [x] Multi-template AI VTuber personas
  - [x] Short-term + long-term memory
  - [x] Emotion-aware chat
  - [x] Intent routing: chat, singing, local/network search, drawing
  - [x] so-vits-svc training + inference workflow
  - [x] SD integration (WebUI + ComfyUI)
  - [x] EasyAIVtuber integration
  - [x] Streamlit client for management/customization

- [ ] **Current focus:**
  - [x] Improve documentation
  - [ ] Record updated usage tutorials
  - [x] Publish integration bundles

- [ ] **Future v2 plan (timeline may be slow):**
  - 0. Reduce footprint and runtime cost
  - 1. Electron desktop app (primary)
  - 2. Expand Agent module with cost-effective LLMs
  - 3. Improve streamer interaction features
  - 4. Explore additional avatar pipelines (e.g., Live2D + image generation)
    Example: https://github.com/user-attachments/assets/9f699967-feb7-4dc8-9f38-b28a64d06c89


## Getting Started

**Prerequisites**

Release builds require downloading pretrained models into:
```pyth
runtime
├───miniconda3
└───pretrained_models
    ├───faster-whisper
    	└───large-v2
    		└───(place here)
    ├───gte-base-zh
    	└───(place here)
tools
├───uvr5
    └───uvr5_weights
        └───(place here)
```

**In the repo root, run the bat scripts:**

```pyth
Run condaenv.bat  # Set up the main environment (skip in bundles)
Run start.bat  # Launch the client
```

## Optional PyPI Mirrors
```pyth
Tsinghua: https://pypi.tuna.tsinghua.edu.cn/simple/
Aliyun: http://mirrors.aliyun.com/pypi/simple/
USTC: https://pypi.mirrors.ustc.edu.cn/simple/
HUST: http://pypi.hustunique.com/simple/
SJTU: https://mirror.sjtu.edu.cn/pypi/web/simple/
Douban: http://pypi.douban.com/simple/
```

## Avatar Demo (EasyAIVTuber integration, example: Firefly)

[Firefly: Sleeping]

https://github.com/whoiswennie/AI-Vtuber/assets/104626642/4422cde1-e6c2-4c7c-8562-f5f1d2ab5c8c

<video width="640" height="360" controls>
  <source src="assets/ly_sleep.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[Firefly: Talking]

https://github.com/whoiswennie/AI-Vtuber/assets/104626642/6bb1bfda-c1e4-4a16-812d-f155f3c7619c

<video width="640" height="360" controls>
  <source src="assets/ly_talk.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[Firefly: Song Request]

https://github.com/whoiswennie/AI-Vtuber/assets/104626642/8e5db4d6-f71c-4a94-a474-e5bd5f31f251

<video width="640" height="360" controls>
  <source src="assets/ly_search.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[Firefly: Singing]

https://github.com/whoiswennie/AI-Vtuber/assets/104626642/db5347d6-95f7-4836-95fd-00040e9826c4

<video width="640" height="360" controls>
  <source src="assets/ly_sing.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

---


## Integrations

https://github.com/xfgryujk/blivedm

https://github.com/ycyy/faster-whisper-webui

https://github.com/svc-develop-team/so-vits-svc

https://github.com/RVC-Boss/GPT-SoVITS

https://github.com/Anjok07/ultimatevocalremovergui

https://github.com/Ksuriuri/EasyAIVtuber

https://github.com/fishaudio/Bert-VITS2

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=whoiswennie/AI-Vtuber&type=Date)](https://star-history.com/#whoiswennie/AI-Vtuber&Date)
