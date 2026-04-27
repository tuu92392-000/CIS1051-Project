import streamlit as st
import os
import random
import numpy as np
from pydub import AudioSegment
import io

# --- ENHANCED AUDIO UTILITIES ---

def get_energy(segment):
    """Returns the RMS energy of a pydub segment."""
    return segment.rms

def detect_phrases(audio, min_silence_len=300, silence_thresh=-40):
    """
    Groups audio into phrases rather than raw chops.
    Looks for segments bounded by relative silence.
    """
    from pydub.silence import split_on_silence
    # We use a higher silence threshold to find 'vocal gaps'
    chunks = split_on_silence(
        audio, 
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        keep_silence=100
    )
    return chunks if chunks else [audio]

def create_remix(uploaded_file, genre="House"):
    # 1. LOAD & ANALYZE
    file_bytes = uploaded_file.read()
    audio = AudioSegment.from_file(io.BytesIO(file_bytes), format="mp3")
    
    # Genre-Specific Settings
    if genre == "House":
        bpm = 126
        total_bars = 64  # ~2 minutes
        bass_boost = 6
    else: # Techno
        bpm = 140
        total_bars = 96  # ~2:45 minutes
        bass_boost = 12
    
    beat_ms = int(60000 / bpm)
    bar_ms = beat_ms * 4

    # 2. DYNAMIC INSTRUMENT ISOLATION
    # We split the frequency spectrum into 'bins' to simulate multiple tracks
    # High-end/Risk-Controlled Approach: Dynamically create stems based on energy
    st.write(f"🔍 Analyzing {genre} structure...")
    
    # Virtual Stemming via band-pass filters
    stems = {
        "sub_bass": audio.low_pass_filter(100),
        "kick_punch": audio.high_pass_filter(100).low_pass_filter(250),
        "mids_low": audio.high_pass_filter(250).low_pass_filter(800),
        "mids_high": audio.high_pass_filter(800).low_pass_filter(3000),
        "high_perc": audio.high_pass_filter(5000)
    }
    
    # VOCAL PHRASE DETECTION (AI-simulated phrase grouping)
    vocal_source = audio.high_pass_filter(300).low_pass_filter(3500)
    phrases = detect_phrases(vocal_source)
    # Filter for 'significant' phrases (length check)
    vocal_hooks = [p for p in phrases if len(p) > 800 and len(p) < 5000]

    # 3. THE ARRANGEMENT ENGINE
    remix = AudioSegment.empty()
    st.write(f"🎹 Generating {total_bars} bars of {genre}...")

    for bar in range(total_bars):
        bar_content = AudioSegment.silent(duration=bar_ms)
        
        # A. FOUNDATION: THE KICK
        kick = stems["sub_bass"][:120].compress_dynamic_range() + bass_boost
        for b in range(4):
            bar_content = bar_content.overlay(kick, position=b * beat_ms)

        # B. GENRE-SPECIFIC PERCUSSION
        if genre == "Techno":
            # Driving 16th note high-hats
            hat = stems["high_perc"][500:550] - 5
            for b in range(16):
                bar_content = bar_content.overlay(hat, position=b * (beat_ms // 4))
        else:
            # Classic House Off-beat hat
            if bar % 2 == 0:
                hat = stems["high_perc"][1000:1150].fade_in(20).fade_out(20)
                for b in range(4):
                    bar_content = bar_content.overlay(hat, position=(b * beat_ms) + (beat_ms // 2))

        # C. DYNAMIC INSTRUMENTAL LAYERING
        # Every 4-8 bars, we 'introduce' or 'remove' an instrument group
        active_stems = []
        if bar > 8: active_stems.append("mids_low")
        if bar > 16: active_stems.append("mids_high")
        
        for stem_name in active_stems:
            s_start = (bar * bar_ms) % len(stems[stem_name])
            s_slice = stems[stem_name][s_start : s_start + bar_ms]
            # Smooth the mix with crossfades
            bar_content = bar_content.overlay(s_slice.fade_in(100).fade_out(100) - 3)

        # D. VOCAL PHRASES (Complete sentences, not chops)
        # Arrangement: Vocals drop in every 16 bars for a "Chorus" effect
        if (bar // 8) % 4 == 2 and vocal_hooks:
            hook = random.choice(vocal_hooks)
            # Center the hook in the 8-bar phrase
            bar_content = bar_content.overlay(hook.fade_in(200).fade_out(200) + 2)

        # E. SMOOTHING (Saturation & Compression)
        remix += bar_content.compress_dynamic_range()

    # 4. FINAL POLISH
    remix = remix.fade_in(bar_ms * 2).fade_out(bar_ms * 4)
    out_buffer = io.BytesIO()
    remix.export(out_buffer, format="mp3", bitrate="192k")
    out_buffer.seek(0)
    return out_buffer

# --- UI INTERFACE ---
st.set_page_config(page_title="AI Remix Station", page_icon="🎚️")
st.title("🎚️ AI Pro Remix Engine")
st.caption("Advanced MIS Audio Processing: Dynamic Stemming & Phrase Detection")

# Toggle for Genre
genre_mode = st.radio("Select Remix Style:", ["House", "Techno"], horizontal=True)

uploaded_file = st.file_uploader("Upload your track", type=["mp3"])

if uploaded_file:
    if st.button(f"🚀 Create {genre_mode} Remix"):
        with st.spinner(f"Processing audio for {genre_mode} arrangement..."):
            try:
                uploaded_file.seek(0)
                final_audio = create_remix(uploaded_file, genre=genre_mode)
                st.success("✅ Mixdown Complete!")
                st.audio(final_audio, format="audio/mp3")
                st.download_button("Download HQ MP3", data=final_audio, file_name=f"{genre_mode}_remix.mp3")
            except Exception as e:
                st.error(f"Mixing Error: {e}")
