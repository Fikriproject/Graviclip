import os
import sys
import yt_dlp
import ffmpeg
import whisper
import warnings
from datetime import datetime, timedelta

# --- 🛠️ SYSTEM OVERRIDE: FORCE FFmpeg DETECTION ---
# Menambahkan folder ffmpeg ke sistem Python secara paksa
ffmpeg_path = r"C:\ffmpeg\bin"
os.environ["PATH"] += os.pathsep + ffmpeg_path

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

def zero_g_download(url, start_time, end_time, output_filename="output_clip.mp4"):
    """
    Downloads a portion of a video from a URL using yt-dlp and trims it using ffmpeg.

    Args:
        url (str): The URL of the video to download.
        start_time (str): Start time in 'HH:MM:SS' format.
        end_time (str): End time in 'HH:MM:SS' format.
        output_filename (str): The filename for the final clipped video.

    Returns:
        str: Path to the downloaded clip if successful, None otherwise.
    """
    
    # --- Input Validation ---
    try:
        t_start = datetime.strptime(start_time, "%H:%M:%S")
        t_end = datetime.strptime(end_time, "%H:%M:%S")
        if t_start >= t_end:
            raise ValueError("Start time must be before end time.")
    except ValueError as e:
        print(f"Error: Invalid time format or range. Use 'HH:MM:SS'. Details: {e}")
        return None

    print(f"[*] Initiating Zero-G Download sequence...")
    print(f"    Target: {url}")
    print(f"    Window: {start_time} - {end_time}")

    temp_filename = "temp_raw_video.mp4"
    
    # --- Step 1: Download with yt-dlp ---
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
        'outtmpl': temp_filename,
        'quiet': True,
        'no_warnings': True,
        'overwrites': True,
        # 👇 KUNCI PERBAIKAN: Memberitahu yt-dlp lokasi mesin ffmpeg secara spesifik
        'ffmpeg_location': ffmpeg_path, 
    }

    try:
        print(f"[*] Engaging yt-dlp for raw asset retrieval...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
    except yt_dlp.utils.DownloadError as e:
        print(f"Error: Download failed. Invalid URL or network issue.\nDetails: {e}")
        return None
    except Exception as e:
        print(f"Error: An unexpected error occurred during download.\nDetails: {e}")
        return None

    if not os.path.exists(temp_filename):
        print("Error: Temporary file not found after download attempt.")
        return None

    # --- Step 2: Trim with ffmpeg-python ---
    print(f"[*] Raw asset secured. Initializing ffmpeg for precision trim...")
    
    try:
        (
            ffmpeg
            .input(temp_filename, ss=start_time, to=end_time)
            .output(output_filename, c='copy') 
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        print(f"[*] Trim complete. Payload delivered to: {output_filename}")

    except ffmpeg.Error as e:
        print("Error: ffmpeg failed.")
        try:
            print(f"ffmpeg stderr: {e.stderr.decode('utf8')}")
        except:
            print(f"ffmpeg stderr: {e.stderr}")
        return None
    except FileNotFoundError:
        print("Error: ffmpeg binary not found. Even with override!")
        return None
    except Exception as e:
        print(f"Error: An unexpected error occurred during processing.\nDetails: {e}")
        return None
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
            print("[*] Temporary debris cleared.")

    return output_filename

def grav_warp_format(input_file, output_file="portrait_clip.mp4"):
    if not os.path.exists(input_file):
        print(f"Error: Gravity anomaly detected. Input file '{input_file}' does not exist.")
        return None

    print(f"[*] Warping dimensions to TikTok-spec (9:16)...")
    
    try:
        (
            ffmpeg
            .input(input_file)
            .filter('crop', 'ih*(9/16)', 'ih')
            .output(
                output_file, 
                vcodec='libx264', 
                preset='fast', 
                crf=23, 
                acodec='copy' 
            )
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        print(f"[*] Warp complete. Dimensional shift stabilized at: {output_file}")
        return output_file
        
    except ffmpeg.Error as e:
        print("Error: ffmpeg failed during warp.")
        try:
            print(f"ffmpeg stderr: {e.stderr.decode('utf8')}")
        except:
            print(f"ffmpeg stderr: {e.stderr}")
        return None
    except Exception as e:
        print(f"Error: An unexpected error occurred during warp.\nDetails: {e}")
        return None

def _seconds_to_srt_time(seconds):
    millis = int((seconds - int(seconds)) * 1000)
    delta = timedelta(seconds=int(seconds))
    h, m, s = str(delta).split(':')
    return f"{int(h):02}:{int(m):02}:{int(s):02},{millis:03}"

def levitate_subtitles(video_path, output_path="final_captioned.mp4"):
    if not os.path.exists(video_path):
        print(f"Error: Video void detected. '{video_path}' not found.")
        return None

    print(f"[*] AI is listening to the cosmic waves (extracting audio)...")
    temp_audio = "temp_audio_levitate.wav"
    temp_srt = "temp_subtitles_levitate.srt"

    # 1. Extract Audio
    try:
        (
            ffmpeg
            .input(video_path)
            .output(temp_audio, acodec='pcm_s16le', ac=1, ar='16k')
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        print("Error: Failed to extract audio coordinates.")
        return None

    # 2. Transcribe with Whisper
    print(f"[*] Subtitles materializing from the void (transcribing)...")
    try:
        model = whisper.load_model("base")
        result = model.transcribe(temp_audio, fp16=False)
    except Exception as e:
        print(f"Error: AI Transcription malfunction. Details: {e}")
        if os.path.exists(temp_audio): os.remove(temp_audio)
        return None

    # 3. Generate SRT
    print(f"[*] Forging SRT artifacts...")
    with open(temp_srt, "w", encoding="utf-8") as f:
        for i, segment in enumerate(result['segments']):
            start = _seconds_to_srt_time(segment['start'])
            end = _seconds_to_srt_time(segment['end'])
            text = segment['text'].strip()
            f.write(f"{i+1}\n{start} --> {end}\n{text}\n\n")

    # 4. Burn-in Subtitles
    print(f"[*] Etching runes onto the visual plane (burning subtitles)...")
    
    # FONT SIZE DIPERBESAR JADI 28 AGAR JELAS DI HP
    style_str = "FontName=Arial,FontSize=28,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,MarginV=30,Alignment=2,Bold=1"

    try:
        (
            ffmpeg
            .input(video_path)
            .output(
                output_path, 
                vf=f"subtitles={temp_srt}:force_style='{style_str}'",
                vcodec='libx264', 
                preset='fast', 
                crf=23, 
                acodec='copy'
            )
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        print(f"[*] Levitation complete. Final artifact: {output_path}")

    except ffmpeg.Error as e:
        print("Error: Subtitle fusion failed.")
        try:
            print(f"ffmpeg stderr: {e.stderr.decode('utf8')}")
        except:
            print(f"ffmpeg stderr: {e.stderr}")
        return None
    finally:
        if os.path.exists(temp_audio): os.remove(temp_audio)
        if os.path.exists(temp_srt): os.remove(temp_srt)
        print("[*] Cleaning up the cosmic dust...")

    return output_path
