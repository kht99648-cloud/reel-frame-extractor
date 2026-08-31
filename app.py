import os
import tempfile
import zipfile
import cv2
import imageio_ffmpeg
import streamlit as st
import yt_dlp

st.set_page_config(
    page_title="1-Click Reel Downloader & Storage Hub",
    page_icon="🎬",
    layout="centered"
)

# Folder to store downloaded videos in session
STORAGE_DIR = "stored_videos"
os.makedirs(STORAGE_DIR, exist_ok=True)

st.title("🎬 1-Click Profile Reel Hub")
st.write("Batch process Facebook Reels, auto-store files, and download everything in 1 click.")

tab1, tab2, tab3 = st.tabs(["⚡ 1-Click Batch Downloader", "🔍 Grab All Profile Links", "📂 Stored Videos Library"])

def process_video_extraction(video_bytes, interval):
    """Extracts activity frames from video bytes and renders them in Streamlit."""
    with tempfile.TemporaryDirectory() as temp_dir:
        input_video_path = os.path.join(temp_dir, "input_video.mp4")
        
        with open(input_video_path, "wb") as f:
            f.write(video_bytes)

        cap = cv2.VideoCapture(input_video_path)
        if not cap.isOpened():
            st.error("Could not process video file.")
            return

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps == 0 or fps is None:
            return

        frame_step = int(fps * interval)
        frame_count = 0
        saved_frames = []

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % frame_step == 0:
                timestamp_sec = int(frame_count / fps)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                saved_frames.append((frame_rgb, timestamp_sec))

            frame_count += 1

        cap.release()

        st.write(f"**Extracted {len(saved_frames)} Activity Photos:**")
        cols = st.columns(3)
        for idx, (frame_rgb, timestamp) in enumerate(saved_frames):
            col = cols[idx % 3]
            col.image(frame_rgb, caption=f"Time: {timestamp}s", use_container_width=True)


# TAB 1: BATCH DOWNLOADER & 1-CLICK ZIP
with tab1:
    st.subheader("1-Click Batch Downloader")
    st.caption("Paste profile Reel links below. All videos will download and compress into 1 click!")
    
    urls_input = st.text_area(
        "Paste Reel Links (One per line):",
        placeholder="https://www.facebook.com/reel/1000123456789\nhttps://www.facebook.com/reel/1000987654321",
        height=150
    )
    
    extract_frames = st.checkbox("Also extract activity frames for each video", value=False)
    extract_interval = st.slider("Photo Extraction Interval (seconds):", 0.5, 10.0, 2.0)
    
    if st.button("🚀 Process All Videos", type="primary"):
        urls = [url.strip() for url in urls_input.splitlines() if url.strip()]
        
        if not urls:
            st.warning("Please paste at least one Facebook Reel URL.")
        else:
            downloaded_files = []
            progress_bar = st.progress(0)
            status_text = st.empty()

            for idx, url in enumerate(urls, 1):
                status_text.text(f"Downloading Video {idx} of {len(urls)}...")
                file_name = f"reel_{idx}.mp4"
                save_path = os.path.join(STORAGE_DIR, file_name)

                ydl_opts = {
                    'format': 'bestvideo+bestaudio/best',
                    'outtmpl': save_path,
                    'quiet': True,
                    'merge_output_format': 'mp4',
                    'ffmpeg_location': imageio_ffmpeg.get_ffmpeg_exe(),
                }

                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])
                    
                    downloaded_files.append((file_name, save_path))
                    
                    if extract_frames:
                        with open(save_path, "rb") as f:
                            process_video_extraction(f.read(), extract_interval)

                except Exception as e:
                    st.error(f"Failed link {idx}: {url} | Error: {e}")

                progress_bar.progress(idx / len(urls))

            status_text.success("All videos downloaded and stored!")

            # PACK INTO ZIP FOR 1-CLICK DEVICE DOWNLOAD
            if downloaded_files:
                zip_path = os.path.join(STORAGE_DIR, "all_profile_reels.zip")
                with zipfile.ZipFile(zip_path, "w") as zipf:
                    for filename, filepath in downloaded_files:
                        zipf.write(filepath, arcname=filename)

                with open(zip_path, "rb") as zf:
                    st.download_button(
                        label="📦 ONE-CLICK DOWNLOAD ALL VIDEOS (.ZIP)",
                        data=zf.read(),
                        file_name="all_profile_reels.zip",
                        mime="application/zip",
                        type="primary",
                        use_container_width=True
                    )


# TAB 2: PROFILE LINK COLLECTOR
with tab2:
    st.subheader("How to Collect Links From Any Profile")
    st.markdown("""
    Because Facebook blocks direct profile crawlers, use this snippet to copy all profile Reel links in 3 seconds:

    1. Open any Facebook Profile/Page **Reels tab** in your web browser.
    2. Scroll down until the videos you want are loaded on screen.
    3. Press **F12** (Developer Tools) $\rightarrow$ switch to **Console** $\rightarrow$ paste this snippet $\rightarrow$ hit **Enter**:
    """)
    
    st.code("""
let links = Array.from(document.querySelectorAll('a'))
  .map(a => a.href)
  .filter(href => href.includes('/reel/'));
let uniqueLinks = [...new Set(links)];
copy(uniqueLinks.join('\\n'));
alert(uniqueLinks.length + " Reel links copied! Paste them into Tab 1.");
    """, language="javascript")


# TAB 3: STORAGE GALLERY & MANAGEMENT
with tab3:
    st.subheader("Stored Videos Library")
    st.caption("Access, replay, or delete files saved in your current session.")
    
    files = [f for f in os.listdir(STORAGE_DIR) if f.endswith('.mp4')]
    
    if not files:
        st.info("No stored videos yet. Use Tab 1 to download Reels.")
    else:
        # Clear All Button
        if st.button("🗑️ Clear All Stored Videos", type="secondary"):
            for file in os.listdir(STORAGE_DIR):
                file_path = os.path.join(STORAGE_DIR, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            st.success("All stored videos have been deleted!")
            st.rerun()

        st.write(f"**Stored Files ({len(files)} total):**")
        for f in files:
            file_path = os.path.join(STORAGE_DIR, f)
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.write(f"📄 **{f}**")
            with col2:
                # Delete Individual File
                if st.button("Delete", key=f"del_{f}"):
                    os.remove(file_path)
                    st.success(f"Deleted {f}")
                    st.rerun()
                    
            with open(file_path, "rb") as video_file:
                st.video(video_file.read())
