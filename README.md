# ReelsAI

**A quick and easy way to leverage [Kokoro TTS](https://github.com/hexgrad/kokoro) to automate the creation of short-form video content.**

This Python script runs natively on your system, while Kokoro AI can be used via Docker, ensuring broad compatibility across operating systems. I use Linux, but you can install it on Windows, macOS, and more.

## Prerequisites

1. **Kokoro TTS**  
   Set up the Kokoro TTS FastAPI server by following the instructions in the [Kokoro-FastAPI Quick Start](https://github.com/remsky/Kokoro-FastAPI). A convenient way is to use the provided Docker Compose setup.

2. **Python Requirements**  
   Install all required Python packages using the `requirements.txt` included in this repository:
   ```bash
   pip install -r requirements.txt
   ```

3. **Background Video**  
   Place any MP4 files you want to use as backgrounds in the `assets/background_videos` folder.

## Usage

1. **Run Kokoro TTS**  
   After setting up Kokoro TTS, ensure it is up and running. You should be able to test it by navigating to [http://localhost:8880/web](http://localhost:8880/web).  
   - If you have changed the default port or are hosting on another machine, update the URL in `video.py` accordingly:
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

2. **Run ReelsAI**  
   From the root of this project, launch the Streamlit application:
   ```bash
   python3 -m streamlit run webui.py
   ```

3. **Multiple Video Option**  
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

## Demo and Small Tutorial

For a demonstration of how ReelsAI works, check out [this YouTube video](#).  
The video includes a small demo of the tool in action and a quick tutorial on how to get it running (excluding the Kokoro setup part).

---

Feel free to open an issue or submit a pull request if you have suggestions or improvements. Happy automating!
