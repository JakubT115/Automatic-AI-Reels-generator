import sys
import os
import torch
import PIL.Image
import glob
import re
from moviepy.editor import AudioFileClip, concatenate_audioclips
import ollama

# 1. PATHS AND SYSTEM CONFIGURATION
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Pillow API fix
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
    print("\n🚀 === AUTO GENERATED PODCAST === 🚀")

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

    # Select Voices
    voices_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "voices")
    available_voices = [os.path.basename(f) for f in glob.glob(os.path.join(voices_dir, "*.wav"))]
    
    if len(available_voices) < 2:
        print(f"❌ Error: Need at least 2 .wav files in {voices_dir}!")
        return
        
    print("\n🎤 Available voices:")
    for idx, v in enumerate(available_voices):
        print(f"[{idx}] {v}")
        
    v1_idx = int(input("👉 Select index for Person 1 (Host): ").strip())
    v2_idx = int(input("👉 Select index for Person 2 (Guest): ").strip())
    
    v1_file = os.path.join(voices_dir, available_voices[v1_idx])
    v2_file = os.path.join(voices_dir, available_voices[v2_idx])
    
    # Extract names from file names without extension
    name_1 = os.path.splitext(available_voices[v1_idx])[0]
    name_2 = os.path.splitext(available_voices[v2_idx])[0]

    print(f"\n🎙️ Person 1: {name_1}")
    print(f"🎙️ Person 2: {name_2}")

    # Path settings
    AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "audio")
    TEMP_DIR = os.path.join(AUDIO_DIR, "temp_podcast")
    FINAL_VOICE_OUT = os.path.join(AUDIO_DIR, "final_podcast.wav")
    FINAL_VIDEO = "auto_generated_podcast.mp4"

    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)

    # Clean TEMP_DIR if there's any old files
    for old_f in glob.glob(os.path.join(TEMP_DIR, "*.wav")):
        try:
            os.remove(old_f)
        except:
            pass

    # --- STEP 1: DOWNLOADING FROM YT ---
    print("\n[1/6] Downloading audio from YouTube...")
    sciezka_mp3 = download_audio(yt_url, os.path.join(AUDIO_DIR, "yt_download_podcast"))
    
    if not sciezka_mp3 or not os.path.exists(sciezka_mp3):
        print("❌ Error: Could not find the downloaded audio file.")
        return

    # --- STEP 2: ORIGINAL TRANSCRIPTION ---
    print("\n[2/6] Transcribing original audio (Model: Large)...")
    scenariusz = transcribe_audio(sciezka_mp3, return_segments=False, model_size="large-v3", language=lang_input)
    print(f"📝 Original transcription completed (length: {len(scenariusz)} characters).")

    # --- STEP 3: LLM PODCAST SCRIPT GENERATION ---
    print(f"\n[3/6] Generating podcast script using LLM...")
    prompt = f"""
Jesteś doświadczonym scenarzystą i ekspertem od tworzenia angażujących podcastów. Twoim zadaniem jest przekształcenie poniższego transkryptu wideo w naturalną, płynną i ciekawą rozmowę dwóch osób.

Zasady, których musisz bezwzględnie przestrzegać:
1. Format TTS: Podział na role musi być idealnie czysty. Używaj wyłącznie formatu "Imię: Tekst". Nie dodawaj żadnych didaskaliów, opisów emocji, nawiasów z akcjami ani wstępów/zakończeń od siebie. Ten tekst trafi bezpośrednio do generatora mowy.
2. Imiona: Rozmówcy to {name_1} (prowadzący/ekspert) oraz {name_2} (ciekawski słuchacz/współprowadzący).
3. Przywitanie: Rozpocznij od naturalnego przywitania z użyciem obu imion i krótkiego zapowiedzenia tematu.
4. Treść: Sparafrazuj oryginalny transkrypt. Nie kopiuj go 1:1. Rozmowa ma być dynamiczna – niech postaci zadają sobie pytania, dopowiadają, zgadzają się ze sobą lub drążą temat. Zachowaj wszystkie kluczowe informacje merytoryczne z oryginału.
5. Styl: Rozmowa ma brzmieć jak naturalny, nowoczesny podcast. Używaj języka mówionego.

Oczekiwany format:
{name_1}: [Tekst do przeczytania]
{name_2}: [Tekst do przeczytania]

Oto transkrypt do przetworzenia:
{scenariusz}
"""
    try:
        response = ollama.chat(model="llama3", messages=[{'role': 'user', 'content': prompt}])
        script_text = response['message']['content']
        print("✅ Podcast script generated successfully.")
    except Exception as e:
        print(f"❌ Error communicating with Ollama: {e}")
        return

    # --- STEP 4: VOICE GENERATION FOR EACH LINE ---
    print("\n[4/6] Generating TTS voice for each participant line...")
    lines = script_text.strip().split('\n')
    audio_clips = []
    
    generate_idx = 0
    for line_idx, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # Parse "Name: Text"
        match = re.match(r'^([^:]+):(.*)$', line)
        if not match:
            # Fallback if model behaves weirdly
            continue
            
        speaker = match.group(1).strip()
        text = match.group(2).strip()
        
        if not text:
            continue

        if speaker.lower() == name_1.lower():
            speaker_wav = v1_file
        elif speaker.lower() == name_2.lower():
            speaker_wav = v2_file
        else:
            # If the model hallucinates a third name, ignore or pick default
            speaker_wav = v1_file

        part_path = os.path.join(TEMP_DIR, f"part_{generate_idx:04d}.wav")
        print(f"   -> [{generate_idx+1}] Generating for {speaker}: {text[:30]}...")
        
        success = generate_voice(text, speaker_wav=speaker_wav, output_path=part_path, language=lang_input)
        if success and os.path.exists(part_path):
            audio_clips.append(AudioFileClip(part_path))
            generate_idx += 1
        else:
            print(f"      ❌ Failed to generate voice for line {generate_idx}")

    if not audio_clips:
        print("❌ Error: No valid voice lines generated.")
        return

    # Combine all parts
    print(f"\n[5/6] Concatenating {len(audio_clips)} audio segments...")
    final_audio = concatenate_audioclips(audio_clips)
    final_audio.write_audiofile(FINAL_VOICE_OUT, fps=44100, logger=None)
    
    # Close clips to free memory
    for clip in audio_clips:
        clip.close()
    final_audio.close()

    # --- STEP 6: TRANSCRIPTION (SYNC) & VIDEO ASSEMBLY ---
    print("\n[6/6] Analyzing final podcast segments for subtitles...")
    segments = transcribe_audio(FINAL_VOICE_OUT, return_segments=True, model_size="turbo", language=lang_input)

    print("\n[6/6] Assembling everything (60FPS engine)...")
    try:
        create_video_with_subtitles(
            audio_path=FINAL_VOICE_OUT,
            background_video_path=video_background,
            segments=segments,
            output_filename=FINAL_VIDEO
        )
        print(f"\n✨ SUCCESS! Video ready: {FINAL_VIDEO}")
    except Exception as e:
        print(f"❌ Video assembly error: {e}")

if __name__ == "__main__":
    main()
