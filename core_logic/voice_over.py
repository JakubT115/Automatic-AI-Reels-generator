import sys
import os
import torch
import PIL.Image

# 1. PATHS AND SYSTEM CONFIGURATION
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Pillow API fix (AttributeError: ANTIALIAS)
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

# PyTorch 2.6 security fix for XTTS
try:
    from TTS.tts.configs.xtts_config import XttsConfig
    from TTS.tts.models.xtts import XttsAudioConfig
    torch.serialization.add_safe_globals([XttsConfig, XttsAudioConfig])
except ImportError:
    print("⚠️ Warning: Failed to load XTTS config to safe_globals.")

# 2. IMPORT CUSTOM MODULES
from youtube_extractor.downloader import download_audio
from core_logic.transcriber import transcribe_audio
from core_logic.voice_engine import generate_voice
from videos_maker.video_maker import create_video_with_subtitles

def main():
    print("\n🚀 === REELS GENERATOR === 🚀")

    # --- STEP 0: INPUT ---
    yt_url = input("\n🔗 Enter YouTube video link: ").strip()
    video_input = input("🎬 Drag and drop background video and press Enter: ").strip()
    video_background = video_input.replace("'", "").replace('"', '').strip()

    valid_langs = ["en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "hu", "ko", "ja", "hi"]
    while True:
        lang_input = input("🌍 Enter language code (e.g. en, pl, es): ").strip().lower()
        if lang_input in valid_langs:
            break
        print(f"❌ Invalid language code! Supported languages: {', '.join(valid_langs)}")

    if not yt_url or not os.path.exists(video_background):
        print("❌ Error: Missing link or valid background file!")
        return

    # Path settings
    GLOS_WZORZEC = "voices/peter_griffin.wav"
    AUDIO_DIR = "data/audio"
    PETER_VOICE_OUT = "data/generated_voice.wav"
    FINAL_VIDEO = "gotowy_film_petera.mp4"

    os.makedirs(AUDIO_DIR, exist_ok=True)

    # --- STEP 1: DOWNLOADING FROM YT ---
    print("\n[1/5] Downloading audio from YouTube...")
    sciezka_mp3 = download_audio(yt_url, os.path.join(AUDIO_DIR, "yt_download"))
    
    if not sciezka_mp3 or not os.path.exists(sciezka_mp3):
        print("❌ Error: Could not find the downloaded audio file.")
        return

    # --- STEP 2: ORIGINAL TRANSCRIPTION (Full text) ---
    print("\n[2/5] Transcribing original audio (Model: Large)...")
    scenariusz = transcribe_audio(sciezka_mp3, return_segments=False, model_size="large-v3", language=lang_input)
    
    print(f"📝 Generating voice for the full text (length: {len(scenariusz)} characters).")

    # --- STEP 3: VOICE GENERATION ---
    print("\n[3/5] Generating voice using TTS engine...")
    if not generate_voice(scenariusz, GLOS_WZORZEC, PETER_VOICE_OUT, language=lang_input):
        return

    # --- STEP 4: SUBTITLE TRANSCRIPTION (Sync) ---
    print("\n[4/5] Analyzing segments for subtitles...")
    # Doing this again because the generated voice might have a different tempo than the original
    segments = transcribe_audio(PETER_VOICE_OUT, return_segments=True, model_size="turbo", language=lang_input)

    # --- STEP 5: FINAL ASSEMBLY ---
    print("\n[5/5] Assembling everything (60FPS engine)...")
    try:
        create_video_with_subtitles(
            audio_path=PETER_VOICE_OUT,
            background_video_path=video_background,
            segments=segments,
            output_filename=FINAL_VIDEO
        )
        print(f"\n✨ SUCCESS! Video ready: {FINAL_VIDEO}")
    except Exception as e:
        print(f"❌ Video assembly error: {e}")

if __name__ == "__main__":
    main()