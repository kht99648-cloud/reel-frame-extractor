import os
import cv2

def convert_video_to_photos(video_path, output_dir, interval_seconds=2.0):
    os.makedirs(output_dir, exist_ok=True)
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video at '{video_path}'.")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0 or fps is None:
        print("Error: Could not read video frame rate.")
        return

    frame_step = int(fps * interval_seconds)
    frame_count = 0
    saved_count = 0

    print(f"Processing video: {video_path}")
    print(f"Extracting 1 photo every {interval_seconds} second(s)...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_step == 0:
            timestamp_sec = int(frame_count / fps)
            filename = f"activity_{saved_count + 1:04d}_time_{timestamp_sec}s.jpg"
            save_path = os.path.join(output_dir, filename)
            cv2.imwrite(save_path, frame)
            saved_count += 1

        frame_count += 1

    cap.release()
    print(f"\nDone! Successfully saved {saved_count} photos to:\n'{output_dir}'")

# --- AUTO-LOCATE YOUR VIDEO ---
folder_path = r"C:\Users\user\Desktop\K1M H3NG\HTML\extracted"
output_folder_path = os.path.join(folder_path, "activity_photos")

# Search for video files inside the 'extracted' folder automatically
video_extensions = ('.mp4', '.mov', '.avi', '.mkv', '.webm')
target_video = None

# Check if 'mp4' file exists directly
for file in os.listdir(folder_path):
    if file.lower().endswith(video_extensions) or file.lower() == 'mp4':
        target_video = os.path.join(folder_path, file)
        break

if target_video:
    convert_video_to_photos(target_video, output_dir=output_folder_path, interval_seconds=2.0)
else:
    print(f"Error: No video file found inside '{folder_path}'. Please check your folder.")