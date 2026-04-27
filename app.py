import streamlit as st
import numpy as np
from pydub import AudioSegment
from pydub.effects import compress_dynamic_range
import io
import random

# --- GLITCH ENGINE UTILITIES ---

def create_glitch_pattern(source_audio, beat_ms, rate=8):
    """
    Takes a source (vocals or mids) and turns it into a rhythmic instrument.
    Rate 8 = 1/8th notes, Rate 16 = 1/16th notes.
    """
    slice_len = beat_ms // (rate // 4)
    # Pick one 'Hero' micro-chop for this bar to keep it melodic/consistent
    start_point = random.randint(0, len(source_audio) - slice_len)
    micro_chop = source_audio[start_point : start_point + slice_len].fade_in(5).fade_out(5)
    
    # Create a rhythmic pattern (e.g., skip every 3rd note for 'groove')
    pattern = AudioSegment.empty()
    for i in range(rate):
        if random.random() > 0.2: # 80% density for that 'experimental' feel
            pattern += micro_chop
        else:
            pattern += AudioSegment.silent(duration=slice_len)
    return pattern

# --- THE FINAL ENGINE ---

def create_experimental_remix(uploaded_file, genre):
    with st.status(f"🧪 Synthesizing {genre} Glitch Master...", expanded=True) as status:
        file_bytes = uploaded_file.read()
        audio = AudioSegment.from_file(io.BytesIO(file_bytes), format="mp3")
        
        # Timing Architecture
        bpm = {"House": 120, "Techno": 160, "Dubstep": 140}[genre]
        beat_ms = int(60000 / bpm)
        bar_ms = beat_ms * 4
        
        # Stem Extraction (Frequency Focused)
        bass = audio.low_pass_filter(160)
        mids = audio.high_pass_filter(300).low_pass_filter(3500)
        vocals = audio.high_pass_filter(600).low_pass_filter(4000)
        highs = audio.high_pass_filter(6000)

        remix = AudioSegment.empty()
        
        for bar in range(80): # Extended length
            bar_content = AudioSegment.silent(duration=bar_ms)
            
            # 1. THE FOUNDATION: REPETITIVE LOUD KICK
            # This is the 'Anchor'—it never changes, ensuring a clear EDM pulse
            kick = bass[:160].compress_dynamic_range() + 16 # Extreme boost
            for b in range(4):
                bar_content = bar_content.overlay(kick, position=b * beat_ms)

            # 2. CHOPPY INSTRUMENTAL MELODY
            # We treat the mids like a rhythmic synth
            instr_glitch = create_glitch_pattern(mids, beat_ms, rate=8)
            # Sidechain the melody so it pumps with the kick
            for b in range(4):
                instr_glitch = instr_glitch.fade(to_gain=-15, start=b*beat_ms, end=b*beat_ms+120)
            
            bar_content = bar_content.overlay(instr_glitch - 2)

            # 3. VOCAL AS AN INSTRUMENT (The 'Glitch' Layer)
            # Vocals are chopped even finer (1/16th notes) for texture
            vocal_glitch = create_glitch_pattern(vocals, beat_ms, rate=16)
            bar_content = bar_content.overlay(vocal_glitch - 6)

            # 4. RANDOM PERCUSSIVE ACCENTS
            if bar % 2 == 0:
                snare_high = highs[200:350] + 8
                bar_content = bar_content.overlay(snare_high, position=beat_ms * 2)

            # 5. MASTERING: SATURATION & GLUE
            # This squashes the glitches and kick into a single 'Wall of Sound'
            remix += compress_dynamic_range(bar_content) + 3

        status.update(label="✨ Glitch Master Complete!", state="complete")
        
    out_buffer = io.BytesIO()
    remix.export(out_buffer, format="mp3", bitrate="192k")
    out_buffer.seek(0)
    return out_buffer

# --- UI ---
st.set_page_config(page_title="AI Glitch Remixer", page_icon="🧪")
st.title("🧪 AI Glitch Remix Engine")
st.caption("Double Major MIS & Corporate Risk: Granular Synthesis Logic")

style = st.selectbox("Style:", ["House", "Techno", "Dubstep"])
file = st.file_uploader("Upload Track", type=["mp3"])

if file:
    if st.button("🚀 Generate Final Master"):
        file.seek(0)
        out = create_experimental_remix(file, style)
        st.audio(out)
        st.download_button("Download Remix", out, f"{style.lower()}_glitch_remix.mp3")
