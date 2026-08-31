import os
import zipfile
import imageio_ffmpeg
import streamlit as st
import yt_dlp
from concurrent.futures import ThreadPoolExecutor, as_completed

st.set_page_config(
    page_title="K1M H3NG | High-Speed Reel & Caption Downloader",
    page_icon="⚡",
    layout="centered"
)

# Folder to store downloaded videos and captions in session
STORAGE_DIR = "stored_videos"
os.makedirs(STORAGE_DIR, exist_ok=True)

# Custom Header Branding
st.markdown("<h3 style='text-align: center; color: #FF4B4B;'>🔥 K1M H3NG 🔥</h3>", unsafe_allow_html=True)
st.title("⚡ Turbo 1-Click Profile Reel Hub")
st.write("Batch process Facebook Reels concurrently at maximum speed, extract captions, and download in 1 click.")

tab1, tab2, tab3 = st.tabs(["⚡ Turbo Downloader", "🔍 Grab All Profile Links", "📂 Stored Videos Library"])


def download_single_reel(args):
    """Worker function to process single video concurrently"""
    idx, url = args
    video_file_name = f"reel_{idx}.mp4"
    caption_file_name = f"reel_{idx}_caption.txt"
    
    video_path = os.path.join(STORAGE_DIR, video_file_name)
    caption_path = os.path.join(STORAGE_DIR, caption_file_name)

    ydl_opts = {
        'format': 'best',  # Pre-merged format avoids slow FFmpeg post-processing merge steps
        'outtmpl': video_path,
        'quiet': True,
        'no_warnings': True,
        'ffmpeg_location': imageio_ffmpeg.get_ffmpeg_exe(),
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            caption_text = info.get('description') or info.get('title') or "No caption found for this post."
            
            with open(caption_path, "w", encoding="utf-8") as cap_file:
                cap_file.write(f"URL: {url}\n\n--- POST CAPTION ---\n\n{caption_text}")
        
        return True, (video_file_name, video_path), (caption_file_name, caption_path), url, None
    except Exception as e:
        return False, None, None, url, str(e)


# TAB 1: TURBO BATCH DOWNLOADER & 1-CLICK ZIP
with tab1:
    st.subheader("High-Speed Concurrent Downloader")
    st.caption("Paste profile Reel links below. Multiple videos will download simultaneously!")
    
    urls_input = st.text_area(
        "Paste Reel Links (One per line):",
        placeholder="https://www.facebook.com/reel/1000123456789\nhttps://www.facebook.com/reel/1000987654321",
        height=180
    )
    
    # Speed adjustment control
    max_workers = st.slider("Parallel Downloads (Concurrent Threads)", min_value=2, max_value=8, value=4, help="Higher values speed up downloads but require more network bandwidth.")

    if st.button("🚀 Process All Videos (Turbo Mode)", type="primary"):
        urls = [url.strip() for url in urls_input.splitlines() if url.strip()]
        
        if not urls:
            st.warning("Please paste at least one Facebook Reel URL.")
        else:
            downloaded_files = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            tasks = [(idx, url) for idx, url in enumerate(urls, 1)]
            completed_count = 0
            total_tasks = len(urls)

            # Parallel Thread Pool Executor
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_url = {executor.submit(download_single_reel, task): task for task in tasks}
                
                for future in as_completed(future_to_url):
                    success, vid_info, cap_info, url, err = future.result()
                    completed_count += 1
                    
                    if success:
                        downloaded_files.append(vid_info)
                        downloaded_files.append(cap_info)
                    else:
                        st.error(f"Failed link: {url} | Error: {err}")

                    status_text.text(f"Processed {completed_count} of {total_tasks} videos...")
                    progress_bar.progress(completed_count / total_tasks)

            status_text.success("⚡ All downloads finished in record time!")

            # PACK MP4s AND CAPTION TXTs INTO 1-CLICK ZIP
            if downloaded_files:
                zip_path = os.path.join(STORAGE_DIR, "K1M_H3NG_reels_and_captions.zip")
                with zipfile.ZipFile(zip_path, "w") as zipf:
                    for filename, filepath in downloaded_files:
                        zipf.write(filepath, arcname=filename)

                with open(zip_path, "rb") as zf:
                    st.download_button(
                        label="📦 ONE-CLICK DOWNLOAD ALL (VIDEOS + CAPTIONS .ZIP)",
                        data=zf.read(),
                        file_name="K1M_H3NG_reels_and_captions.zip",
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
    st.caption("Access, replay, view captions, or delete files saved in your current session.")
    
    files = [f for f in os.listdir(STORAGE_DIR) if f.endswith('.mp4')]
    
    if not files:
        st.info("No stored videos yet. Use Tab 1 to download Reels.")
    else:
        if st.button("🗑️ Clear All Stored Files", type="secondary"):
            for root, dirs, filenames in os.walk(STORAGE_DIR):
                for f in filenames:
                    os.remove(os.path.join(root, f))
            st.success("All stored files have been deleted!")
            st.rerun()

        st.write(f"**Stored Files ({len(files)} total):**")
        for f in files:
            file_path = os.path.join(STORAGE_DIR, f)
            caption_file = f.replace(".mp4", "_caption.txt")
            caption_file_path = os.path.join(STORAGE_DIR, caption_file)

            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.write(f"📄 **{f}**")
            with col2:
                if st.button("Delete", key=f"del_{f}"):
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    if os.path.exists(caption_file_path):
                        os.remove(caption_file_path)
                    st.success(f"Deleted {f}")
                    st.rerun()
                    
            with open(file_path, "rb") as video_file:
                st.video(video_file.read())

            if os.path.exists(caption_file_path):
                with open(caption_file_path, "r", encoding="utf-8") as cap_file:
                    st.text_area(f"Caption for {f}:", cap_file.read(), height=100, key=f"txt_{f}")
