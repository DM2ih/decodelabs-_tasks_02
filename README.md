# The Multimodal Content Engine 🎬🎙️🎨

An automated, AI-powered multimedia orchestration pipeline designed to ingest long-form video content and programmatically distill it into short-form, high-engagement viral clips. 

The pipeline automates download logistics, speech-to-text conversion, algorithmic timestamp mapping, precise sub-clip slicing, and contextual B-roll artwork generation.

## 🚀 Key Features

* **Universal Feed Ingestion:** Automatically downloads optimized video streams directly from YouTube feeds or parses existing local `.mp4` data with built-in connection timeout recoveries.
* **Timestamped Audio Transcription:** Isolates speech signals using MoviePy and processes the audio matrix using Groq’s high-speed Whisper API implementation.
* **Contextual Viral Extraction:** Leverages large language models (`llama-3.3-70b-versatile`) to evaluate full conversational logs, programmatically extracting non-overlapping viral segments ranging between 60–90 seconds.
* **Sidecar Metadata Assets:** For every viral clip extracted, the engine creates social media distribution headlines, structured platform captions, and specific image creation prompts.
* **Automated B-Roll Harvesting:** Programmatically routes generated image prompts to Pollinations AI text-to-image models to export context-aware 1024x1024 graphics.
* **In-Notebook Rich Previews:** Includes a visualization engine that prints formatted HTML metadata blocks alongside active HTML5 streaming video preview players within the workspace.

---

## 🛠️ Tech Stack & Requirements

* **Core Language:** Python 3.10+
* **Multimedia Manipulation:** `moviepy`, `yt-dlp`
* **AI & Inference Gateways:** `requests` (Groq API, Pollinations AI REST APIs)
* **Foundation Models:** `whisper-large-v3` (Audio), `llama-3.3-70b-versatile` (Text)

---

## 📂 Workflow Directory Output

When processing is initiated, the engine dynamically organizes its outputs into matching local storage assets:

```text
├── input_video.mp4           # Downloaded target video feed
├── extracted_audio.mp3       # Isolated high-fidelity audio track
├── viral_clip_1.mp4          # Sliced video snippet (60-90s long)
├── clip_1_metadata.txt       # Headline, social description, and image prompt
└── broll_asset_1.jpg         # 1024x1024 context artwork generated for Clip 1
