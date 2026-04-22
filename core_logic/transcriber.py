import whisper
import torch
import os

def transcribe_audio(path, return_segments=True, model_size="large-v3", language="pl"):
    """
    Audio transcription with model selection.
    model_size: "large-v3" (accurate), "turbo" or "medium" (fast)
    """
    if not os.path.exists(path):
        print(f"❌ ERROR: File to transcribe does not exist: {path}")
        return None

    print(f"\n🔍 [WHISPER] Starting transcription of file: {os.path.basename(path)}")
    print(f"📦 Model used: {model_size}")

    # Detect Apple Silicon acceleration (MPS)
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    
    try:
        # Loading model into memory
        # WARNING: This is the moment when RAM usage spikes
        model = whisper.load_model(model_size, device=device)

        # Transcription with live preview (verbose=True)
        # language parameter forces the provided language, which speeds up startup (model doesn't guess)
        result = model.transcribe(path, verbose=True, language=language)

        print(f"✅ Transcription completed successfully.")

        if return_segments:
            # Return a list of segments with timestamps (for VIDEO_MAKER)
            return result["segments"]
        else:
            # Return just the text (for program logic)
            return result["text"]

    except Exception as e:
        print(f"❌ Transcription error: {e}")
        return None