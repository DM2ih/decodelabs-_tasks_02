import streamlit as st
import os
import shutil
import time
from utils.video_handler import prepare_video_and_audio, slice_clip
from utils.transcriber import transcribe_audio_free
from utils.analyzer import process_full_transcript
from utils.broll import generate_b_roll_asset

st.set_page_config(page_title="Multimodal Content Engine", page_icon="🎬", layout="wide")

st.title("🎬 The Multimodal Content Engine")
st.markdown("Extract viral short-form clips and AI-driven B-roll imagery from long videos in minutes.")

# --- 1) Initialize Advanced Session State Architecture ---
if 'groq_api_key' not in st.session_state:
    st.session_state['groq_api_key'] = ''
if 'pipeline_results' not in st.session_state:
    st.session_state['pipeline_results'] = []
if 'is_processing' not in st.session_state:
    st.session_state['is_processing'] = False
if 'stop_requested' not in st.session_state:
    st.session_state['stop_requested'] = False
if 'execution_counter' not in st.session_state:
    st.session_state['execution_counter'] = 0

# --- Helper Function to Clean Cache Assets & Reset App Data ---
def clean_local_cache():
    st.session_state['pipeline_results'] = []
    st.session_state['is_processing'] = False
    st.session_state['stop_requested'] = False
    for file in os.listdir("."):
        if file.startswith("viral_clip_") or file.startswith("broll_asset_") or file in ["input_video.mp4", "extracted_audio.mp3", "temp_uploaded_video.mp4"]:
            try:
                os.remove(file)
            except Exception:
                pass

# --- 2) Sidebar Control Management Layout ---
with st.sidebar:
    st.header("🔑 Authentication")
    api_key_input = st.text_input("Enter Groq API Key:", type="password", value=st.session_state['groq_api_key'])
    if api_key_input:
        st.session_state['groq_api_key'] = api_key_input
        st.success("API Key locked in session!")
    else:
        st.warning("Please provide your API key to activate functionality.")

    st.markdown("---")
    st.header("🧹 Process Controllers")
    
    if st.session_state['is_processing']:
        if st.button("🛑 Stop Generation", type="primary", use_container_width=True, key="stop_btn"):
            st.session_state['stop_requested'] = True
            st.session_state['is_processing'] = False
            st.warning("Halting pipeline sequence...")
            st.rerun()
    else:
        if st.button("🗑️ Delete Generated Content", use_container_width=True, key="delete_btn"):
            clean_local_cache()
            st.success("Caches and interface maps purged cleanly!")
            st.rerun()

# --- 3) Handle Stop State Interruption Messages ---
if st.session_state['stop_requested']:
    st.markdown(
        """
        <div style="background-color: #FFF3CD; padding: 15px; border: 2px solid #DC3545; border-radius: 6px; margin-bottom: 25px;">
            <b style="color: #DC3545; font-size: 16px;">🛑 Generation Process Interrupted by User.</b><br>
            <span style="color: #1e1e2e;">The sequence was stopped mid-execution. You can modify your parameters below to give a new video input.</span>
        </div>
        """, 
        unsafe_allow_html=True
    )
    st.session_state['stop_requested'] = False

# Safeguard execution access rights
if not st.session_state['groq_api_key']:
    st.info("👈 Please enter your Groq API key in the sidebar menu to get started.")
