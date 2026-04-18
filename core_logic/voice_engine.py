import os
import torch
import warnings

# Ignorujemy błędy wersji, żeby nie śmieciły
warnings.filterwarnings("ignore", category=UserWarning)

# --- KLUCZOWA POPRAWKA PYTORCH 2.6 ---
# W PyTorch 2.6 zablokowano domyślny odczyt złożonych obiektów, a biblioteka
# TTS składa się z wielu klas (m.in. XttsConfig, XttsAudioConfig). Zamiast dodawać każdą,
# omijamy ten test globalnie dla tej konkretnej sesji i skryptu.
_original_load = torch.load
def safe_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return _original_load(*args, **kwargs)
torch.load = safe_load
from TTS.api import TTS

def generate_voice(text, speaker_wav, output_path="data/generated_voice.wav"):
    """
    Klonuje głos na podstawie wzorca i zapisuje do pliku .wav
    """
    print(f"\n🧠 Inicjalizacja modelu XTTS-v2...")
    
    # Wykrywamy procesor Maca (MPS)
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    
    try:
        # Ładowanie modelu
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        
        print(f"🎙️ Peter Griffin generuje audio...")
        tts.tts_to_file(
            text=text,
            speaker_wav=speaker_wav,
            language="pl",
            file_path=output_path
        )
        print(f"✅ Głos wygenerowany pomyślnie!")
        return True
    except Exception as e:
        print(f"❌ Błąd w silniku głosu: {e}")
        return False

if __name__ == "__main__":
    generate_voice("Testujemy głos Petera Griffina!", "voices/peter_griffin.wav")