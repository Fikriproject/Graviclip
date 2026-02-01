import os
import sys
import yt_dlp
import ffmpeg
import whisper
import warnings
from datetime import datetime, timedelta

try:
    import mediapipe as mp
    import cv2
    import numpy as np
except ImportError:
    mp = None
    warnings.warn("MediaPipe not found. Neural Split-Stacking will be disabled.")


# --- 🛠️ SYSTEM OVERRIDE: FORCE FFmpeg DETECTION ---
# Menambahkan folder ffmpeg ke sistem Python secara paksa
ffmpeg_path = r"C:\ffmpeg\bin"
os.environ["PATH"] += os.pathsep + ffmpeg_path

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

def zero_g_download(url, start_time, end_time, output_filename="output_clip.mp4"):
    """
    Downloads a portion of a video from a URL using yt-dlp and trims it using ffmpeg.
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
        'ffmpeg_location': ffmpeg_path, 
    }

    try:
        print(f"[*] Engaging yt-dlp for raw asset retrieval...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        # FIX: Check if file exists and is not empty
        if not os.path.exists(temp_filename) or os.path.getsize(temp_filename) == 0:
            print("Error: Download failed (Zero Byte Artifact).")
            return None
            
    except yt_dlp.utils.DownloadError as e:
        print(f"Error: Download failed. Invalid URL or network issue.\nDetails: {e}")
        return None
    except Exception as e:
        print(f"Error: An unexpected error occurred during download.\nDetails: {e}")
        return None

    # --- Step 2: Trim with ffmpeg-python ---
    print(f"[*] Raw asset secured. Initializing ffmpeg for precision trim (Ultrafast Mode)...")
    
    try:
        (
            ffmpeg
            .input(temp_filename, ss=start_time, to=end_time)
            .output(
                output_filename, 
                vcodec='libx264', 
                preset='ultrafast',  # TURBO: Ultrafast trim
                crf=25,
                acodec='aac'
            ) 
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
    except Exception as e:
        print(f"Error: An unexpected error occurred during processing.\nDetails: {e}")
        return None
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
            print("[*] Temporary debris cleared.")

    return output_filename

def detect_face_coordinates(video_path):
    """
    Scans the video for a face using MediaPipe and returns the normalized center x-coordinate.
    Only analyzes the first few seconds to get a general position.
    """
    if not mp or not hasattr(mp, 'solutions'):
        return None

    print("[*] Neural Network analyzing facial coordinates...")
    
    mp_face_detection = mp.solutions.face_detection
    cap = cv2.VideoCapture(video_path)
    
    face_x_coords = []
    frames_checked = 0
    max_frames = 50  # Check first 50 frames
    
    with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detection:
        while cap.isOpened() and frames_checked < max_frames:
            success, image = cap.read()
            if not success:
                break
            
            # TURBO: Optimization - Process every 15th frame
            if frames_checked % 15 == 0:
                image.flags.writeable = False
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = face_detection.process(image_rgb)
                
                if results.detections:
                    for detection in results.detections:
                        # Get bounding box
                        bboxC = detection.location_data.relative_bounding_box
                        center_x = bboxC.xmin + bboxC.width / 2
                        face_x_coords.append(center_x)
                        # We assume one main speaker, so break after first face
                        break 
            
            frames_checked += 1
            
    cap.release()
    
    if face_x_coords:
        # Return average center X
        return sum(face_x_coords) / len(face_x_coords)
    return None

def _seconds_to_srt_time(seconds):
    millis = int((seconds - int(seconds)) * 1000)
    delta = timedelta(seconds=int(seconds))
    h, m, s = str(delta).split(':')
    return f"{int(h):02}:{int(m):02}:{int(s):02},{millis:03}"

def grav_warp_and_subtitle_combo(input_file, output_file="final_graviclip.mp4", model_size="small"):
    """
    TURBO ENGINE: Single-Pass Rendering.
    Combines Neural Split-Stacking and Subtitle Burn-in into a single FFmpeg pass.
    """
    if not os.path.exists(input_file):
        print(f"Error: Void detected at '{input_file}'.")
        return None

    print(f"[*] Activating Turbo Engine: Single-Pass Rendering Sequence...")

    # Define temp file paths
    temp_audio = f"temp_turbo_audio_{int(datetime.now().timestamp())}.wav"
    temp_srt = f"temp_turbo_subs_{int(datetime.now().timestamp())}.srt"
    
    has_subtitles = False

    # --- 1. Audio Extraction & Transcription (Pre-Process) ---
    if model_size:
        print(f"[*] AI is listening to the cosmic waves (extracting audio)...")
        try:
            (
                ffmpeg
                .input(input_file)
                .output(temp_audio, acodec='pcm_s16le', ac=1, ar='16k')
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
        except ffmpeg.Error:
            print("Error: Audio extraction failed. Proceeding without subtitles.")
            model_size = None # Disable AI if extraction fails

    if model_size:
        print(f"[*] Upgrading Neural Cortex to [{model_size.upper()}] model...")
        try:
            model = whisper.load_model(model_size)
            result = model.transcribe(temp_audio, fp16=False)
            
            # Ensure SRT is not empty
            srt_content_written = False
            with open(temp_srt, "w", encoding="utf-8") as f:
                for i, segment in enumerate(result['segments']):
                    start = _seconds_to_srt_time(segment['start'])
                    end = _seconds_to_srt_time(segment['end'])
                    text = segment['text'].strip()
                    f.write(f"{i+1}\n{start} --> {end}\n{text}\n\n")
                    srt_content_written = True
                
                if not srt_content_written:
                    # Write dummy
                    f.write("1\n00:00:00,000 --> 00:00:01,000\n \n\n")
            
            has_subtitles = True
                    
        except Exception as e:
            print(f"Error: Transcription failed. {e}")
            model_size = None
        finally:
            if os.path.exists(temp_audio): os.remove(temp_audio)

    # --- 2. Neural Layout Logic ---
    print(f"[*] Calculating Neural Split-Stacking Coordinates...")
    face_center_x = detect_face_coordinates(input_file)
    
    try:
        probe = ffmpeg.probe(input_file)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        width = int(video_stream['width'])
        height = int(video_stream['height'])
    except:
        print("Error: Probe failed.")
        return None

    inp = ffmpeg.input(input_file)
    audio_stream = inp.audio
    
    # Define Layout Graph
    if face_center_x is not None:
        # Neural Split-Stacking
        print(f"[*] Neural lock engaged at X: {face_center_x:.2f}")
        
        # Top: Full Width Scaled
        top_part = inp.filter('scale', 1080, -1).filter('pad', 1080, 960, 0, '(oh-ih)/2', color='black')
        
        # Bottom: Face Crop
        crop_size = min(width, height)
        c_x = int(face_center_x * width)
        x1 = max(0, c_x - crop_size // 2)
        if x1 + crop_size > width: x1 = width - crop_size
        
        bottom_part = (
            inp
            .crop(x1, 0, crop_size, height)
            .filter('scale', 1080, 960, force_original_aspect_ratio='increase')
            .filter('crop', 1080, 960)
        )
        stacked = ffmpeg.filter([top_part, bottom_part], 'vstack')
    else:
        # Cinematic Fit Fallback
        print(f"[*] No lifeform detected. Switching to Cinematic Fit.")
        bg = inp.filter('scale', 1080, 1920, force_original_aspect_ratio='increase').filter('crop', 1080, 1920).filter('boxblur', 20)
        fg = inp.filter('scale', 1080, -1)
        stacked = ffmpeg.filter([bg, fg], 'overlay', '(W-w)/2', '(H-h)/2')

    # --- 3. Subtitle Fusion (Filter Chaining) ---
    final_video = stacked
    if has_subtitles:
        # Style: Font=12 (Small), Align=2 (Bottom), MarginV=50
        style_str = "FontName=Arial,FontSize=12,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=1,MarginV=50,Alignment=2,Bold=1"
        
        # FIX: Use basename logic (Relative Path)
        # Assuming we are running in the same dir as the file
        srt_basename = os.path.basename(temp_srt)
        final_video = stacked.filter('subtitles', srt_basename, force_style=style_str)

    # --- 4. Turbo Output ---
    print(f"[*] Velocity maximized. Rendering in Superfast mode.")
    try:
        (
            ffmpeg
            .output(
                 final_video,
                 audio_stream,
                 output_file,
                 vcodec='libx264',
                 preset='superfast', # TURBO
                 crf=25,             # TURBO
                 acodec='aac',
                 audio_bitrate='128k' # TURBO
            )
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        print(f"[*] Mission Complete. Artifact: {output_file}")
    except ffmpeg.Error as e:
        print(f"Error: Turbo render failed.")
        try: print(e.stderr.decode())
        except: pass
        return None
    finally:
        if os.path.exists(temp_srt): os.remove(temp_srt)

    return output_file

def grav_warp_format(input_file, output_file="portrait_clip.mp4"):
    # Backward compatibility wrapper: Runs Turbo mode without AI (model_size=None)
    # This ensures old calls still get the benefit of Neural Layout + Turbo Encoding
    return grav_warp_and_subtitle_combo(input_file, output_file, model_size=None)

def levitate_subtitles(video_path, output_path, model_size="small"):
    # Backward compatibility wrapper - Since logic is merged, just return path or print warning
    print("[*] Subtitles are now handled in the main Turbo pass.")
    return video_path
