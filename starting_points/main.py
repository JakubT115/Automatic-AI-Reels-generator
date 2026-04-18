import argparse
import sys
import os

# Dodanie katalogu głównego projektu do ścieżki Pythona, aby widział nowe foldery
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from youtube_extractor.downloader import download_audio
from core_logic.transcriber import transcribe_audio
from core_logic.summarizer import summarize_text

def run_pipeline(url: str = None, file_path: str = None, whisper_model: str = "base", ollama_model: str = "llama3"):
    if url:
        print("="*60)
        print(f"🎬 Rozpoczęcie ekstrakcji wiedzy dla URL: {url}")
        print("="*60)
        
        # ---------------------------------------------
        # KROK 1: POBIERANIE AUDIO
        # ---------------------------------------------
        try:
            audio_path = download_audio(url, output_dir="data")
        except Exception as e:
            print(f"[!] Błąd podczas pobierania audio: {e}")
            sys.exit(1)
            
        if not os.path.exists(audio_path):
            print(f"[!] Błąd: Plik audio nie istnieje na dysku: {audio_path}")
            sys.exit(1)
    elif file_path:
        print("="*60)
        print(f"🎬 Rozpoczęcie ekstrakcji wiedzy dla pliku lokalnego: {file_path}")
        print("="*60)
        audio_path = file_path
        if not os.path.exists(audio_path):
            print(f"[!] Błąd: Podany plik nie istnieje na dysku: {audio_path}")
            sys.exit(1)
    else:
        print("[!] Musisz podać --url albo --file.")
        sys.exit(1)
        
    # ---------------------------------------------
    # KROK 2: TRANSKRYPCJA
    # ---------------------------------------------
    try:
        result = transcribe_audio(audio_path)
        transcription = result["text"].strip()
    except Exception as e:
        print(f"[!] Błąd podczas transkrypcji: {e}")
        sys.exit(1)
    
    # Zapis oryginalnej transkrypcji w celach debugowania i backupu
    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    transcription_path = os.path.join("data", f"{base_name}_transcription.txt")
    
    with open(transcription_path, "w", encoding="utf-8") as f:
        f.write(transcription)
    print(f"[+] Surowa transkrypcja zapisana do: {transcription_path}")
    
    if not transcription.strip():
        print("[!] Transkrypcja jest pusta, przerywam pracę.")
        sys.exit(1)
        
    # ---------------------------------------------
    # KROK 3: PODSUMOWANIE (LLM)
    # ---------------------------------------------
    try:
        summary = summarize_text(transcription, model_name=ollama_model)
    except Exception as e:
        print(f"[!] Błąd podczas generowania podsumowania: {e}")
        print("Upewnij się, że lokalny serwer Ollama jest uruchomiony!")
        sys.exit(1)
    
    # Zapis gotowego podsumowania
    summary_path = os.path.join("data", f"{base_name}_summary.txt")
    
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary)
        
    # Wynik końcowy
    print("\n" + "="*60)
    print("✨ GOTOWE PODSUMOWANIE:")
    print("="*60)
    print(summary)
    print("="*60)
    print(f"\n[+] Wynik zapisano również w: {summary_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ekstraktor wiedzy z filmów na YouTube lub lokalnych plików audio.")
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", "-u", help="URL do filmu na YouTube.")
    group.add_argument("--file", "-f", help="Ścieżka do lokalnego pliku audio (np. .mp3, .wav).")
    
    parser.add_argument("--whisper", default="base", help="Model Whisper. Domyślnie base.")
    parser.add_argument("--ollama", default="llama3", help="Model Ollama do podsumowania. Domyślnie llama3.")
    
    args = parser.parse_args()
    
    run_pipeline(url=args.url, file_path=args.file, whisper_model=args.whisper, ollama_model=args.ollama)
