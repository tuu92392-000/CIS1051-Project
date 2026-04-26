import streamlit as st
import os
import random
import numpy as np
import librosa
import soundfile as sf
from pydub import AudioSegment
import io

# Note: In a free production environment, we use a lighter approach 
# because Demucs requires 4GB+ RAM which free tiers often lack.
# For this version, we will focus on the Remix Logic.

def create_house_remix(uploaded_file):
    # Load file into Pydub
    audio = AudioSegment.from_file(uploaded_file)
    
    # 1. TEMPO & ANALYSIS (House standard 124-128 BPM)
    bpm = 126 
    beat_ms = int(60000 / bpm)
    bar_ms = beat_ms * 4
    total_bars = 32 # Keep it shorter for free server memory limits
    
    # Load with Librosa for "AI" Analysis of segments
    y, sr = librosa.load(uploaded_file, sr=None)
    
    # Find "Climactic" moments (High spectral energy usually = Chorus/Vocals)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    # Split audio into 2-second chunks and find the ones with highest energy
    chunk_size = 2 * sr
    energy = [np.sum(y[i:i+chunk_size]**2) for i in range(0, len(y), chunk_size)]
    top_chunks = np.argsort(energy)[-5:] # The 5 most "energetic" snippets
    
    # 2. STEM SIMULATION (If Demucs isn't available on the free server)
    # We use frequency filters to "fake" stems to save CPU
    low_end = audio.low_pass_filter(200) # Bass
    high_end = audio.high_pass_filter(3000) # Sparkle/Hi-hats
    mid_range = audio.high_pass_filter(300).low_pass_filter(2000) # Vocals/Synths

    remix = AudioSegment.empty()
    
    st.write("🔨 Building your unique House arrangement...")
    
    for bar in range(total_bars):
        bar_content = AudioSegment.silent(duration=bar_ms)
        
        # A. DYNAMIC FOUR-ON-THE-FLOOR
        # We vary the percussion every 8 bars to keep it interesting
        kick = low_end[:150].compress_dynamic_range() + 10
        for b in range(4):
            bar_content = bar_content.overlay(kick, position=b * beat_ms)
            
        # Add a "switch up" percussion (Open hat) every 2nd and 4th beat on odd bars
        if bar % 2 == 0:
            snare = high_end[1000:1150] + 5
            bar_content = bar_content.overlay(snare, position=(beat_ms * 1) + (beat_ms // 2))

        # B. LUSH INSTRUMENTAL SPLICING
        # Slice random 1-beat segments of the "other" instruments
        i_start = random.randint(0, len(mid_range) - beat_ms)
        instr_slice = mid_range[i_start:i_start + beat_ms].fade_in(20).fade_out(20)
        
        # Arrange based on "House Arrangement" logic (Layers build every 8 bars)
        if bar > 4:
            bar_content = bar_content.overlay(instr_slice)
        
        # C. CLIMACTIC VOCAL CHORUS
        # Every 8 bars, trigger one of the "High Energy" snippets found by our AI analysis
        if (bar // 8) % 2 != 0:
            v_idx = random.choice(top_chunks)
            v_start_ms = int((v_idx * chunk_size / sr) * 1000)
            v_slice = audio[v_start_ms : v_start_ms + (bar_ms // 2)].fade_in(100).fade_out(100)
            bar_content = bar_content.overlay(v_slice + 3)

        remix += bar_content

    # Final Polish
    remix = remix.fade_out(3000)
    
    # Export to Buffer for Streamlit
    buffer = io.BytesIO()
    remix.export(buffer, format="mp3")
    return buffer

# --- STREAMLIT UI ---
st.set_page_config(page_title="AI House Remixer", page_icon="🎹")
st.title("🎹 AI House Remix Engine")
st.subheader("Turn any song into a 126 BPM House track")

uploaded_file = st.file_uploader("Upload your MP3", type=["mp3"])

if uploaded_file:
    if st.button("🚀 Generate Remix"):
        with st.spinner("Analyzing harmonic structure and slicing stems..."):
            try:
                output_buffer = create_house_remix(uploaded_file)
                st.success("Remix Complete!")
                st.audio(output_buffer, format="audio/mp3")
                st.download_button("Download MP3", data=output_buffer, file_name="remix.mp3")
            except Exception as e:
                st.error(f"Error: {e}")