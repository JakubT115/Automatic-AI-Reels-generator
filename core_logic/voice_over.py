import sys
import os
import torch
import PIL.Image

# 1. ŚCIEŻKI I KONFIGURACJA SYSTEMOWA
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Fix dla Pillow (AttributeError: ANTIALIAS)
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

# Kompletna poprawka bezpieczeństwa PyTorch 2.6 dla XTTS
try:
    from TTS.tts.configs.xtts_config import XttsConfig
    from TTS.tts.models.xtts import XttsAudioConfig
    torch.serialization.add_safe_globals([XttsConfig, XttsAudioConfig])
except ImportError:
    print("⚠️ Uwaga: Nie udało się załadować konfiguracji XTTS do safe_globals.")

# 2. IMPORT TWOICH MODUŁÓW
from youtube_extractor.downloader import download_audio
from core_logic.transcriber import transcribe_audio
from core_logic.voice_engine import generate_voice
from videos_maker.video_maker import create_video_with_subtitles

def main():
    print("\n🚀 === FULL AUTOMAT: YT TO TIKTOK (PETER EDITION) === 🚀")

    # --- KROK 0: WEJŚCIE ---
    yt_url = input("\n🔗 Podaj link do filmu na YouTube: ").strip()
    video_input = input("🎬 Przeciągnij wideo tło (np. Subway Surfers) i naciśnij Enter: ").strip()
    video_background = video_input.replace("'", "").replace('"', '').strip()

    if not yt_url or not os.path.exists(video_background):
        print("❌ Błąd: Brak linku lub poprawnego pliku tła!")
        return

    # Ustawienia ścieżek
    GLOS_WZORZEC = "voices/peter_griffin.wav"
    AUDIO_DIR = "data/audio"
    PETER_VOICE_OUT = "data/generated_voice.wav"
    FINAL_VIDEO = "gotowy_film_petera.mp4"

    os.makedirs(AUDIO_DIR, exist_ok=True)

    # --- KROK 1: POBIERANIE Z YT ---
    print("\n[1/5] Pobieranie dźwięku z YouTube...")
    sciezka_mp3 = download_audio(yt_url, os.path.join(AUDIO_DIR, "yt_download"))
    
    if not sciezka_mp3 or not os.path.exists(sciezka_mp3):
        print("❌ Błąd: Nie udało się odnaleźć pobranego pliku audio.")
        return

    # --- KROK 2: TRANSKRYPCJA ORYGINAŁU (Cały tekst) ---
    print("\n[2/5] Przepisuję oryginał 1:1 (Model: Large)...")
    scenariusz = transcribe_audio(sciezka_mp3, return_segments=False, model_size="large-v3")
    
    print(f"📝 Peter przeczyta pełny tekst (długość: {len(scenariusz)} znaków).")

    # --- KROK 3: GENEROWANIE GŁOSU PETERA ---
    print("\n[3/5] Peter Griffin wchodzi do studia...")
    if not generate_voice(scenariusz, GLOS_WZORZEC, PETER_VOICE_OUT):
        return

    # --- KROK 4: TRANSKRYPCJA DLA NAPISÓW (Synchronizacja) ---
    print("\n[4/5] Analiza segmentów pod napisy...")
    # Robimy to na nowo, bo Peter mówi w innym tempie niż oryginał
    segments = transcribe_audio(PETER_VOICE_OUT, return_segments=True, model_size="turbo")

    # --- KROK 5: MONTAŻ FINALNY ---
    print("\n[5/5] Składanie wszystkiego w całość (Twój silnik 60FPS)...")
    try:
        create_video_with_subtitles(
            audio_path=PETER_VOICE_OUT,
            background_video_path=video_background,
            segments=segments,
            output_filename=FINAL_VIDEO
        )
        print(f"\n✨ SUKCES! Film gotowy: {FINAL_VIDEO}")
    except Exception as e:
        print(f"❌ Błąd montażu: {e}")

if __name__ == "__main__":
    main()