import os
import random
import requests
import base64
import json
import re
import unicodedata

from moviepy import AudioFileClip, VideoFileClip, TextClip, CompositeVideoClip, vfx
from moviepy.video.VideoClip import ImageClip

from image import generate_my_post_image  # Custom image generation

# ---------------------------------------------------------------------
# Path & File Utilities
# ---------------------------------------------------------------------

video_folder = "assets/background_videos"
font_path = "assets/default/OpenSans-Bold.ttf"
output_dir = "assets/outputs"


def get_next_available_filename(directory, base_name="video", extension=".mp4"):
    """
    Find the next available filename by checking existing files.
    If 'video.mp4' doesn't exist, return that. Otherwise, pick video_1.mp4,
    video_2.mp4, etc., based on the highest existing number.
    """
    import os

    base_path = os.path.join(directory, base_name + extension)
    if not os.path.exists(base_path):
        return base_path  # If "video.mp4" doesn't exist, return it directly

    existing_files = [
        f for f in os.listdir(directory)
        if f.startswith(base_name + "_") and f.endswith(extension)
    ]

    numbers = []
    for filename in existing_files:
        try:
            num = int(filename.split("_")[-1].split(".")[0])
            numbers.append(num)
        except ValueError:
            pass

    next_number = max(numbers, default=0) + 1
    return os.path.join(directory, f"{base_name}_{next_number}{extension}")


# ---------------------------------------------------------------------
# Title Matching
# ---------------------------------------------------------------------

def find_title_end_time(raw_tokens, title_text):
    """
    Attempts to match all (or as many as possible) of the words in `title_text`
    with the tokens in `raw_tokens`. Returns the end_time of the final matched
    token, or a fallback (2.0) if matching fails.

    1) Flattens all newlines in title into spaces
    2) Removes punctuation in both the title and the tokens
    3) Never resets match index on mismatches (skips TTS extras)
    4) Debug prints to show matching progress
    """
    # Normalize unicode (handle “smart quotes,” etc.) & flatten whitespace
    normalized = unicodedata.normalize("NFKC", title_text)
    normalized = " ".join(normalized.split())  # flatten multi-spaces/newlines

    # Remove punctuation (except alphanumerics & whitespace)
    clean_title = re.sub(r"[^\w\s]", "", normalized)

    # Split into words
    wanted_words = clean_title.split()
    if not wanted_words:
        #print("DEBUG: Title is empty after removing punctuation!")
        return 2.0

    #print("DEBUG: Starting multi-line title matching...")
    #print(f"DEBUG: Wanted words => {wanted_words}\n")

    match_index = 0
    last_end_time = None

    for i, token in enumerate(raw_tokens):
        # Clean token word
        token_clean = re.sub(r"[^\w\s]", "", token["word"]).lower().strip()

        if match_index < len(wanted_words):
            wanted = wanted_words[match_index].lower()

            #print(f"DEBUG: Token[{i}]='{token_clean}' vs wanted='{wanted}'")
            if token_clean == wanted:
                match_index += 1
                last_end_time = token["end_time"]
                #print(f"      MATCH! match_index={match_index}, end_time={last_end_time}")

                # If we've matched all words, break
                if match_index == len(wanted_words):
                    #print("DEBUG: Matched entire title!")
                    return last_end_time
        else:
            # Matched them all, no need to continue
            break

    # If partial or no match, fallback to last_end_time or 2.0
    if last_end_time is None:
        #print("DEBUG: Could not match any or enough words from the multi-line title.")
        return 2.0
    else:
        #print("DEBUG: Partially matched the title; using last matched end_time.")
        return last_end_time


# ---------------------------------------------------------------------
# Token Merging (for Body Subtitles Only)
# ---------------------------------------------------------------------

