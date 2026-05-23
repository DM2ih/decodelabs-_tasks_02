import os
import yt_dlp
from moviepy import VideoFileClip

def prepare_video_and_audio(video_input, is_url=True, local_video_path="input_video.mp4", local_audio_path="extracted_audio.mp3"):
    """
    Downloads YouTube URLs or processes uploaded local files,
    then extracts the underlying audio track safely.
    """
    if is_url:
        print("📥 YouTube URL detected. Downloading optimized video stream...")
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': local_video_path,
            'quiet': True,
            'retries': 10,
            'fragment_retries': 10,
            'socket_timeout': 30,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_input])
        video_source = local_video_path
    else:
        print("🎬 Local video file detected.")
        video_source = video_input

    if not os.path.exists(video_source):
        raise FileNotFoundError(f"Video source not found: {video_source}")

    print("🎧 Extracting audio track via MoviePy...")
    with VideoFileClip(video_source) as video:
        if video.audio is None:
            raise RuntimeError(f"No audio stream found in video: {video_source}")
        video.audio.write_audiofile(local_audio_path, logger=None)

    return video_source, local_audio_path

def slice_clip(video_path, start, end, output_filename):
    """Slices a specific segment of the video and saves it."""
    video = VideoFileClip(video_path)
    truncated_end = min(end, video.duration)
    
    if start >= video.duration:
        video.close()
        return False
        
    # --- FIX: Handle both MoviePy v1.x and v2.x methods ---
    if hasattr(video, "subclipped"):
        sub_clip = video.subclipped(start, truncated_end)  # MoviePy v2.0+
    else:
        sub_clip = video.subclip(start, truncated_end)    # MoviePy v1.x
    # ------------------------------------------------------
        
    sub_clip.write_videofile(output_filename, codec="libx264", audio_codec="aac", logger=None)
    video.close()
    return True