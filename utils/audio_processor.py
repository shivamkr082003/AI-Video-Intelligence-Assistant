import yt_dlp
from pydub import AudioSegment
import os

DOWNLOAD_DIR = 'downloades'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_youtube_audio(url: str) -> str:
    # ── 🔥 FINAL FIX: HARDCODED STATIC FILENAME ──
    # Emojis, spaces, aur special characters (||, 🔥, ✅) ka jhanjhat 
    # khatam karne ke liye hum file ka naam fix 'youtube_audio' rakh rahe hain.
    output_path = os.path.join(DOWNLOAD_DIR, "youtube_audio.%(ext)s")
    
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        "no_warnings": True,
        
        # ── CLOUD BYPASS CONFIGS ──
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web_embedded"],
                "skip": ["dash", "hls"]
            }
        },
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Sec-Fetch-Mode": "navigate"
        }
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Pura downloading aur post-processing (WAV conversion) yt-dlp khud sambhalega
        ydl.download([url])
        
    # Kyunki filename fix hai, toh final WAV file hamesha isi path par milegi
    final_wav_path = os.path.join(DOWNLOAD_DIR, "youtube_audio.wav")
    
    # Ek safety check ki file disk par generate hui ya nahi
    if not os.path.exists(final_wav_path):
        raise FileNotFoundError(f"Error: Final audio file could not be found at {final_wav_path}")
        
    return final_wav_path


def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to WAV format using pydub."""
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000) # 16khz
    audio.export(output_path, format="wav")
    return output_path


def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000 

    chunks = []

    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start : start + chunk_ms]
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")

        chunks.append(chunk_path)
    
    return chunks


def process_input(source: str) -> list:
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks