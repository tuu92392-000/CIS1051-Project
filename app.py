import streamlit as st
import numpy as np
from pydub import AudioSegment
from pydub.effects import compress_dynamic_range
import io
import random

# --- ADVANCED AUDIO UTILITIES ---

def apply_sidechain(segment, beat_ms, intensity=-14):
    """The 'pumping' effect that prevents frequency clashing."""
    ducked = segment
    for b in range(4):
        start = b * beat_ms
        ducked = ducked.fade(to_gain=intensity, start=start, end=start + 100)
        ducked = ducked.fade(from_gain=intensity, start=start + 100, end=start + 200)
    return ducked

def get_climactic_hooks(audio, num_hooks=3):
    """Finds the most energetic vocal/melodic sections for the chorus."""
    # Focus on the 'Power' frequency range (400Hz - 2500Hz)
    focus = audio.high_pass_filter(400).low_pass_filter(2500)
    chunk_ms = 4000 # 4-second phrases
    peaks = []
    
    for i in range(0, len(focus) - chunk_ms, 2000):
        peaks.append((focus[i:i+chunk_ms].rms, i))
    
    peaks.sort(key=lambda x: x[0], reverse=True)
    # Return a list of AudioSegments for the top peaks
    return [audio[p[1]:p[1]+chunk_ms].fade_in(200).fade_out(200) for p in peaks[:10]]

# --- THE REMIX ENGINE ---

def create_pro_layered_remix(uploaded_file, genre):
    with st.status(f"🏗️ Building {genre} Wall of Sound...", expanded=True) as status:
        file_bytes = uploaded_file.read()
        audio = AudioSegment.from_file(io.BytesIO(file_bytes), format="mp3")
        
        # 1. SETUP ENGINE
        if genre == "House":
            bpm, bars, halftime = 126, 64, False
        elif genre == "Techno":
            bpm, bars, halftime = 142, 80, False
        else: # Dubstep
            bpm, bars, halftime = 140, 72, True
            
        beat_ms = int(60000 / bpm)
        bar_ms = beat_ms * 4
        
        # 2. DYNAMIC INSTRUMENT SEPARATION
        status.update(label="🔬 Deep Scanning for Melodic Layers...")
        bass = audio.low_pass_filter(180)
        mids = audio.high_pass_filter(300).low_pass_filter(3000)
        highs = audio.high_pass_filter(5000)
        
        # Identify 'Melody' by finding the most energetic part of the mids
        hooks = get_climactic_hooks(audio)

        remix = AudioSegment.empty()
        progress = st.progress(0)

        for bar in range(bars):
            progress.progress((bar + 1) / bars)
            bar_content = AudioSegment.silent(duration=bar_ms)
            
            # --- LAYER 1: THE FOUNDATION (Drums) ---
            kick = bass[:160].compress_dynamic_range() + 12
            if halftime: # Dubstep
                bar_content = bar_content.overlay(kick, position=0)
                snare = highs[500:750] + 10
                bar_content = bar_content.overlay(snare, position=beat_ms * 2)
            else: # House/Techno
                for b in range(4):
                    bar_content = bar_content.overlay(kick, position=b * beat_ms)

            # --- LAYER 2: THE RHYTHMIC MELODY (Always Active) ---
            # To prevent 'bare' parts, we loop a melodic slice of the song
            m_start = (bar * bar_ms) % len(mids)
            melody_slice = mids[m_start : m_start + bar_ms]
            
            # Apply rhythmic gating to the melody
            if genre == "House":
                melody_slice = apply_sidechain(melody_slice, beat_ms)
            elif genre == "Techno":
                # Create a 1/16th note 'pulse' for techno
                melody_slice = apply_sidechain(melody_slice, beat_ms // 2, intensity=-20)
            
            bar_content = bar_content.overlay(melody_slice - 4)

            # --- LAYER 3: DYNAMIC EDM PATTERNS (Complexity) ---
            # Every 4 bars, we add a new instrument layer to build tension
            if bar % 4 >= 1:
                h_start = (bar * 500) % len(highs)
                perc_layer = highs[h_start : h_start + bar_ms]
                bar_content = bar_content.overlay(perc_layer - 10)

            # --- LAYER 4: THE VOCAL CHORUS (Memorable Hooks) ---
            # Drop the chorus every 8 bars, and alternate hooks
            if (bar // 8) % 2 != 0 and hooks:
                selected_hook = hooks[bar % len(hooks)]
                # Ensure vocal hook doesn't exceed the current bar if we want it tight
                bar_content = bar_content.overlay(selected_hook[:bar_ms] + 4)

            # --- LAYER 5: PERCUSSION FILL ---
            if bar % 2 != 0:
                hat = highs[100:250] + 6
                for b in range(4):
                    bar_content = bar_content.overlay(hat, position=(b * beat_ms) + (beat_ms // 2))

            # MASTERING: Final Glue Compression
            remix += compress_dynamic_range(bar_content)

        status.update(label="✨ Production Mastered!", state="complete")
        
    out_buffer = io.BytesIO()
    remix.export(out_buffer, format="mp3", bitrate="192k")
    out_buffer.seek(0)
    return out_buffer

# --- UI ---
st.set_page_config(page_title="AI Pro Remix Engine", page_icon="🔊")
st.title("🔊 AI Pro Remix Engine")

genre = st.selectbox("Style:", ["House", "Techno", "Dubstep"])
file = st.file_uploader("MP3 File", type=["mp3"])

if file:
    if st.button("Generate Master Remix"):
        try:
            file.seek(0)
            out = create_pro_layered_remix(file, genre)
            st.audio(out)
            st.download_button("Download", out, "remix.mp3")
        except Exception as e:
            st.error(f"Error: {e}")
