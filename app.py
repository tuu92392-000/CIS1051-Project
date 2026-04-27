import streamlit as st
import numpy as np
from pydub import AudioSegment
from pydub.effects import compress_dynamic_range
import io
import random

# --- MUSICAL LOGIC UTILITIES ---

def get_melody_notes(segment, beat_ms):
    """
    Slices a segment into 4 distinct 'notes' (chops) 
    to be used as a melodic palette.
    """
    palette = []
    for _ in range(4):
        start = random.randint(0, len(segment) - beat_ms)
        palette.append(segment[start : start + beat_ms].fade_in(10).fade_out(10))
    return palette

def apply_sidechain(segment, beat_ms):
    """Ducks the volume on every beat to let the kick drum through."""
    ducked = segment
    for b in range(4):
        start = b * beat_ms
        ducked = ducked.fade(to_gain=-18, start=start, end=start + 120)
        ducked = ducked.fade(from_gain=-18, start=start + 120, end=start + 240)
    return ducked

# --- THE FINAL ENGINE ---

def create_layered_masterpiece(uploaded_file, genre):
    with st.status(f"🎹 Orchestrating {genre} Layers...", expanded=True) as status:
        file_bytes = uploaded_file.read()
        audio = AudioSegment.from_file(io.BytesIO(file_bytes), format="mp3")
        
        # 1. TIMING & STEMS
        bpm = {"House": 124, "Techno": 138, "Dubstep": 140}[genre]
        beat_ms = int(60000 / bpm)
        bar_ms = beat_ms * 4
        
        bass = audio.low_pass_filter(150)
        mids = audio.high_pass_filter(350).low_pass_filter(3000)
        highs = audio.high_pass_filter(5000)
        
        # 2. SEED THE MELODY (Music Theory Alignment)
        # We pick 4 distinct 'notes' from the mids to act as our instrument
        status.update(label="🎸 Extracting Melodic Palette...")
        note_palette = get_melody_notes(mids, beat_ms // 2)
        # Minor Progression Pattern (index of notes in palette)
        # Standard: i - VI - III - VII 
        melody_pattern = [0, 2, 1, 3, 0, 2, 3, 1] 

        # 3. SEED THE VOCALS
        status.update(label="🎤 Scanning for Chorus Hooks...")
        vocal_hook = audio[random.randint(0, len(audio)-bar_ms*2) :].high_pass_filter(500)[:bar_ms*2]

        remix = AudioSegment.empty()
        
        for bar in range(96): # Standard 3-minute club track
            bar_content = AudioSegment.silent(duration=bar_ms)
            
            # --- TRACK 1: THE KICK (Always Consistent) ---
            # Saturated low-end pulse
            kick = bass[:160].compress_dynamic_range() + 16
            for b in range(4):
                bar_content = bar_content.overlay(kick, position=b * beat_ms)

            # --- TRACK 2: THE LAYERED MELODY ---
            # We follow the melody_pattern across 2 bars
            bar_melody = AudioSegment.empty()
            pattern_start = (bar % 2) * 4
            for i in range(4):
                note_idx = melody_pattern[pattern_start + i]
                # Repeat the note twice for a 1/8th note house feel
                bar_melody += note_palette[note_idx] + note_palette[note_idx]
            
            # Apply sidechain so the melody 'pumps'
            bar_content = bar_content.overlay(apply_sidechain(bar_melody, beat_ms) - 4)

            # --- TRACK 3: THE RHYTHMIC GLITCH ---
            # High-pass percussion chops on the off-beats
            if bar % 2 == 0:
                h_chop = highs[100:200] * 8
                bar_content = bar_content.overlay(h_chop.fade_in(500) - 10)

            # --- TRACK 4: THE VOCAL CHORUS ---
            # Drop the vocals only in the 2nd and 4th 'blocks' of 8 bars
            if (bar // 8) % 4 in [1, 3]:
                # Chop the vocal hook into the current bar
                v_slice = vocal_hook[(bar % 2) * bar_ms : ((bar % 2) + 1) * bar_ms]
                bar_content = bar_content.overlay(v_slice - 2)

            # --- FINAL MASTERING: THE GLUE ---
            # Squash everything together to make it sound like one song
            remix += compress_dynamic_range(bar_content) + 2

        status.update(label="✨ Club Master Finalized!", state="complete")
        
    out_buffer = io.BytesIO()
    remix.export(out_buffer, format="mp3", bitrate="192k")
    out_buffer.seek(0)
    return out_buffer

# --- STREAMLIT UI ---
st.title("🎧 Multi-Track AI Remixer")
genre = st.selectbox("Style:", ["House", "Techno", "Dubstep"])
file = st.file_uploader("Upload Track", type=["mp3"])

if file:
    if st.button("🚀 Generate Final Master"):
        file.seek(0)
        out = create_layered_masterpiece(file, genre)
        st.audio(out)
