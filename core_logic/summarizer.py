import ollama

def summarize_text(text: str, model_name: str = "llama3") -> str:
    """
    Przekazuje transkrypcję do lokalnego modelu LLM w celu podsumowania.
    Wymaga działającego serwera Ollama i pobranego zadanego modelu.
    """
    print(f"[*] Generowanie podsumowania przy użyciu lokalnego modelu ({model_name})...")
    
    prompt = f"""
Jako inteligentny asystent, przeanalizuj poniższą transkrypcję z podcastu lub nagrania wideo.
Przygotuj dla mnie:
1. Główne przesłanie (1-2 zdania tłumaczące o co chodzi).
2. Krótki artykuł na bloga i angażujące podsumowanie najważniejszych kwestii.
3. Czytelną listę najważniejszych kluczowych punktów (bullet points).

Oto transkrypcja:
---
{text}
---
Wygeneruj odpowiedź w języku polskim, chyba że sam tekst wyraźnie jest w innym i to psuje kontekst.
"""

    response = ollama.chat(model=model_name, messages=[
        {
            'role': 'user',
            'content': prompt
        }
    ])
    
    print("[+] Podsumowanie gotowe.")
    return response['message']['content']
