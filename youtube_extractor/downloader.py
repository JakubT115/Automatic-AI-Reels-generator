import yt_dlp
import os

def download_audio(url: str, output_dir: str = "data") -> str:
    """
    Pobiera audio z filmu na YouTube i zapisuje jako plik .mp3.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_template = os.path.join(output_dir, "%(title)s.%(ext)s")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_template,
        'quiet': False,
        
        'cookiesfrombrowser': ('firefox', ), 
        'remote_components': ['ejs:github'],
        
        # Zostawiamy Androida, współpracuje on najlepiej z ciasteczkami z przeglądarki
        'extractor_args': {
            'youtube': ['player_client=android'] 
        }
    }

    print(f"[*] Pobieranie audio z {url}...")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        expected_filename = ydl.prepare_filename(info_dict)
        base, _ = os.path.splitext(expected_filename)
        mp3_path = f"{base}.mp3"
        print(f"[+] Pobrano i zapisano jako: {mp3_path}")
        return mp3_path
