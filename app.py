import streamlit as st
import os
import time
from graviclip_core import zero_g_download, grav_warp_format, levitate_subtitles

# --- Configuration & Styling ---
st.set_page_config(
    page_title="GraviClip: Anti-Gravity Editor",
    page_icon="🌌",
    layout="centered"
)

# Custom CSS to hide default chrome and add 'Anti-Gravity' vibes
st.markdown("""
<style>
    /* Hide Streamlit Hamburger & Footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom Title Style */
    .grav-title {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 800;
        font-size: 3rem;
        background: -webkit-linear-gradient(45deg, #FF00CC, #3333FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0;
    }
    .grav-subtitle {
        text-align: center;
        color: #888;
        font-size: 1.2rem;
        letter-spacing: 2px;
        margin-bottom: 2rem;
    }
    
    /* Button Customization (Streamlit buttons are hard to style fully via CSS injection safely, 
       but we can try to influence the primary button) */
    .stButton button {
        width: 100%;
        background-color: #3333FF !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        padding: 0.5rem 1rem !important;
        border: none !important;
        transition: all 0.3s ease !important;
    }
    .stButton button:hover {
        background-color: #FF00CC !important;
        box-shadow: 0 0 15px #FF00CC !important;
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown('<div class="grav-title">🌌 GRAVICLIP</div>', unsafe_allow_html=True)
st.markdown('<div class="grav-subtitle">ANTI-GRAVITY EDITOR // AUTOMATED TIKTOK MODULE</div>', unsafe_allow_html=True)

# --- Input Area ---
with st.container():
    url = st.text_input("YouTube Broadcast Frequency (URL)", placeholder="https://youtube.com/watch?v=...")
    
    col1, col2 = st.columns(2)
    with col1:
        start_time = st.text_input("T-Minus Start (HH:MM:SS)", value="00:00:10")
    with col2:
        end_time = st.text_input("T-Minus End (HH:MM:SS)", value="00:00:20")
        
    ai_mode = st.checkbox("Enable Levitation Subtitles (AI Mode)", value=True, help="Uses Whisper AI to transcribe and burn captions.")
    
    if ai_mode:
        model_options = {
            "Tiny (Fastest)": "tiny",
            "Base (Fast)": "base",
            "Small (Balanced)": "small",
            "Medium (High Accuracy)": "medium"
        }
        selected_model_label = st.selectbox("AI Model Accuracy", list(model_options.keys()), index=2)
        selected_model = model_options[selected_model_label]

# --- Process Logic ---
if st.button("INITIATE GRAV-DRIVE 🚀"):
    if not url:
        st.error("⚠️ Error: No frequency detected. Please input a URL.")
    else:
        # Define filenames for this session
        timestamp = int(time.time())
        clip_file = f"temp_clip_{timestamp}.mp4"
        warp_file = f"temp_warp_{timestamp}.mp4"
        final_file = f"graviclip_{timestamp}.mp4"
        
        status_box = st.status("Initializing Gravity Drive...", expanded=True)
        
        try:
            # 1. Extraction (Turbo Trim)
            status_box.write("⏬ [Phase 1] Extracting raw asset from the void (Ultrafast Mode)...")
            downloaded = zero_g_download(url, start_time, end_time, clip_file)
            
            if not downloaded:
                status_box.update(label="❌ Extraction Failed", state="error")
                st.error("Failed to download video. Check URL and timestamps.")
                st.stop()
                
            # 2. Turbo Processing (Single-Pass: Neural Warp + Subtitles)
            if ai_mode:
                status_box.write(f"🚀 [Phase 2] Activating Turbo Engine (Single-Pass Rendering)...")
                status_box.write(f"🧠 Calibrating Neural Cortex [{selected_model.upper()}]...")
                
                # Import new combo function wrapper if needed or direct
                from graviclip_core import grav_warp_and_subtitle_combo
                processed = grav_warp_and_subtitle_combo(clip_file, final_file, model_size=selected_model)
                
            else:
                # If no AI, we can use the old separate warp function or just the combo without subs?
                # But combo forces subs unless we change it.
                # Use legacy/wrapper for non-AI mode or just warp.
                # Refactored graviclip_core has wrappers.
                status_box.write("📐 [Phase 2] Warping dimensions (No AI)...")
                processed = grav_warp_format(clip_file, final_file)

            if not processed:
                status_box.update(label="❌ Turbo Engine Stalled", state="error")
                st.error("Processing failed.")
                st.stop()
            
            current_output = processed
                
            status_box.update(label="✅ Velocity Maximized. Mission Complete!", state="complete", expanded=False)
            
            # --- Result Display ---
            st.divider()
            st.success("🎉 Asset Secured!")
            
            # Video Player
            st.video(current_output)
            
            # Download Button
            with open(current_output, "rb") as file:
                btn = st.download_button(
                    label="📥 Download GraviClip",
                    data=file,
                    file_name="final_graviclip.mp4",
                    mime="video/mp4"
                )
                
            # --- Cleanup Temporary Files ---
            if os.path.exists(clip_file): os.remove(clip_file)
            
        except Exception as e:
            status_box.update(label="❌ Critical System Failure", state="error")
            st.error(f"An unexpected error occurred: {e}")
