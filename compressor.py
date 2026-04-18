import subprocess
import os

def compress_video(input_path, output_path, target_size_mb=None):
    """
    Kompresuje wideo przy użyciu ffmpeg.
    :param input_path: Ścieżka do ciężkiego pliku
    :param output_path: Gdzie zapisać lżejszy plik
    :param target_size_mb: (Opcjonalnie) Jeśli chcesz celować w konkretną wagę
    """
    if not os.path.exists(input_path):
        print(f"❌ Błąd: Nie znaleziono pliku {input_path}")
        return

    print(f"Standardowa kompresja pliku: {input_path}...")

    # Używamy CRF (Constant Rate Factor). 
    # 0 to bezstratna, 23 to standard, 51 to najgorsza jakość.
    # Wartość 28 jest idealna dla TikToków - plik jest mały, a obraz żyleta.
    cmd = [
        'ffmpeg',
        '-i', input_path,        # plik wejściowy
        '-vcodec', 'libx264',    # kodek h264
        '-crf', '28',            # jakość (im wyżej tym mniejszy plik)
        '-preset', 'slow',       # wolniej = lepsza kompresja
        '-acodec', 'aac',        # kompresja audio
        '-b:a', '128k',          # bitrate audio
        '-y', output_path        # nadpisz jeśli istnieje
    ]

    try:
        subprocess.run(cmd, check=True)
        
        old_size = os.path.getsize(input_path) / (1024 * 1024)
        new_size = os.path.getsize(output_path) / (1024 * 1024)
        
        print(f"\n✅ Kompresja zakończona!")
        print(f"Stary rozmiar: {old_size:.2f} MB")
        print(f"Nowy rozmiar: {new_size:.2f} MB")
        print(f"Zaoszczędzono: {((old_size - new_size) / old_size) * 100:.1f}%")

    except subprocess.CalledProcessError as e:
        print(f"❌ Błąd podczas kompresji: {e}")

if __name__ == "__main__":
    print("=== KOMPRESOR WIDEO ===")
    plik_wejsciowy = input("Wklej ścieżkę do ciężkiego MP4: ").strip()
    
    # Tworzy nazwę wyjściową np. wideo_compressed.mp4
    nazwa, rozszerzenie = os.path.splitext(plik_wejsciowy)
    plik_wyjsciowy = f"{nazwa}_compressed.mp4"
    
    compress_video(plik_wejsciowy, plik_wyjsciowy)