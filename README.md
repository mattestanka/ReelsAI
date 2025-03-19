# ReelsAI

**A quick and easy way to leverage ************************[Kokoro TTS](https://github.com/hexgrad/kokoro)************************ to automate the creation of short-form video content.**

This project provides two ways to run ReelsAI:

1. **Native Python Execution** – Run directly on your system.
2. **Docker Compose Setup (Recommended for Speed & Ease of Use)** – A streamlined way to run everything using Docker.

I use Linux, but you can install and run it on Windows, macOS, and more.

---

## Prerequisites

### Option 1: Running Natively (Python)

1. **Kokoro TTS**\
   Set up the Kokoro TTS FastAPI server by following the instructions in the [Kokoro-FastAPI Quick Start](https://github.com/remsky/Kokoro-FastAPI). You can also use the provided Docker Compose setup (see the Docker section below).

2. **Python Requirements**\
   Install all required Python packages using the `requirements.txt` included in this repository:

   ```bash
   pip install -r requirements.txt
   ```

3. **Background Video**\
   Place any MP4 files you want to use as backgrounds in the `assets/background_videos` folder.

4. **Running Kokoro TTS**\
   Ensure Kokoro TTS is running. You can check by navigating to [http://localhost:8880/web](http://localhost:8880/web).\
   If you changed the port or are running it on another machine, update the `video.py` URL:

   ```python
   response = requests.post(
       "http://localhost:8880/dev/captioned_speech",
       json={
           "model": "kokoro",
           "input": combined_text,
           "voice": voice,
           "speed": speed,
           "response_format": "mp3",
           "stream": False,
       },
       stream=False
   )
   ```

5. **Launch ReelsAI**\
   From the root of this project, start the Streamlit application:

   ```bash
   python3 -m streamlit run webui.py
   ```

---

### Option 2: Running via Docker Compose (Recommended)

**Requirements:**

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/) (included with Docker Desktop on Windows/macOS)

#### Setup Steps

1. **Download the ************************`docker-compose.yaml`************************ file** from this repository.
2. **Modify the volume path** to point to your background video directory:
   ```yaml
   volumes:
     - "INSERT_PATH_HERE:/app/assets/background_videos"
   ```
   - On **Windows**, adjust the path: `C:\example\example` → `/c/example/example`
3. **Run the container**:
   ```bash
   docker-compose up -d
   ```

This method automatically sets up the environment and dependencies, making it the fastest way to get started.

---

## Usage

Simply navigate to [http://localhost:8501](http://localhost:8501) in your browser to use the program.

---

## Multiple Video Generation

To generate multiple videos in one run, create a text file with pairs of **title** and **body** separated by `##`, for example:

```
title for video 1
##
body for video 1
##
title for video 2
##
body for video 2
##
etc.
```

---

## Demo and Small Tutorial

For a demonstration of how ReelsAI works, check out [this YouTube video](https://youtu.be/UrhNAN6KP_Y?si=460zR_JwWp920IHy).\
The video includes a demo of the tool in action and a tutorial on how to get it running natively (excluding the Kokoro setup part).

For a quick start guide for windows check out [this YouTube video](https://youtu.be/ZFEPiPGhfR0).\


---

## Contributing

Feel free to open an issue or submit a pull request if you have suggestions or improvements. Happy automating!

