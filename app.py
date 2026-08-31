import os
import tempfile
import cv2
import imageio_ffmpeg
import streamlit as st
import yt_dlp

st.set_page_config(
    page_title="Facebook Profile Reel & Batch Downloader",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Facebook Reel & Frame Extractor")

tab1, tab2, tab3 = st.tabs(["🌐 Batch Reel Downloader", "🔍 Link Collector Helper", "📁 Local Upload"])

def process_video_extraction(video_bytes, interval):
    """Extracts frames from video bytes and displays them in Streamlit."""
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
            st.error("Could not read frame rate from video.")
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

        st.write(f"**Extracted {len(saved_frames)} activity photos:**")
        cols = st.columns(3)
        for idx, (frame_rgb, timestamp) in enumerate(saved_frames):
            col = cols[idx % 3]
            col.image(frame_rgb, caption=f"Time: {timestamp}s", use_container_width=True)


# TAB 1: BATCH DOWNLOAER FOR PASTED LINKS
with tab1:
    st.subheader("1. Download Multiple Profile Reels")
    st.caption("Paste multiple public Facebook Reel URLs (one per line).")
    
    urls_input = st.text_area(
        "Facebook Reel URLs:",
        placeholder="https://www.facebook.com/reel/1000123456789\nhttps://www.facebook.com/reel/1000987654321",
        height=150
    )
    
    extract_interval_fb = st.slider("Photo Extraction Interval (seconds):", 0.5, 10.0, 2.0, key="fb_slider")
    
    if st.button("Download All Reels", type="primary", key="fb_btn"):
        urls = [url.strip() for url in urls_input.splitlines() if url.strip()]
        
        if not urls:
            st.warning("Please enter at least one valid Facebook Reel URL.")
        else:
            for idx, url in enumerate(urls, 1):
                st.markdown(f"--- \n### Processing Reel {idx} of {len(urls)}")
                with st.spinner(f"Fetching Reel {idx}..."):
                    with tempfile.TemporaryDirectory() as temp_dir:
                        output_path = os.path.join(temp_dir, f"reel_{idx}.mp4")
                        
                        ydl_opts = {
                            'format': 'bestvideo+bestaudio/best',
                            'outtmpl': output_path,
                            'quiet': True,
                            'merge_output_format': 'mp4',
                            'ffmpeg_location': imageio_ffmpeg.get_ffmpeg_exe(),
                        }
                        
                        try:
                            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                                ydl.download([url])
                            
                            with open(output_path, "rb") as file:
                                video_bytes = file.read()
                            
                            st.video(video_bytes)
                            st.download_button(
                                label=f"💾 Save Reel #{idx} to Device",
                                data=video_bytes,
                                file_name=f"facebook_reel_{idx}.mp4",
                                mime="video/mp4",
                                key=f"dl_{idx}"
                            )
                            
                            process_video_extraction(video_bytes, extract_interval_fb)
                            
                        except Exception as e:
                            st.error(f"Failed to download URL: {url}\nEnsure it's a public Reel.\nError: {e}")


# TAB 2: INSTRUCTIONS TO COPY PROFILE LINKS IN BULK
with tab2:
    st.subheader("2. How to Grab All Reel Links From Any Profile")
    st.info("Because Facebook blocks profile scrapers, follow these 3 steps to grab all links from a profile in 30 seconds:")
    
    st.markdown("""
    1. Open the Facebook Page/Profile **Reels** tab in your web browser.
    2. Scroll down until all the Reels you want to download are loaded on the screen.
    3. Press **F12** (or Right-Click → *Inspect*) to open Developer Console, switch to the **Console** tab, paste this JavaScript snippet, and press **Enter**:
    """)
    
    st.code("""
let links = Array.from(document.querySelectorAll('a'))
  .map(a => a.href)
  .filter(href => href.includes('/reel/'));
let uniqueLinks = [...new Set(links)];
console.log(uniqueLinks.join('\\n'));
copy(uniqueLinks.join('\\n'));
alert(uniqueLinks.length + " Reel links copied to your clipboard!");
    """, language="javascript")
    
    st.markdown("4. Switch back to **Tab 1** of this app and **Paste** into the text box!")


# TAB 3: LOCAL VIDEO UPLOAD
with tab3:
    st.subheader("3. Upload Local Videos")
    uploaded_files = st.file_uploader("Choose video files", type=["mp4", "mov", "avi", "mkv"], accept_multiple_files=True)
    extract_interval_local = st.slider("Photo Extraction Interval (seconds):", 0.5, 10.0, 2.0, key="local_slider")

    if uploaded_files:
        if st.button("Process Uploaded Files", type="primary", key="local_btn"):
            for idx, uploaded_file in enumerate(uploaded_files, 1):
                st.markdown(f"--- \n### Video {idx}: {uploaded_file.name}")
                video_bytes = uploaded_file.read()
                st.video(video_bytes)
                process_video_extraction(video_bytes, extract_interval_local)