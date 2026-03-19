from flask import Blueprint, render_template
from app.models.blog import BlogPost
from flask import request, send_file
from PIL import Image
import io
import os
import requests
import pillow_heif
from gtts import gTTS

main_bp = Blueprint('main', __name__)

# Register HEIF opener so Pillow can read iPhone photos
pillow_heif.register_heif_opener()


# Load keys from environment

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

# --- HuggingFace CONFIGURATION 
HF_TOKEN = os.getenv("HF_TOKEN")

API_URL = "https://api-inference.huggingface.co/models/coqui/XTTS-v2"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}




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
    text = request.form.get('text')
    # This receives the ID from the radio button choice
    voice_id = request.form.get('voice_id') 
    
    if not text or not voice_id:
        return "Missing text or voice selection", 400

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY,
    }

    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            return send_file(io.BytesIO(response.content), mimetype='audio/mpeg')
        else:
            # FALLBACK to gTTS if ElevenLabs fails/credits over
            tts = gTTS(text=text, lang='hi')
            audio_io = io.BytesIO()
            tts.write_to_fp(audio_io)
            audio_io.seek(0)
            return send_file(audio_io, mimetype='audio/mpeg')
    except Exception as e:
        return str(e), 500

@main_bp.route('/get-voice-preview/<voice_id>')
def get_voice_preview(voice_id):
    import os
    import requests
    
    # 1. Try to get key from Environment (Vercel/Local .env)
    # 2. Fallback to the string ONLY for local testing
    api_key = os.getenv("ELEVENLABS_API_KEY", "sk_f274fe938fd4ab5f9328bdb74a902cd022b99c1b125b905a")

    if not api_key:
        return {"error": "API Key missing"}, 500

    url = f"https://api.elevenlabs.io/v1/voices/{voice_id}"
    headers = {"xi-api-key": api_key}
    
    try:
        # Increase timeout to 10 to prevent 500 errors on slow connections
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {"preview_url": data.get('preview_url')}
        else:
            # This helps you see the REAL error from ElevenLabs in your terminal
            print(f"ElevenLabs API Error: {response.status_code} - {response.text}")
            return {"error": response.text}, response.status_code
            
    except Exception as e:
        print(f"Python Crash: {str(e)}")
        return {"error": str(e)}, 500