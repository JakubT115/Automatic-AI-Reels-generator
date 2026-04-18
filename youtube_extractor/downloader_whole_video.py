import os
from pathlib import Path
import yt_dlp

def pobierz_wideo_z_yt(url, folder_docelowy="data/video"):
    """
    Pobiera film z YouTube i testuje plik ciasteczek.
    """
    # 1. USTALANIE ŚCIEŻEK
    folder_skryptu = Path(__file__).parent.absolute()
    pelna_sciezka_folderu = (folder_skryptu / folder_docelowy).resolve()
    sciezka_do_cookies = folder_skryptu / "cookies.txt"

    # Tworzymy folder na filmy, jeśli go nie ma
    if not pelna_sciezka_folderu.exists():
        pelna_sciezka_folderu.mkdir(parents=True, exist_ok=True)

    print(f"🎬 Plik wideo zostanie zapisany w: {pelna_sciezka_folderu}")

    # ==========================================
    # --- DIAGNOSTYKA CIASTECZEK ---
    # ==========================================
    print("\n--- TEST CIASTECZEK ---")
    print(f"Ścieżka do ciasteczek: {sciezka_do_cookies}")
    print(f"Czy Python widzi plik 'cookies.txt'?: {sciezka_do_cookies.exists()}")
    
    if sciezka_do_cookies.exists():
        try:
            with open(sciezka_do_cookies, 'r', encoding='utf-8') as f:
                pierwsza_linia = f.readline().strip()
                print(f"Pierwsza linia pliku: {pierwsza_linia}")
                if "Netscape HTTP Cookie File" not in pierwsza_linia:
                    print("❌ BŁĄD KRYTYCZNY: Zły format pliku! Brakuje nagłówka Netscape.")
                else:
                    print("✅ Format pliku wydaje się poprawny.")
        except Exception as e:
             print(f"❌ Nie mogłem odczytać pliku: {e}")
    else:
        print("❌ BŁĄD: Python nie widzi pliku z ciasteczkami w tym folderze!")
    print("-----------------------\n")
    # ==========================================

    # 3. KONFIGURACJA yt-dlp
    opcje = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', 
        'outtmpl': str(pelna_sciezka_folderu / '%(title)s.%(ext)s'),
        'cookiefile': str(sciezka_do_cookies), 
    }

    # 4. POBIERANIE
    try:
        with yt_dlp.YoutubeDL(opcje) as ydl:
            ydl.download([url])
        print(f"\n✅ Sukces! Twój film czeka w folderze.")
    except Exception as e:
        print(f"\n❌ Wystąpił błąd podczas pobierania: {e}")

# --- Testowanie programu ---
if __name__ == "__main__":
    link = input("Wklej link do filmu na YouTube: ").strip()
    pobierz_wideo_z_yt(link)