def merge_for_subtitles(original_timestamps):
    """
    Merge short words like "a", "the" with their following word, reduce punctuation.
    This function is called AFTER we determine the title boundary so it won't
    break multi-line title matching.
    """
    merged = []
    i = 0

    merge_words = {"a", "an", "the", "or", "and"}
    allowed_punctuation = {"?"}
    remove_punctuation = {"!", ",", ".", ":", ";"}

    while i < len(original_timestamps):
        token = original_timestamps[i]
        word = token["word"]

        if word in remove_punctuation:
            i += 1
            continue

        if word in allowed_punctuation:
            if merged:
                merged[-1]["word"] += word
                merged[-1]["end_time"] = token["end_time"]
            else:
                merged.append(token)
            i += 1
            continue

        # Attempt to merge with next token if in merge_words
        if word.lower() in merge_words and i + 1 < len(original_timestamps):
            next_token = original_timestamps[i + 1]
            if next_token["word"] not in remove_punctuation:
                merged_word = word + " " + next_token["word"]
                merged_token = {
                    "word": merged_word,
                    "start_time": token["start_time"],
                    "end_time": next_token["end_time"]
                }
                # Merge punctuation if next is punctuation
                if (i + 2 < len(original_timestamps)
                    and original_timestamps[i + 2]["word"] in allowed_punctuation):
                    merged_token["word"] += original_timestamps[i + 2]["word"]
                    merged_token["end_time"] = original_timestamps[i + 2]["end_time"]
                    i += 1
                merged.append(merged_token)
                i += 2
                continue

        # Otherwise, just append as-is
        merged.append(token)
        i += 1

    return merged

# ---------------------------------------------------------------------
# Main Function: make_video
# ---------------------------------------------------------------------

def make_video(voice, speed, title, body):
    """
    Generates a video with a multi-line title shown first (as an image)
    and then body subtitles. The final clip is saved with an auto-incremented filename
    to avoid overwriting existing files.
    """
    title_text = title
    body_text = body
    combined_text = f"{title_text} {body_text}"

    # --- Step 1: TTS Request ---
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
    audio_json = json.loads(response.content)
    audio_data = base64.b64decode(audio_json["audio"].encode("utf-8"))
    timestamps = audio_json["timestamps"]

    # Save MP3 to disk
    with open("assets/cache/output.mp3", "wb") as f:
        f.write(audio_data)

    # --- Step 2: Generate cover image for the multi-line title ---
    generate_my_post_image(title_text)

    # --- Step 3: Use UNmerged tokens to find the title boundary ---
    raw_tokens = timestamps[:]  # shallow copy
    title_end_time = find_title_end_time(raw_tokens, title_text)

    # --- Step 4: Merge tokens for body subtitles only AFTER finding boundary ---
    merged_tokens = merge_for_subtitles(timestamps)

    # Filter out tokens that belong to the body (start_time >= title_end_time)
    body_tokens = [tok for tok in merged_tokens if tok["start_time"] >= title_end_time]

    # --- Step 5: Prepare background video & audio ---
    audio_clip = AudioFileClip("assets/cache/output.mp3")
    audio_duration = audio_clip.duration
    video_duration = audio_duration + 0.3
    video_files = [f for f in os.listdir(video_folder) if f.endswith(".mp4")]

    if video_files:
        random_video = random.choice(video_files)
        video_path = os.path.join(video_folder, random_video)
        bg_clip = VideoFileClip(video_path).subclipped(0, video_duration)
    else:
        print("No MP4 files found in the folder!")
        return

    # Resize background for Instagram Reels (1080x1920)
    bg_clip = bg_clip.resized(height=1920)
    crop_fx = vfx.Crop(
        x_center=bg_clip.w / 2,
        y_center=bg_clip.h / 2,
        width=1080,
        height=1920
    )
    bg_clip = crop_fx.apply(bg_clip)

    # --- Step 6: Create body text clips only for body tokens ---
    def create_text_clip(word, start_time, end_time):
        duration = end_time - start_time
        return (
            TextClip(
                text=word,
                font=font_path,
                font_size=110,
                size=(1920, 200),
                color='white',
                method='caption',
                text_align='center',
                horizontal_align='center',
                vertical_align='center',
                stroke_color='black',
                stroke_width=10
            )
            .with_duration(duration)
            .with_start(start_time)
            .with_position(('center', 1100))
        )

    text_clips = [
        create_text_clip(t["word"], t["start_time"], t["end_time"])
        for t in body_tokens
    ]

    # --- Step 7: Title image overlay for [0, title_end_time] ---
    title_image_clip = (
        ImageClip("assets/cache/reddit_post_cover.png")
        .with_duration(title_end_time)
        .with_position("center")
    )

    # --- Step 8: Composite the final clip ---
    final_clip = CompositeVideoClip([bg_clip, title_image_clip] + text_clips).with_audio(audio_clip)

    # --- Step 9: Output to a unique filename ---
    output_filename = get_next_available_filename(output_dir)

    final_clip.write_videofile(
        output_filename,
        fps=24,
        codec="libx264",  # Use NVIDIA GPU
        audio_codec="aac",
        preset="medium",
        ffmpeg_params=["-pix_fmt", "yuv420p"]
    )

    print(f"Video saved as: {output_filename}")
    return output_filename
