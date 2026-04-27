import streamlit as st
import numpy as np
from pydub import AudioSegment
from pydub.effects import compress_dynamic_range
import io
import random

# --- CORE CLUB UTILITIES ---

def create_rhythmic_chop(segment, duration_ms, repeats):
    """Creates the 'stutter' effect that defines electronic music."""
    if len(segment) < duration_ms:
        return segment
    chop = segment[:duration_ms].fade_in(5).fade_out(5)
    return chop * repeats

def get_vocal_phrase(vocal_track, bar_ms):
    """Finds a energetic 1-bar phrase for the 'Chorus'."""
    start = random.randint(0, len(vocal_track) - bar_ms)
    return vocal_track[start : start + bar_ms].fade_in(100).fade_out(100)

# --- THE ENGINE ---

def create_club_remix(uploaded_file, genre):
    with st.status(f"🎹 Re-Engineering {genre} Remix...", expanded=True) as status:
        file_bytes = uploaded_file.read()
        audio = AudioSegment.from_file(io.BytesIO(file_bytes), format="mp3")
        
        # 1. GENRE PARAMETERS
        if genre == "House":
            bpm, bars, halftime = 126, 64, False
        elif genre == "Techno":
            bpm, bars, halftime = 142, 80, False
        else: # Dubstep
            bpm, bars, halftime = 140, 72, True
            
        beat_ms = int(60000 / bpm)
        bar_ms = beat_ms * 4
        
        # 2. FREQUENCY ISOLATION
        status.update(label="🔬 Isolating Harmonic Stems...")
        bass = audio.low_pass_filter(150)
        mids = audio.high_pass_filter(300).low_pass_filter(3500)
        highs = audio.high_pass_filter(5000)

        remix = AudioSegment.empty()
        
        for bar in range(bars):
            bar_content = AudioSegment.silent(duration=bar_ms)
            
            # --- LAYER A: THE BEAT (Saturated Kick) ---
            kick = bass[:160].compress_dynamic_range() + 15
            if halftime: # Dubstep
                bar_content = bar_content.overlay(kick, position=0)
                snare = highs[500:750] + 10
                bar_content = bar_content.overlay(snare, position=beat_ms * 2)
            else: # House/Techno
                for b in range(4):
                    bar_content = bar_content.overlay(kick, position=b * beat_ms)

            # --- LAYER B: RHYTHMIC INSTRUMENTAL (The Melody) ---
            # Take a 1/2 beat chop and repeat it across the bar
            i_start = random.randint(0, len(mids) - beat_ms)
            chop_rate = 8 if genre != "Dubstep" else 4
            melody_chop = create_rhythmic_chop(mids[i_start:], beat_ms // (chop_rate // 4), chop_rate)
            
            # Apply sidechain 'pumping'
            for b in range(4):
                melody_chop = melody_chop.fade(to_gain=-12, start=b*beat_ms, end=b*beat_ms+100)
                melody_chop = melody_chop.fade(from_gain=-12, start=b*beat_ms+100, end=b*beat_ms+200)
            
            bar_content = bar_content.overlay(melody_chop - 4)

            # --- LAYER C: PERCUSSION SPARKLE ---
            if bar % 2 != 0:
                h_start = random.randint(0, len(highs) - (beat_ms // 4))
                sparkle = create_rhythmic_chop(highs[h_start:], beat_ms // 4, 16)
                bar_content = bar_content.overlay(sparkle - 8)

            # --- LAYER D: THE CHORUS (Vocal Phrases) ---
            if (bar // 8) % 2 != 0:
                vocal_phrase = get_vocal_phrase(audio, bar_ms)
                bar_content = bar_content.overlay(vocal_phrase + 3)

            # --- LAYER E: FINAL SATURATION ---
            remix += compress_dynamic_range(bar_content) + 2

        status.update(label="✅ Mastered Remix Complete!", state="complete")
        
    out_buffer = io.BytesIO()
    remix.export(out_buffer, format="mp3", bitrate="192k")
    out_buffer.seek(0)
    return out_buffer

# --- UI ---
st.title("🎧 Pro Club Remixer")
genre_choice = st.selectbox("Style:", ["House", "Techno", "Dubstep"])
uploaded_file = st.file_uploader("Upload MP3", type=["mp3"])

if uploaded_file:
    if st.button("🚀 Generate Master Remix"):
        uploaded_file.seek(0)
        final_audio = create_club_remix(uploaded_file, genre_choice)
        st.audio(final_audio)
