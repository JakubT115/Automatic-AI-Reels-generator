import sys
import os

# Dodanie ścieżki do głównego folderu projektu, aby importy działały
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from youtube_extractor.downloader import download_audio
from core_logic.transcriber import transcribe_audio
from videos_maker.video_maker import create_video_with_subtitles

def main():
    print("=== GENERATOR TIKTOKÓW Z AI ===")
    
    # 1. Interaktywna konfiguracja
    youtube_url = input("🎬 Wklej link do filmu na YouTube: ").strip()
    background_video = input("📂 Wklej ścieżkę do wideo w tle: ").strip()
    
    # NOWE: Pytanie o nazwę pliku wyjściowego
    output_name = input("💾 Podaj nazwę pliku wyjściowego (np. moj_film): ").strip()
    
    # Automatyczne dodawanie rozszerzenia .mp4, jeśli użytkownik go nie podał
    if not output_name.lower().endswith(".mp4"):
        output_name += ".mp4"
    
    # Zabezpieczenie ścieżki tła
    if not os.path.exists(background_video):
        print(f"\n❌ BŁĄD: Nie znaleziono pliku wideo pod ścieżką: '{background_video}'")
        return 
    
    # 2. Pobieranie audio
    print("\n--- ETAP 1: Pobieranie audio ---")
    audio_path = download_audio(youtube_url)
    
    # 3. Transkrypcja
    print("\n--- ETAP 2: Transkrypcja Whisperem (large-v3) ---")
    result = transcribe_audio(audio_path)
    
    segments = result["segments"] 
    
    # 4. Generowanie Wideo
    print(f"\n--- ETAP 3: Generowanie Wideo ({output_name}) ---")
    create_video_with_subtitles(
        audio_path=audio_path,
        background_video_path=background_video,
        segments=segments,
        output_filename=output_name # Używamy nazwy podanej przez użytkownika
    )
    
    print(f"\n✅ Gotowe! Twój film został zapisany jako: {output_name}")

if __name__ == "__main__":
    main()