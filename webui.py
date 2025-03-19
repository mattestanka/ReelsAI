import streamlit as st
import os
import time
import zipfile
from video import make_video  # Ensure this function exists in your project


# Streamlit UI
st.title("AI Video Creator 🎬")

# Sidebar settings (User selects voice and speed directly)
st.sidebar.header("Settings")
voice = st.sidebar.selectbox("Choose Voice", ["af_alloy","af_aoede","af_bella","af_heart","af_jadzia","af_jessica",
                                              "af_kore","af_nicole","af_nova","af_river","af_sarah","af_sky","af_v0",
                                              "af_v0bella","af_v0irulan","af_v0nicole","af_v0sarah","af_v0sky",
                                              "am_adam","am_echo","am_eric","am_fenrir","am_liam","am_michael",
                                              "am_onyx","am_puck","am_santa","am_v0adam","am_v0gurney","am_v0michael",
                                              "bf_alice","bf_emma","bf_lily","bf_v0emma","bf_v0isabella","bm_daniel",
                                              "bm_fable","bm_george","bm_lewis","bm_v0george","bm_v0lewis","ef_dora",
                                              "em_alex","em_santa","ff_siwis","hf_alpha","hf_beta","hm_omega","hm_psi",
                                              "if_sara","im_nicola","jf_alpha","jf_gongitsune","jf_nezumi",
                                              "jf_tebukuro","jm_kumo","pf_dora","pm_alex","pm_santa","zf_xiaobei",
                                              "zf_xiaoni","zf_xiaoxiao","zf_xiaoyi","zm_yunjian","zm_yunxi","zm_yunxia",
                                              "zm_yunyang"])
speed = st.sidebar.slider("Speech Speed", 0.5, 2.0, 1.0)

# Mode selection
mode = st.radio("Select Mode", ["Single", "Multiple"])

download_ready = False
output_files = []
video_output_dir = "assets/outputs"  # Directory to store generated videos


def clean_output_directory():
    """Removes all files from the output directory before generating new videos."""
    if os.path.exists(video_output_dir):
        for file in os.listdir(video_output_dir):
            file_path = os.path.join(video_output_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        print("✅ Cleaned up old videos in assets/outputs/")
    else:
        os.makedirs(video_output_dir)  # Ensure the directory exists


def process_video_file(script_content, voice, speed):
    """Processes multiple videos using raw script content (without saving to a file)."""

    # Split script content into lines (simulating reading from a file)
    lines = [line.rstrip() for line in script_content.splitlines()]  # Remove trailing spaces but keep structure

    videos = []
    title_lines = []
    body_lines = []
    is_body = False  # Start by reading the title

    for line in lines:
        if line.startswith("##"):  # Separator detected
            if title_lines and body_lines:  # If we have both title and body, save the video
                title = "\n".join(title_lines).strip()
                body = "\n".join(body_lines).strip()
                videos.append((title, body))
                title_lines.clear()
                body_lines.clear()

            is_body = not is_body  # Toggle between title and body mode
            continue  # Skip the ## line itself

        if is_body:
            body_lines.append(line)
        else:
            title_lines.append(line)

    # Ensure the last video is added if the file does not end with ##
    if title_lines and body_lines:
        videos.append((" ".join(title_lines).strip(), "\n".join(body_lines).strip()))

    if not videos:
        print("No valid video scripts found in the content.")
        return []

    output_videos = []

    for i, (t, b) in enumerate(videos):
        print(f"\nProcessing video {i + 1}/{len(videos)}...")
        print(f"Title: {t}")
        print(f"Body preview: {b[:50]}...")  # Show preview of body

        file_path = make_video(voice, speed, t, b)  # Call your video generation function
        output_videos.append(file_path)

    return output_videos  # Return list of generated video filenames


def create_zip(output_files):
    """Creates a ZIP archive from a list of file paths."""
    os.makedirs(video_output_dir, exist_ok=True)  # Ensure the directory exists
    zip_filename = os.path.join(video_output_dir, "generated_videos.zip")

    with zipfile.ZipFile(zip_filename, "w") as zipf:
        for file_path in output_files:
            zipf.write(file_path, os.path.basename(file_path))  # Store only the filename inside the ZIP

    return zip_filename


if mode == "Single":
    st.subheader("Single Video Mode")
    title = st.text_input("Enter Video Title")
    body = st.text_area("Enter Video Script")

    #background_option = st.radio("Choose Background", ["Upload", "Random"])
    #video_file = None
    #if background_option == "Upload":
    #    video_file = st.file_uploader("Upload Background Video", type=["mp4"])

    if st.button("Generate Video"):
        clean_output_directory()  # Cleanup before generating new videos
        with st.spinner("Generating video..."):
            file_path = make_video(voice, speed, title, body)
            output_files = [file_path]
            download_ready = True
        st.success(f"Video '{os.path.basename(file_path)}' is ready!")

elif mode == "Multiple":
    st.subheader("Multiple Videos Mode")

    script_file = st.file_uploader("Upload Script File (TXT)", type=["txt"])
    #background_option = st.radio("Choose Background", ["Upload", "Random"])
    #video_file = None
    #if background_option == "Upload":
    #    video_file = st.file_uploader("Upload Background Video", type=["mp4"])

    if st.button("Generate Videos"):
        if script_file is not None:
            clean_output_directory()  # Cleanup before generating new videos
            with st.spinner("Generating multiple videos..."):
                # Read the uploaded script file directly (without saving it)
                script_content = script_file.read().decode("utf-8")  # Convert bytes to string

                # Process the script content directly instead of reading from a file
                output_files = process_video_file(script_content, voice, speed)  # Pass content, not path

                download_ready = True
            if output_files:
                with st.spinner("Compressing videos into ZIP..."):
                    zip_file = create_zip(output_files)
                    st.success("All videos are ready!")
        else:
            st.error("Please upload a script file.")

# Provide a single download button for ZIP file after processing multiple videos
if download_ready and mode == "Multiple" and output_files:
    if os.path.exists(zip_file):  # Ensure the ZIP file exists
        with open(zip_file, "rb") as f:
            st.download_button(
                label="Download All Videos (ZIP)",
                data=f,
                file_name="generated_videos.zip",
                mime="application/zip"
            )

# Provide a download button for single mode
elif download_ready and mode == "Single" and output_files:
    file_path = output_files[0]
    if os.path.exists(file_path):  # Ensure the file exists before allowing download
        with open(file_path, "rb") as f:
            st.download_button(
                label="Download Video",
                data=f,
                file_name=os.path.basename(file_path),  # Extract only the filename
                mime="video/mp4"
            )
