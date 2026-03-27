from flask import Blueprint, render_template
from app.models.blog import BlogPost
import tempfile

from flask import Blueprint, request, send_file, render_template,after_this_request


from PIL import Image
import io
import os, shutil
from dotenv import load_dotenv
import base64
import requests
import pillow_heif
from gtts import gTTS
import io
from gradio_client import Client, handle_file



# 2. Load the .env file (looks for a file named .env in your root folder)
load_dotenv()


# Define where you store your "Pre-known" voice files
VOICE_ASSETS_DIR = "app/static/audio/voices/"

# Map names to the PROCESSED wav files in static
VOICE_MAP = {
        "abhi": "app/static/audio/voices/abhi_ref.wav",
        "deepika": "app/static/audio/voices/deepika_ref.wav",
        "kelly": "app/static/audio/voices/kelly_ref.wav",
        "davel": "app/static/audio/voices/davel_ref.wav",
        
    }



main_bp = Blueprint('main', __name__)



# Register HEIF opener so Pillow can read iPhone photos
pillow_heif.register_heif_opener()

# --- CONFIGURATION 
HF_TOKEN = os.getenv("HF_TOKEN")

# Connect to the official Qwen3 Space
client = Client("Qwen/Qwen3-TTS", token=HF_TOKEN)



# Using a powerful multilingual XTTS-v2 API
API_URL = "https://api-inference.huggingface.co/models/coqui/XTTS-v2"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json",
    
}



@main_bp.route('/')
def index():
    # Fetch the 3 latest posts to show on your Home Page
    latest_posts = BlogPost.query.filter_by(is_published=True).order_by(BlogPost.published_at.desc()).limit(3).all()
    return render_template('index.html', posts=latest_posts)

@main_bp.route('/services')
def services():
    return render_template('services.html')

@main_bp.route('/tools')
def tools():
    return render_template('tools.html')

@main_bp.route('/work')
def work():
    return render_template('work.html')


@main_bp.route('/convert-advanced', methods=['POST'])
def convert_advanced():
    file = request.files.get('image')
    target_ext = request.form.get('target').lower()
    
    if not file:
        return "No file uploaded", 400

    try:
        # 1. Open the image
        img = Image.open(file)

        # 2. Universal Format Mapping for Pillow
        # Maps user selection to Pillow's internal driver names
        save_format = target_ext.upper()
        if save_format in ['JPG', 'JPEG', 'JFIF']: save_format = 'JPEG'
        if save_format in ['ICO', 'ICNS']: save_format = 'ICO'
        if save_format in ['EPS', 'PS']: save_format = 'EPS'

        # 3. Smart Flattening (Transparency Fix)
        # Formats that REQUIRE RGB (No Alpha/Transparency allowed)
        no_alpha_formats = ['JPEG', 'PDF', 'EPS', 'BMP', 'JFIF']
        
        if save_format in no_alpha_formats:
            if img.mode in ("RGBA", "P", "LA"):
                # Create white background and paste original image over it
                background = Image.new("RGB", img.size, (255, 255, 255))
                # If mode is RGBA, use the 4th channel as a mask for clean edges
                mask = img.split()[3] if img.mode == 'RGBA' else None
                background.paste(img, mask=mask)
                img = background
            elif img.mode != "RGB":
                img = img.convert("RGB")

        # 4. Process to Memory
        img_io = io.BytesIO()
        
        # Specific saving parameters
        save_params = {}
        if save_format == 'JPEG': save_params['quality'] = 90
        if save_format == 'PDF': save_params['resolution'] = 100.0
        
        img.save(img_io, save_format, **save_params)
        img_io.seek(0)

        # 5. Professional MIME Mapping
        mime_map = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'ico': 'image/x-icon',
            'pdf': 'application/pdf',
            'eps': 'application/postscript',
            'ps': 'application/postscript',
            'webp': 'image/webp'
        }

        return send_file(
            img_io, 
            mimetype=mime_map.get(target_ext, f'image/{target_ext}'),
            as_attachment=True,
            download_name=f"nexa-converted.{target_ext}"
        )

    except Exception as e:
        print(f"Nexa Converter Error: {e}")
        return f"Conversion failed: {str(e)}", 500


@main_bp.route('/text-to-speech')
def tts_page():
    return render_template('tts.html')

        
@main_bp.route('/generate-audio', methods=['POST'])
def generate_audio():
    import shutil
    target_text = request.form.get('text', '').strip()
    voice_key = request.form.get('voice_id', 'abhi')
    
    BASE_DIR = os.getcwd()
    ref_wav_path = os.path.join(BASE_DIR, "app", "static", "audio", "voices", f"{voice_key}_ref.wav")
    output_path = os.path.join(BASE_DIR, "app", "static", "audio", "output.wav")

    if not target_text:
        return "Please enter text", 400

    try:
        print(f" Generating Qwen3 Voice Clone for: {voice_key}")
        
        # We use the 6 parameters exactly as defined in the Qwen3 API docs you shared:
        # ref_audio, ref_text, target_text, language, use_xvector_only, model_size
        result = client.predict(
            ref_audio=handle_file(ref_wav_path),
            ref_text="",               # Empty because we'll use x-vector
            target_text=target_text,
            language="Auto",           # Handles Hindi/English automatically
            use_xvector_only=True,     # Setting to True bypasses the need for transcription
            model_size="1.7B",         # High quality mode
            api_name="/generate_voice_clone"
        )

        # Qwen3 returns a tuple: [0] is the filepath
        generated_file = result[0]
        
        if os.path.exists(output_path):
            os.remove(output_path)
        shutil.move(generated_file, output_path)

        return send_file(output_path, mimetype='audio/wav')

    except Exception as e:
        print(f"Qwen3 Error: {e}")
        return f"Cloning Error: {str(e)}", 500