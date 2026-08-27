import os
import tempfile
import streamlit as st
import yt_dlp
import imageio_ffmpeg  # Added to supply FFmpeg automatically

st.set_page_config(page_title="Facebook Reel Downloader", page_icon="🎬", layout="centered")

st.title("🎬 Facebook Reel Downloader")
st.write("Paste a public Facebook Reel link below to fetch and download the video.")

reel_url = st.text_input("Facebook Reel URL:", placeholder="https://www.facebook.com/reel/1234567890")

if st.button("Fetch & Download Video", type="primary"):
    if not reel_url.strip():
        st.warning("Please enter a valid URL.")
    else:
        with st.spinner("Extracting and processing video..."):
            with tempfile.TemporaryDirectory() as temp_dir:
                output_path = os.path.join(temp_dir, "reel.mp4")
                
                ydl_opts = {
                    'format': 'bestvideo+bestaudio/best',
                    'outtmpl': output_path,
                    'quiet': True,
                    'merge_output_format': 'mp4',
                    'ffmpeg_location': imageio_ffmpeg.get_ffmpeg_exe(),  # Points yt-dlp to the imageio ffmpeg executable
                }
                
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([reel_url])
                    
                    with open(output_path, "rb") as file:
                        video_bytes = file.read()
                    
                    st.success("Download ready!")
                    st.video(video_bytes)
                    st.download_button(
                        label="💾 Save Video to Device",
                        data=video_bytes,
                        file_name="facebook_reel.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Failed to download video. Ensure the link is public.\nError: {e}")