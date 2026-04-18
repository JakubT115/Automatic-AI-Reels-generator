import os
import sys
from pydub import AudioSegment

def convert_to_xtts_format(input_path, output_path="data/moj_glos.wav"):
    """Konwertuje dźwięk z dowolnej lokalizacji na wzorzec dla AI."""
    
    # 1. Sprawdzenie czy plik w ogóle istnieje
    if not os.path.exists(input_path):
        print(f"❌ BŁĄD: Nie znaleziono pliku pod ścieżką: {input_path}")
        return False

    print(f"🛠️ Przetwarzam: {input_path}...")
    
    try:
        # 2. Tworzenie folderu data, jeśli go nie ma
        os.makedirs("data", exist_ok=True)

        # 3. Ładowanie dźwięku (obsługuje mp3, wav, m4a, ogg itd.)
        sound = AudioSegment.from_file(input_path)
        
        # 4. Optymalizacja pod XTTS (Mono, 22050Hz) - to gwarantuje najlepszy głos
        sound = sound.set_frame_rate(22050).set_channels(1)
        
        # 5. Eksport
        sound.export(output_path, format="wav")
        print(f"✅ SUKCES! Plik został przygotowany i zapisany jako: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Wystąpił błąd podczas konwersji: {e}")
        return False

def main():
    print("=== KONWERTER ŚCIEŻKI NA GŁOS LEKTORA ===")
    
    # Prosimy o ścieżkę
    path = input("\nWklej ścieżkę do pliku audio (lub przeciągnij plik tutaj): ").strip()
    
    # Mac czasami dodaje spacji na końcu lub cudzysłowów przy przeciąganiu - czyścimy to
    path = path.replace("'", "").replace('"', '').strip()

    if convert_to_xtts_format(path):
        print("\n🚀 Teraz możesz odpalić 'python core_logic/voice_over.py'!")

if __name__ == "__main__":
    main()