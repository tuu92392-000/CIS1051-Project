import streamlit as st
import numpy as np
from pydub import AudioSegment
from pydub.effects import compress_dynamic_range
import io
import random

# --- HARMONIC-STYLE UTILITIES ---

def create_rhythmic_chop(segment, duration_ms, repeats):
    """
    Takes a tiny slice and repeats it to create a 'synth' rhythm.
    This is what makes it sound like a real House remix.
    """
    if len(segment) < duration_ms:
        return segment
    chop = segment[:duration_ms].fade_in(10).fade_out(10)
    return chop * repeats

def apply_club_warmth(segment):
    """Adds 'Grit' and 'Saturation' by compressing and boosting gain."""
    return compress_dynamic_range(segment) + 2

# --- THE ENGINE ---

def create_club_ready_remix(uploaded_file, genre):
    with st.status(f"🎹 Booting Club Engine: {genre} Mode...", expanded=True) as status:
        file_bytes = uploaded_file.read()
        audio = AudioSegment.from_file(io.BytesIO(file_bytes), format="mp3")
        
        # Timing
        bpm = {"House": 124, "Techno": 140, "Dubstep": 140}[genre]
        beat_ms = int(60000 / bpm)
        bar_ms = beat_ms * 4
        
        # 1. BAND-PASS SCANNING (Simulating Stems)
        status.update(label="🔬 Isolating Harmonic Layers...")
        vocals = audio.high_pass_filter(350).low_pass_filter(3000)
        bass = audio.low_pass_filter(150)
        instr = audio.high_pass_filter(300).low_pass_filter(5000)
        highs = audio.high_pass_filter(5000)

        remix = AudioSegment.empty()
        
        for bar in range(64):
            bar_content = AudioSegment.silent(duration=bar_ms)
            
            # LAYER A: THE BEAT (Saturated Kick)
            # We use the bass frequency for the 'thump'
            kick = bass[:150].compress_dynamic_range() + 15
            if genre == "Dubstep":
                bar_content = bar_content.overlay(kick, position=0)
                snare = highs[500:700] + 12
                bar_content = bar_content.overlay(snare, position=beat_ms * 2)
            else:
                for b in range(4):
                    bar_content = bar_content.overlay(kick, position=b * beat_ms)

            # LAYER B: RHYTHMIC CHOPPING (The 'House' Sound)
            # Take a 1/2 beat slice and repeat it 8 times across the bar
            i_start = random.randint(0, len(instr) - beat_ms)
            chop_len = beat_ms // 2
            mid_chop = create_rhythmic_chop(instr[i_start:], chop_len, 8)
            bar_content = bar_content.overlay(mid_chop - 5)

            # LAYER C: HIGH-PASS SPARKLE
            if bar % 2 == 0:
                h_start = random.randint(0, len(highs) - (beat_ms // 4))
                sparkle = create_rhythmic_chop(highs[h_start:], beat_ms // 4, 16)
                bar_content = bar_content.overlay(sparkle - 8)

            # LAYER D: SMOOTH VOCAL PHRASES
            # Instead of constant vocals, we drop them in 8-bar intervals
            if (bar // 8) % 2 != 0:
                v_start = random.randint(0, len(vocals) - bar_ms)
                v_slice = vocals[v_start : v_start + bar_ms].fade_in(200).fade_out(200)
                bar_content = bar_content.overlay(v_slice + 3)

            # LAYER E: CLUB WARMTH (Saturation)
            remix += apply_club_warmth(bar_content)

        status.update(label="✅ Remix Mastered!", state="complete")
        
    out_buffer = io.BytesIO()
    remix.export(out_buffer, format="mp3", bitrate="192k")
    out_buffer.seek(0)
    return out_buffer

# --- UI ---
st.title("🎧 Club-Ready Remix Engine")
genre = st.selectbox("Style:", ["House", "Techno", "Dubstep"])
file = st.file_uploader("MP3", type=["mp3"])

if file:
    if st.button("🚀 Generate"):
        file.seek(0)
        out = create_club_ready_remix(file, genre)
        st.audio(out)
