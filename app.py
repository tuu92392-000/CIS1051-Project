import streamlit as st
import os
import random
import numpy as np
from pydub import AudioSegment
import io

# --- UNIVERSAL FREQUENCY SCANNER ---

def scan_and_isolate_stems(audio):
    """
    Scans the frequency spectrum in iterations and groups active ranges 
    into dynamic 'instrument' lists.
    """
    st.write("📡 Scanning frequency spectrum for active instruments...")
    
    # We define our 'search zones' in Hz
    # Using a logarithmic-style scale since music is perceived that way
    zones = [
        (20, 150, "Sub/Bass"),
        (150, 400, "Low-Mid/Body"),
        (400, 800, "Mids/Guitars"),
        (800, 2000, "High-Mids/Vocals"),
        (2000, 5000, "Presence/Synths"),
        (5000, 12000, "Brilliance/Hats"),
        (12000, 20000, "Air")
    ]
    
    active_stems = []
    
    for low, high, label in zones:
        # Filter the audio to this specific range
        stem = audio.high_pass_filter(low).low_pass_filter(high)
        
        # Check if there is actually 'sound' here (Risk management for empty bins)
        if stem.rms > (audio.rms * 0.1): # Only keep if it has at least 10% of total energy
            active_stems.append({"label": label, "audio": stem, "range": (low, high)})
            
    return active_stems

def detect_vocal_phrases(audio):
    from pydub.silence import split_on_silence
    # Isolate the vocal range specifically and try to suppress side frequencies
    vocal_focus = audio.high_pass_filter(350).low_pass_filter(3000)
    
    # Advanced: Use a slight volume reduction on 'center' to help isolation
    # (Approximating a center-channel extractor)
    chunks = split_on_silence(
        vocal_focus, 
        min_silence_len=400,
        silence_thresh=-35,
        keep_silence=150
    )
    return [c for c in chunks if len(c) > 1000]

def create_universal_remix(uploaded_file, genre="House"):
    # 1. LOAD
    file_bytes = uploaded_file.read()
    audio = AudioSegment.from_file(io.BytesIO(file_bytes), format="mp3")
    
    # 2. DYNAMIC STEMMING
    all_stems = scan_and_isolate_stems(audio)
    vocal_hooks = detect_vocal_phrases(audio)
    
    # Settings
    bpm = 126 if genre == "House" else 142
    beat_ms = int(60000 / bpm)
    bar_ms = beat_ms * 4
    total_bars = 80 # Approx 2.5 - 3 minutes
    
    # Categorize detected stems
    percussion_stems = [s['audio'] for s in all_stems if s['range'][0] < 300]
    mid_stems = [s['audio'] for s in all_stems if 300 <= s['range'][0] < 4000]
    high_stems = [s['audio'] for s in all_stems if s['range'][0] >= 4000]

    remix = AudioSegment.empty()
    st.write(f"🎹 Remixing {len(all_stems)} identified frequency layers into {genre}...")

    for bar in range(total_bars):
        bar_content = AudioSegment.silent(duration=bar_ms)
        
        # A. PERCUSSION (Lowest detected frequency bin)
        if percussion_stems:
            kick_src = percussion_stems[0] # Grab the deepest found layer
            kick = kick_src[:150].compress_dynamic_range() + (10 if genre == "House" else 14)
            for b in range(4):
                bar_content = bar_content.overlay(kick, position=b * beat_ms)

        # B. RHYTHMIC INSTRUMENTS (Iterate through mid-frequency bins)
        if bar > 4:
            # We cycle through detected 'instruments' every 4 bars
            stem_idx = (bar // 4) % len(mid_stems) if mid_stems else 0
            if mid_stems:
                current_mid = mid_stems[stem_idx]
                m_slice = current_mid[bar*bar_ms : (bar+1)*bar_ms]
                if len(m_slice) < bar_ms: m_slice = current_mid[:bar_ms]
                
                bar_content = bar_content.overlay(m_slice.fade_in(50).fade_out(50) - 4)

        # C. GENRE-SPECIFIC HI-HATS (Highest detected bin)
        if high_stems:
            hat_src = high_stems[-1] # The highest 'Air' or 'Brilliance' bin
            if genre == "Techno" or bar % 2 != 0:
                hat = hat_src[500:600].fade_in(10).fade_out(10) + 2
                pos = (beat_ms // 4) if genre == "Techno" else (beat_ms // 2)
                for b in range(16 if genre == "Techno" else 4):
                    bar_content = bar_content.overlay(hat, position=b * pos)

        # D. VOCALS (Phrase-based hooks)
        if (bar // 8) % 2 != 0 and vocal_hooks:
            hook = random.choice(vocal_hooks)
            # Center and smooth the phrase
            bar_content = bar_content.overlay(hook.fade_in(200).fade_out(200) + 3)

        remix += bar_content.compress_dynamic_range()

    # 5. EXPORT
    remix = remix.fade_out(4000)
    out_buffer = io.BytesIO()
    remix.export(out_buffer, format="mp3", bitrate="192k")
    out_buffer.seek(0)
    return out_buffer

# --- UI ---
st.set_page_config(page_title="Universal AI Remixer", page_icon="🎸")
st.title("🎸 Universal AI Remix Engine")
st.caption("Double Major MIS & Risk Management: Multi-Band Frequency Scanner")

genre_mode = st.radio("Style:", ["House", "Techno"], horizontal=True)
uploaded_file = st.file_uploader("Upload any song (Rock, Pop, etc.)", type=["mp3"])

if uploaded_file:
    if st.button(f"Generate {genre_mode} Remix"):
        with st.spinner("Scanning frequencies and aligning stems..."):
            try:
                uploaded_file.seek(0)
                final_audio = create_universal_remix(uploaded_file, genre=genre_mode)
                st.success("✅ Successfully Remixed!")
                st.audio(final_audio, format="audio/mp3")
                st.download_button("Download Remix", data=final_audio, file_name="ai_remix.mp3")
            except Exception as e:
                st.error(f"Error: {e}")
