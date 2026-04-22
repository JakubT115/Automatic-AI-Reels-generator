import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, vfx

# ==========================================
# 1. PRZYGOTOWANIE WIDEO W TLE
# ==========================================
def prepare_background_video(background_video_path, audio_clip):
    """
    Ładuje wideo w tle, zapętla je aby nie skończyło się przed audio, i podmienia dźwięk.
    """
    bg_clip = VideoFileClip(background_video_path).resize(height=1080)
    
    # Jeżeli audio jest dłuższe niż wideo w tle, zapętlamy wideo do pełnej długości audio.
    # Używamy vfx.loop aby wideo zawsze wystarczyło.
    bg_clip = bg_clip.fx(vfx.loop, duration=audio_clip.duration)
    
    # Nakładamy wygenerowany głos AI (lub oryginalny) na wideo
    bg_clip = bg_clip.set_audio(audio_clip)
    
    return bg_clip

# ==========================================
# 2. GENEROWANIE NAPISÓW (Z FILTREM AI)
# ==========================================
def create_subtitle_clips(segments, video_width):
    """
    Przetwarza segmenty z Whispera na klatki z tekstem (TextClips),
    automatycznie zawijając tekst, aby zmieścił się na ekranie 9x16.
    """
    subtitle_clips = []
    
    # KLUCZOWA ZMIANA 1: Obliczamy bezpieczną szerokość dla napisów (np. 80% ekranu)
    # Zostawi to ładne marginesy po bokach.
    max_text_width = int(video_width * 0.8) 
    
    for segment in segments:
        text = segment["text"].strip()
        
        # Filtrowanie pustych segmentów
        if not text:
            continue

        # Konfiguracja wyglądu czcionki Impact
        txt_clip = TextClip(
            text,
            fontsize=70, 
            color='white',
            # Ścieżka do czcionki Impact na macOS:
            font='/System/Library/Fonts/Supplemental/Impact.ttf', 
            stroke_color='black',
            stroke_width=2,
            
            # KLUCZOWA ZMIANA 2: Włączamy automatyczne zawijanie tekstu
            method='caption', # Ten parametr jest najważniejszy!
            size=(max_text_width, None) # Stała szerokość, automatyczna wysokość (None)
        )
        
        # Ustawianie czasów pojawienia się i zniknięcia
        txt_clip = txt_clip.set_start(segment["start"]).set_end(segment["end"])
        
        # Ustawiamy napis w centrum ekranu. Ponieważ napisy mogą mieć teraz 
        # kilka linii, MoviePy wyrówna je do środka w pionie i poziomie.
        txt_clip = txt_clip.set_position(('center', 'center'))

        subtitle_clips.append(txt_clip)
        
    return subtitle_clips

def create_video_with_subtitles(audio_path, background_video_path, segments, output_filename="gotowy_film.mp4"):
    print(f"\n🎬 Rozpoczynam montaż wideo: {output_filename}...")
    
    audio_clip = AudioFileClip(audio_path)
    bg_clip = prepare_background_video(background_video_path, audio_clip)
    subtitle_clips = create_subtitle_clips(segments, bg_clip.w)

    final_video = CompositeVideoClip([bg_clip] + subtitle_clips)

    final_video.write_videofile(
        output_filename, 
        fps=60, 
        codec="libx264", 
        audio_codec="aac"
    )
    
    audio_clip.close()
    bg_clip.close()
    final_video.close()