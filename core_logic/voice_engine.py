import os
import torch
import warnings

# Ignore version warnings to keep output clean
warnings.filterwarnings("ignore", category=UserWarning)

# --- CRITICAL PYTORCH 2.6 FIX ---
# PyTorch 2.6 blocked default loading of complex objects, and the
# TTS library consists of multiple classes (e.g. XttsConfig, XttsAudioConfig). 
# Instead of adding each one, we bypass this test globally for this specific script.
_original_load = torch.load
def safe_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return _original_load(*args, **kwargs)
torch.load = safe_load
from TTS.api import TTS

def generate_voice(text, speaker_wav, output_path="data/generated_voice.wav", language="en"):
    """
    Clones voice based on the reference and saves to a .wav file
    """
    print(f"\n🧠 Initializing XTTS-v2 model...")
    
    # Detect Mac processor (MPS)
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    
    try:
        # Loading model
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        
        print(f"🎙️ Generating AI audio...")
        tts.tts_to_file(
            text=text,
            speaker_wav=speaker_wav,
            language=language,
            file_path=output_path
        )
        print(f"✅ Voice generated successfully!")
        return True
    except Exception as e:
        print(f"❌ Voice engine error: {e}")
        return False

if __name__ == "__main__":
    generate_voice("Testing the input voice! Hi im its me hahahaha. Sigma tung tung sahur", input("Podaj ścieżkę do pliku .wav z głosem: "))