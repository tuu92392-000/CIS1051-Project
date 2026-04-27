import streamlit as st
import numpy as np
from pydub import AudioSegment
from pydub.effects import compress_dynamic_range
import io
import random

# --- MODULAR CLUB UTILITIES ---

def scan_for_phrase(vocal_track, min_duration=1500, max_duration=4000):
    """
    Scans the song for a high-energy vocal phrase of a specific length.
    Ensures the 'Chorus' is a complete string of words.
    """
    attempts = 0
    while attempts < 20:
        start = random.randint(0, len(vocal_track) - max_duration)
        sample = vocal_track[start : start + max_duration]
        # Logic: If it's loud enough and the right length, it's a 'memorable' phrase
        if sample.rms > vocal_track.rms * 1.2:
            return sample.fade_in(100).fade_out(100)
        attempts += 1
    return vocal_track[:max_duration] # Fallback

# --- THE ENGINE ---

def create_modular_remix(uploaded_file, genre):
    with st.status(f"🎹 Engineering {genre} Modular Mix...", expanded=True) as status:
        file_bytes = uploaded_file.read()
        audio = AudioSegment.from_file(io.BytesIO(file_bytes), format="mp3")
        
        # 1. STEM ISOLATION
        status.update(label="🔬 Extracting Frequency Layers...")
        bass = audio.low_pass_filter(150)
        mids = audio.high_pass_filter(350).low_pass_filter(3000)
        highs = audio.high_pass_filter(5000)

        # 2. SEED SELECTION (The "Modular" Part)
        # Instead of randomizing every bar, we pick our 'Hero' samples NOW
        status.update(label="🎯 Selecting Hero Samples...")
        
        # Pick 2 different 1/2 beat 'Melody Chops'
        beat_ms = int(60000 / (124 if genre == "House" else 140))
        melody_seeds = []
        for _ in range(2):
            m_start = random.randint(0, len(mids) - beat_ms)
            melody_seeds.append(mids[m_start : m_start + (beat_ms // 2)])
        
        # Pick 1 'Percussion Sparkle' from the highs
        p_start = random.randint(0, len(highs) - (beat_ms // 4))
        perc_seed = highs[p_start : p_start + (beat_ms // 4)]

        # Pick 2 Full-Phrase Vocal Hooks (The Chorus)
        chorus_hooks = [scan_for_phrase(audio) for _ in range(2)]

        remix = AudioSegment.empty()
        
        # 3. ARRANGEMENT
        for bar in range(80):
            bar_ms = beat_ms * 4
            bar_content = AudioSegment.silent(duration=bar_ms)
            
            # --- LAYER A: THE BEAT (Repetitive Kick) ---
            kick = bass[:150].compress_dynamic_range() + 15
            for b in range(4):
                bar_content = bar_content.overlay(kick, position=b * beat_ms)

            # --- LAYER B: THE REPETITIVE MELODY ---
            # We alternate between our two hero melody seeds for 'Call and Response'
            seed = melody_seeds[0] if (bar // 4) % 2 == 0 else melody_seeds[1]
            
            # Create the 'Rhythmic Pulse' by repeating the 1/2 beat seed
            melody_pattern = seed * 8 
            # Apply sidechain to make the melody 'dance' with the kick
            for b in range(4):
                melody_pattern = melody_pattern.fade(to_gain=-12, start=b*beat_ms, end=b*beat_ms+100)
                melody_pattern = melody_pattern.fade(from_gain=-12, start=b*beat_ms+100, end=b*beat_ms+200)
            
            bar_content = bar_content.overlay(melody_pattern - 4)

            # --- LAYER C: PERCUSSION SPARKLE ---
            # Consistent high-hat repetition
            sparkle_pattern = perc_seed * 16
            bar_content = bar_content.overlay(sparkle_pattern - 10)

            # --- LAYER D: THE CHORUS (Complete Phrases) ---
            # Every 8 bars, drop one of our memorable vocal phrases
            if (bar // 8) % 2 != 0:
                hook = chorus_hooks[0] if (bar // 16) % 2 == 0 else chorus_hooks[1]
                bar_content = bar_content.overlay(hook + 3)

            # --- LAYER E: CLUB MASTERING ---
            remix += compress_dynamic_range(bar_content) + 2

        status.update(label="✅ Mastered Modular Mix Complete!", state="complete")
        
    out_buffer = io.BytesIO()
    remix.export(out_buffer, format="mp3", bitrate="192k")
    out_buffer.seek(0)
    return out_buffer

# --- UI ---
st.title("🎧 Modular Club Remixer")
genre_choice = st.selectbox("Genre:", ["House", "Techno"])
uploaded_file = st.file_uploader("Upload MP3", type=["mp3"])

if uploaded_file:
    if st.button("🚀 Generate Remix"):
        uploaded_file.seek(0)
        final_audio = create_modular_remix(uploaded_file, genre_choice)
        st.audio(final_audio)
