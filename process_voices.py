from pydub import AudioSegment
import os

def prepare_reference_audio(input_path, output_name):
    """
    Trims audio to 10 seconds and converts to 22050Hz Mono WAV.
    """
    # 1. Load the file (supports mp3, wav, m4a, etc.)
    audio = AudioSegment.from_file(input_path)
    
    # 2. Trim to first 10 seconds (10,000 milliseconds)
    # XTTS performs best with 6-10 seconds of clear speech
    trimmed_audio = audio[:10000]
    
    # 3. Standardize for XTTS-v2
    # Mono (1 channel) and 22050Hz sample rate are ideal
    processed_audio = trimmed_audio.set_frame_rate(22050).set_channels(1)
    
    # 4. Ensure output directory exists
    output_dir = "app/static/audio/voices/"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, f"{output_name}_ref.wav")
    
    # 5. Export
    processed_audio.export(output_path, format="wav")
    print(f"Success! Voice saved to: {output_path}")

if __name__ == "__main__":
    prepare_reference_audio("downloads/Abhi.mp3", "abhi")
    prepare_reference_audio("downloads/Deepika.mp3", "deepika")
    prepare_reference_audio("downloads/kelly.mp3", "kelly")
    prepare_reference_audio("downloads/Davel.mp3", "davel")
