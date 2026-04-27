import streamlit as st
import os
import random
import numpy as np
import librosa
import soundfile as sf
from pydub import AudioSegment
import io

# --- CORE REMIX ENGINE ---

def create_house_remix(uploaded_file):
    # 1. ROBUST FILE LOADING
    # We read the file into bytes first to avoid "Format not recognised" errors
    file_bytes = uploaded_file.read()
    audio_data = io.BytesIO(file_bytes)
    
    # Load with Pydub (Using the IO stream)
    try:
        audio = AudioSegment.from_file(audio_data, format="mp3")
    except:
        # Fallback for different mpeg headers
        audio_data.seek(0)
        audio = AudioSegment.from_file(audio_data)

    # 2. HOUSE TIMING & ANALYSIS
    bpm = 126 
    beat_ms = int(60000 / bpm)
    bar_ms = beat_ms * 4
    total_bars = 32 
    
    # AI ANALYSIS: Find high-energy "Climactic" moments for vocals
    # We load a small portion into librosa to save RAM on free servers
    y, sr = librosa.load(io.BytesIO(file_bytes), sr=22050, duration=120) 
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
    
    # Identify high-energy segments (spectral energy peaks)
    S = np.abs(librosa.stft(y))
    energy = librosa.feature.rms(S=S)
    frames = np.argsort(energy[0])[-10:] # Top 10 most energetic moments
    climactic_times = librosa.frames_to_time(frames, sr=sr)

    # 3. STEM ISOLATION (Frequency-Based for Speed/Free Tier)
    low_end = audio.low_pass_filter(150)    # The Bass/Kick source
    mid_range = audio.high_pass_filter(200).low_pass_filter(3000) # Vocals/Synths
    high_end = audio.high_pass_filter(5000) # Percussion Sparkle

    remix = AudioSegment.empty()
    
    st.write("🕺 Rearranging instruments and aligning beats...")
    
    for bar in range(total_bars):
        bar_content = AudioSegment.silent(duration=bar_ms)
        
        # LAYER A: THE FOUR-ON-THE-FLOOR HOUSE BEAT
        # Classic house kick from the song's own low-end energy
        kick_sample = low_end[:150].compress_dynamic_range() + 12
        for b in range(4):
            bar_content = bar_content.overlay(kick_sample, position=b * beat_ms)
            
        # LAYER B: PERCURSSION SWITCH-UPS
        # Add "off-beat" hats every other bar to keep it interesting
        if bar % 2 != 0:
            hat_sample = high_end[500:650].fade_in(10).fade_out(10) + 5
            for b in range(4):
                bar_content = bar_content.overlay(hat_sample, position=(b * beat_ms) + (beat_ms // 2))

        # LAYER C: LUSH INSTRUMENTAL SPLICING
        # Splice synth/instrumental bits and rearrange
        if bar > 4:
            i_start = random.randint(0, len(mid_range) - beat_ms)
            instr_slice = mid_range[i_start : i_start + beat_ms].fade_in(50).fade_out(50)
            # Create a rhythmic "chop" pattern
            if bar % 4 == 0:
                bar_content = bar_content.overlay(instr_slice.reverse(), position=beat_ms * 2)
            else:
                bar_content = bar_content.overlay(instr_slice, position=0)

        # LAYER D: CLIMACTIC VOCAL CHORUS
        # Use our "AI" energy detection to drop a vocal hook every 8 bars
        if (bar // 8) % 2 != 0:
            v_time = random.choice(climactic_times)
            v_start_ms = int(v_time * 1000)
            v_slice = audio[v_start_ms : v_start_ms + (bar_ms // 2)]
            v_slice = v_slice.fade_in(100).fade_out(100) + 4
            bar_content = bar_content.overlay(v_slice)

        # LAYER E: COMPRESSION (The "House" Pump)
        bar_content = bar_content.compress_dynamic_range()
        remix += bar_content

    # FINAL EXPORT
    remix = remix.fade_out(3000)
    out_buffer = io.BytesIO()
    remix.export(out_buffer, format="mp3")
    out_buffer.seek(0)
    return out_buffer

# --- STREAMLIT UI ---
st.set_page_config(page_title="AI House Remixer", page_icon="🎧")
st.title("🎧 AI House Remix Engine")
st.markdown("*Automated Audio Engineering*")

uploaded_file = st.file_uploader("Upload an MP3", type=["mp3"])

if uploaded_file:
    st.audio(uploaded_file, format="audio/mp3")
    if st.button("🚀 Generate Unique House Remix"):
        with st.spinner("Analyzing spectral energy and arranging stems..."):
            try:
                # Reset file pointer for the generator
                uploaded_file.seek(0)
                final_audio = create_house_remix(uploaded_file)
                
                st.success("✅ Remix Produced Successfully!")
                st.audio(final_audio, format="audio/mp3")
                st.download_button("Download Remix", data=final_audio, file_name="house_remix.mp3")
            except Exception as e:
                st.error(f"Processing Error: {e}")
