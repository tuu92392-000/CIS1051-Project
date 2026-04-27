import streamlit as st
import os
import random
import numpy as np
from pydub import AudioSegment
import io

# --- CORE REMIX ENGINE ---

def create_house_remix(uploaded_file):
    # 1. FILE LOADING
    file_bytes = uploaded_file.read()
    audio_data = io.BytesIO(file_bytes)
    
    try:
        audio = AudioSegment.from_file(audio_data, format="mp3")
    except:
        audio_data.seek(0)
        audio = AudioSegment.from_file(audio_data)

    # 2. HOUSE TIMING
    bpm = 126 
    beat_ms = int(60000 / bpm)
    bar_ms = beat_ms * 4
    total_bars = 32 
    
    # AI ENERGY ANALYSIS (Manual NumPy Implementation)
    # This replaces Librosa to fix the 'pkg_resources' error while keeping the logic
    st.write("🔍 AI Analysis: Finding climactic vocal hooks...")
    
    # Convert audio to raw data for math analysis
    samples = np.array(audio.get_array_of_samples())
    
    # Break the song into 2-second chunks to find "energy peaks"
    chunk_size = audio.frame_rate * 2
    if audio.channels == 2:
        samples = samples.reshape((-1, 2)).mean(axis=1) # Mono for analysis
        
    energy_levels = []
    for i in range(0, len(samples), chunk_size):
        chunk = samples[i:i+chunk_size]
        if len(chunk) > 0:
            rms = np.sqrt(np.mean(chunk**2)) # Calculate Root Mean Square Energy
            energy_levels.append(rms)
            
    # Find the timestamps of the top 10 most energetic/climactic moments
    top_chunk_indices = np.argsort(energy_levels)[-10:]
    climactic_times_ms = [idx * 2000 for idx in top_chunk_indices]

    # 3. STEM ISOLATION (Frequency-Based)
    st.write("🎹 Isolating frequencies for House stems...")
    low_end = audio.low_pass_filter(150)    
    mid_range = audio.high_pass_filter(250).low_pass_filter(3500) 
    high_end = audio.high_pass_filter(5000) 

    remix = AudioSegment.empty()
    
    for bar in range(total_bars):
        bar_content = AudioSegment.silent(duration=bar_ms)
        
        # A. FOUR-ON-THE-FLOOR
        kick_sample = low_end[:150].compress_dynamic_range() + 10
        for b in range(4):
            bar_content = bar_content.overlay(kick_sample, position=b * beat_ms)
            
        # B. DYNAMIC HI-HATS (Switch-up every 2nd bar)
        if bar % 2 != 0:
            hat = high_end[1000:1150].fade_in(5).fade_out(10) + 4
            for b in range(4):
                bar_content = bar_content.overlay(hat, position=(b * beat_ms) + (beat_ms // 2))

        # C. INSTRUMENTAL SPLICING
        if bar > 4:
            # Grab a random rhythmic slice of the mid-range
            i_start = random.randint(0, len(mid_range) - beat_ms)
            instr_slice = mid_range[i_start : i_start + beat_ms].fade_in(50).fade_out(50)
            bar_content = bar_content.overlay(instr_slice)

        # D. CLIMACTIC VOCAL CHORUS (Using AI-detected energy peaks)
        if (bar // 8) % 2 != 0:
            v_start_ms = random.choice(climactic_times_ms)
            # Ensure we don't grab from past the end of the song
            v_start_ms = min(v_start_ms, len(audio) - bar_ms)
            v_slice = audio[v_start_ms : v_start_ms + (bar_ms // 2)]
            bar_content = bar_content.overlay(v_slice.fade_in(150).fade_out(150) + 4)

        remix += bar_content.compress_dynamic_range()

    # FINAL EXPORT
    remix = remix.fade_out(3000)
    out_buffer = io.BytesIO()
    remix.export(out_buffer, format="mp3")
    out_buffer.seek(0)
    return out_buffer

# --- UI ---
st.set_page_config(page_title="AI House Remixer", page_icon="🎧")
st.title("🎧 AI House Remix Engine")
st.caption("Custom Built Audio Intelligence - Stabilized for Cloud Hosting")

uploaded_file = st.file_uploader("Upload your MP3", type=["mp3"])

if uploaded_file:
    if st.button("🚀 Generate House Remix"):
        with st.spinner("Analyzing spectral energy and arranging stems..."):
            try:
                uploaded_file.seek(0)
                final_audio = create_house_remix(uploaded_file)
                st.success("✅ Remix Produced!")
                st.audio(final_audio, format="audio/mp3")
                st.download_button("Download Remix", data=final_audio, file_name="house_remix.mp3")
            except Exception as e:
                st.error(f"Processing Error: {e}")