else:
    # --- 4) Video Input Source Management Layer ---
    st.header("📥 Video Source Selection")
    source_type = st.radio(
        "Choose video ingestion method:", 
        ("YouTube Link", "Local File Upload"),
        key=f"source_type_{st.session_state['execution_counter']}"
    )

    video_input = None
    is_url = False

    if source_type == "YouTube Link":
        video_input = st.text_input(
            "Paste YouTube Video URL Here:", 
            placeholder="https://youtu.be/...",
            key=f"yt_input_{st.session_state['execution_counter']}"
        )
        is_url = True
    else:
        uploaded_file = st.file_uploader(
            "Upload Video File (MP4, MKV, MOV):", 
            type=["mp4", "mkv", "mov"],
            key=f"file_input_{st.session_state['execution_counter']}"
        )
        if uploaded_file:
            video_input = "temp_uploaded_video.mp4"
            with open(video_input, "wb") as f:
                f.write(uploaded_file.read())
            is_url = False

    # --- 5) Master Core Pipeline Processing Block ---
    if video_input:
        start_processing = st.button(
            "🚀 Process and Generate Shorts", 
            type="primary", 
            disabled=st.session_state['is_processing']
        )
        
        if start_processing:
            st.session_state['is_processing'] = True
            st.session_state['pipeline_results'] = []  # Reset content map
            st.rerun()

    # Create a persistent container block for rendering live output streams safely
    output_area = st.container()

    if st.session_state['is_processing']:
        try:
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Step 1: Media Setup
            status_text.text("⚡ Step 1/4: Ingesting source video track and parsing audio signals...")
            progress_bar.progress(10)
            video_file, audio_file = prepare_video_and_audio(
                video_input, 
                is_url=is_url, 
                local_video_path="input_video.mp4", 
                local_audio_path="extracted_audio.mp3"
            )

            # Step 2: Transcription Core
            status_text.text("🎙️ Step 2/4: Transcribing full-length audio with Groq Whisper...")
            progress_bar.progress(35)
            transcript_data = transcribe_audio_free(audio_file, st.session_state['groq_api_key'])

            # Step 3: Prompt Analysis
            status_text.text("🧠 Step 3/4: Analyzing timeline themes to pinpoint viral sections...")
            progress_bar.progress(60)
            analysis_results = process_full_transcript(transcript_data, st.session_state['groq_api_key'])
            clips_to_generate = analysis_results.get("clips", [])

            if not clips_to_generate:
                st.error("❌ No appropriate viral moments could be isolated.")
                st.session_state['is_processing'] = False
            else:
                status_text.text("✂️ Step 4/4: Slicing video timeline layers and building context b-roll frames.....")
                
                # --- Step 4: Live Rendering Sequence Loop ---
                for idx, clip in enumerate(clips_to_generate):
                    if st.session_state['stop_requested']:
                        break
                        
                    output_clip_name = f"viral_clip_{idx + 1}.mp4"
                    
                    # Generate Media Assets for this block
                    slice_clip(video_file, clip['start_time'], clip['end_time'], output_clip_name)
                    broll_img = generate_b_roll_asset(clip['b_roll_description'], idx + 1)
                    
                    # Package compiled subset data parameters
                    subset_packet = {
                        "headline": clip['headline'],
                        "caption": clip['caption'],
                        "start_time": clip['start_time'],
                        "end_time": clip['end_time'],
                        "video_path": output_clip_name,
                        "broll_path": broll_img,
                        "broll_prompt": clip['b_roll_description']
                    }
                    st.session_state['pipeline_results'].append(subset_packet)
                    
                    # Adjust progress tracking values
                    loop_progress = int(60 + ((idx + 1) / len(clips_to_generate) * 40))
                    progress_bar.progress(loop_progress)
                    
                    # --- LIVE IN-PLACE UI INJECTION ---
                    # Render components immediately to the active workspace area
                    with output_area:
                        st.markdown(f"---")
                        st.subheader(f"🎬 MOMENT {idx + 1}: {clip['headline']}")
                        st.info(f"**📱 Catchy Social Caption:** {clip['caption']}")
                        st.caption(f"⏱️ **Timeline Bounds:** {clip['start_time']}s — {clip['end_time']}s")
                        
                        col1, col2 = st.columns([3, 2])
                        with col1:
                            st.markdown("**▶️ Sliced Short Preview:**")
                            if os.path.exists(output_clip_name):
                                st.video(output_clip_name)
                                # Instant Video download option during runtime
                                with open(output_clip_name, "rb") as v_file:
                                    st.download_button(
                                        label=f"📥 Download Clip Video {idx + 1}",
                                        data=v_file,
                                        file_name=output_clip_name,
                                        mime="video/mp4",
                                        key=f"live_dl_video_{idx}"
                                    )
                        with col2:
                            st.markdown("**🖼️ Contextual B-Roll Frame:**")
                            if broll_img and os.listdir(".") and os.path.exists(broll_img):
                                st.image(broll_img, use_container_width=True)
                                st.code(f"Prompt: {clip['b_roll_description']}", language="text")
                                # Instant B-Roll download option during runtime
                                with open(broll_img, "rb") as img_file:
                                    st.download_button(
                                        label=f"📥 Download B-Roll Asset {idx + 1}",
                                        data=img_file,
                                        file_name=f"broll_asset_{idx + 1}.jpg",
                                        mime="image/jpeg",
                                        key=f"live_dl_broll_{idx}"
                                    )

                # Processing loop resolved completely without breaking
                st.session_state['is_processing'] = False
                st.session_state['execution_counter'] += 1
                progress_bar.progress(100)
                status_text.text("🎉 Pipeline cycle processing execution resolved.")
                st.balloons()
                st.rerun()

        except Exception as error:
            st.session_state['is_processing'] = False
            st.error(f"💥 Pipeline Execution Halted: {error}")

    # --- 6) Persistent Idle UI Rendering Block ---
    if st.session_state['pipeline_results'] and not st.session_state['is_processing']:
        with output_area:
            st.markdown("---")
            st.header("🔥 Generated Viral Outputs")
            
            for idx, clip in enumerate(st.session_state['pipeline_results']):
                st.subheader(f"🎬 MOMENT {idx + 1}: {clip['headline']}")
                st.info(f"**📱 Catchy Social Caption:** {clip['caption']}")
                st.caption(f"⏱️ **Timeline Bounds:** {clip['start_time']}s — {clip['end_time']}s")

                col1, col2 = st.columns([3, 2])
                
                with col1:
                    st.markdown("**▶️ Sliced Short Preview:**")
                    if os.path.exists(clip['video_path']):
                        st.video(clip['video_path'])
                        # Persistent Video download button
                        with open(clip['video_path'], "rb") as v_file:
                            st.download_button(
                                label=f"📥 Download Clip Video {idx + 1}",
                                data=v_file,
                                file_name=f"viral_clip_{idx + 1}.mp4",
                                mime="video/mp4",
                                key=f"idle_dl_video_{idx}_{st.session_state['execution_counter']}"
                            )
                    else:
                        st.error("Video segment file unavailable.")

                with col2:
                    st.markdown("**🖼️ Contextual B-Roll Frame:**")
                    if clip['broll_path'] and os.path.exists(clip['broll_path']):
                        st.image(clip['broll_path'], use_container_width=True)
                        st.code(f"Prompt: {clip['broll_prompt']}", language="text")
                        
                        # Persistent B-Roll download button
                        with open(clip['broll_path'], "rb") as img_file:
                            st.download_button(
                                label=f"📥 Download B-Roll Asset {idx + 1}",
                                data=img_file,
                                file_name=f"broll_asset_{idx + 1}.jpg",
                                mime="image/jpeg",
                                key=f"idle_dl_broll_{idx}_{st.session_state['execution_counter']}"
                            )
                    else:
                        st.warning("B-Roll asset image structure could not be retrieved.")
                
                st.markdown("<br><hr style='border:0; border-top: 1px dashed #444;'>", unsafe_allow_html=True)