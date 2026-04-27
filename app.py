import streamlit as st
import numpy as np
from pydub import AudioSegment
from pydub.effects import compress_dynamic_range
import io
import random

# --- PRO AUDIO UTILITIES ---

def apply_sidechain(segment, beat_ms, intensity=-12):
    """Creates the 'pumping' effect by ducking audio on every downbeat."""
    ducked = segment
    # Duck the volume for 150ms at the start of every beat where the kick hits
    for b in range(4):
        start = b * beat_ms
        ducked = ducked.fade(to_gain=intensity, start=start, end=start + 100)
        ducked = ducked.fade(from_gain=intensity, start=start + 100, end=start + 200)
    return ducked

def apply_wobble(segment, lfo_rate_ms=200):
    """Creates the signature Dubstep 'wobble' by modulating volume."""
    wobbled = AudioSegment.silent(duration=len(segment))
    for i in range(0, len(segment), lfo_rate_ms):
        chunk = segment[i : i + lfo_rate_ms]
        # Alternate volume to create the 'wub'
        vol_mod = -15 if (i // lfo_rate_ms) % 2 == 0 else 0
        wobbled = wobbled.overlay(chunk + vol_mod, position=i)
    return wobbled

def analyze_climactic_vocals(audio, num_hooks=2):
    """Identifies high-energy vocal segments to act as the 'Chorus'."""
    vocal_track = audio.high_pass_filter(400).low_pass_filter(3000)
    chunk_len = 3000 # 3-second hooks
    energies = []
    
    for i in range(0, len(vocal_track) - chunk_len, chunk_len):
        energies.append((vocal_track[i:i+chunk_len].rms, i))
    
    # Sort by energy and pick the top 'hooks'
    energies.sort(key=lambda x: x[0], reverse=True)
    top_starts = [x[1] for x in energies[:10]] # Pick from top 10 peaks
    
    hooks = []
    for _ in range(num_hooks):
        start = random.choice(top_starts)
        hooks.append(audio[start:start+chunk_len].fade_in(200).fade_out(200))
    return hooks

# --- MAIN REMIX ENGINE ---

def create_polished_remix(uploaded_file, genre):
    with st.status(f"🚀 Engineering {genre} Master...", expanded=True) as status:
        file_bytes = uploaded_file.read()
        audio = AudioSegment.from_file(io.BytesIO(file_bytes), format="mp3")
        
        # 1. SETUP GENRE PARAMETERS
        if genre == "House":
            bpm, total_bars, halftime = 126, 64, False
        elif genre == "Techno":
            bpm, total_bars, halftime = 142, 80, False
        else: # Dubstep
            bpm, total_bars, halftime = 140, 72, True # 140 bpm but 70 bpm feel
            
        beat_ms = int(60000 / bpm)
        bar_ms = beat_ms * 4
        
        # 2. SPECTRAL ISOLATION
        status.update(label="🔬 Isolating Instrumental Layers...")
        bass = audio.low_pass_filter(150).set_channels(1)
        mids = audio.high_pass_filter(300).low_pass_filter(3500)
        highs = audio.high_pass_filter(5000)
        
        # 3. CHORUS EXTRACTION
        status.update(label="🎤 Extracting High-Energy Hooks...")
        vocal_hooks = analyze_climactic_vocals(audio)

        remix = AudioSegment.empty()
        
        status.update(label=f"🎚️ Mixing {genre} Arrangement...")
        progress = st.progress(0)

        for bar in range(total_bars):
            progress.progress((bar + 1) / total_bars)
            bar_content = AudioSegment.silent(duration=bar_ms)
            
            # --- LAYER 1: THE BEAT ---
            kick = bass[:150].compress_dynamic_range() + 12
            if halftime: # Dubstep: Kick on 1, Snare-like high on 3
                bar_content = bar_content.overlay(kick, position=0)
                snare = highs[500:700] + 10
                bar_content = bar_content.overlay(snare, position=beat_ms * 2)
            else: # House/Techno: Four-on-the-floor
                for b in range(4):
                    bar_content = bar_content.overlay(kick, position=b * beat_ms)

            # --- LAYER 2: THE INSTRUMENTAL ---
            # Extract current bar logic
            m_start = (bar * bar_ms) % len(mids)
            instr_slice = mids[m_start : m_start + bar_ms]
            
            if genre == "Dubstep":
                instr_slice = apply_wobble(instr_slice)
            else:
                instr_slice = apply_sidechain(instr_slice, beat_ms)
            
            bar_content = bar_content.overlay(instr_slice - 3)

            # --- LAYER 3: THE PERCUSSION ---
            hat = highs[1000:1150] + (5 if genre != "Techno" else 8)
            if genre == "House":
                for b in range(4): # Off-beat hats
                    bar_content = bar_content.overlay(hat, position=(b * beat_ms) + (beat_ms // 2))
            elif genre == "Techno":
                for b in range(16): # 16th note drive
                    bar_content = bar_content.overlay(hat - 6, position=b * (beat_ms // 4))

            # --- LAYER 4: THE CHORUS (Vocal Logic) ---
            # Alternate between two climactic hooks every 8-16 bars
            if (bar // 8) % 2 != 0:
                hook_idx = 0 if (bar // 16) % 2 == 0 else 1
                if vocal_hooks:
                    active_hook = vocal_hooks[hook_idx]
                    # Loop the hook if it's shorter than the bar
                    bar_content = bar_content.overlay(active_hook + 3)

            # MASTERING: Prevent Clipping
            remix += compress_dynamic_range(bar_content)

        status.update(label="✨ Mastering Final Mix...", state="complete")
        
    out_buffer = io.BytesIO()
    remix.export(out_buffer, format="mp3", bitrate="192k")
    out_buffer.seek(0)
    return out_buffer

# --- STREAMLIT UI ---
st.set_page_config(page_title="AI Pro Remix Engine", page_icon="🎧")
st.title("🎧 AI Pro Remix Engine")
st.caption("Advanced Spectral Slicing | Chorus Extraction | Sidechain Compression")

genre_choice = st.selectbox("Select Genre Style:", ["House", "Techno", "Dubstep"])
uploaded_file = st.file_uploader("Upload Audio (MP3)", type=["mp3"])

if uploaded_file:
    if st.button(f"⚡ Generate {genre_choice} Remix"):
        try:
            uploaded_file.seek(0)
            final_audio = create_polished_remix(uploaded_file, genre_choice)
            st.audio(final_audio, format="audio/mp3")
            st.download_button("Download Remix", data=final_audio, file_name=f"{genre_choice.lower()}_remix.mp3")
        except Exception as e:
            st.error(f"Error: {e}")
