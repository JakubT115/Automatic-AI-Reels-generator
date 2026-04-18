import whisper
import torch
import os

def transcribe_audio(path, return_segments=True, model_size="large-v3"):
    """
    Transkrypcja audio z wyborem modelu.
    model_size: "large-v3" (dokładny), "turbo" lub "medium" (szybkie)
    """
    if not os.path.exists(path):
        print(f"❌ BŁĄD: Plik do transkrypcji nie istnieje: {path}")
        return None

    print(f"\n🔍 [WHISPER] Start transkrypcji pliku: {os.path.basename(path)}")
    print(f"📦 Używany model: {model_size}")

    # Wykrywanie akceleracji Apple Silicon (MPS)
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    
    try:
        # Ładowanie modelu do pamięci
        # UWAGA: To jest moment, w którym RAM skacze do góry
        model = whisper.load_model(model_size, device=device)

        # Transkrypcja z podglądem na żywo (verbose=True)
        # language="pl" wymusza polski, co przyspiesza start (model nie musi zgadywać)
        result = model.transcribe(path, verbose=True, language="pl")

        print(f"✅ Transkrypcja zakończona sukcesem.")

        if return_segments:
            # Zwracamy listę z czasami (dla VIDEO_MAKER)
            return result["segments"]
        else:
            # Zwracamy sam tekst (dla logiki programu)
            return result["text"]

    except Exception as e:
        print(f"❌ Błąd podczas transkrypcji: {e}")
        return None