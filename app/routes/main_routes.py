from flask import Blueprint, render_template
from app.models.blog import BlogPost
from flask import request, send_file
from PIL import Image
import io
import requests
import pillow_heif
from gtts import gTTS


# Define where you store your "Pre-known" voice files
VOICE_ASSETS_DIR = "app/static/audio/voices/"


main_bp = Blueprint('main', __name__)

# Register HEIF opener so Pillow can read iPhone photos
pillow_heif.register_heif_opener()

# --- CONFIGURATION 
HF_TOKEN = "your_actual_token_here"

API_URL = "https://api-inference.huggingface.co/models/coqui/XTTS-v2"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

# Map names to the PROCESSED wav files in static
VOICE_MAP = {
    "abhi": "app/static/audio/voices/abhi_ref.wav",
    "deepika": "app/static/audio/voices/deepika_ref.wav",
    "kelly": "app/static/audio/voices/kelly_ref.wav",
    "davel": "app/static/audio/voices/davel_ref.wav",
    
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
    text = request.form.get('text')
    voice_key = request.form.get('voice_id') 
    
    if not text:
        return "No text provided", 400

    # 1. Attempt High-Quality XTTS-v2 with Voice Reference
    try:
        ref_path = VOICE_MAP.get(voice_key)
        
        if ref_path and os.path.exists(ref_path):
            with open(ref_path, "rb") as audio_file:
                # Encode the reference voice to base64 for API transmission
                encoded_speaker = base64.b64encode(audio_file.read()).decode("utf-8")

            payload = {
                "inputs": text,
                "parameters": {
                    "speaker_wav": encoded_speaker,
                    "language": "hi" 
                }
            }
            
            # Increase timeout as XTTS-v2 is a large model
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                print(f"✅ XTTS Success: Voice cloned using {voice_key}")
                return send_file(
                    io.BytesIO(response.content),
                    mimetype='audio/wav'
                )
            else:
                print(f"⚠️ XTTS API Error: {response.status_code} - {response.text}")
        else:
            print(f"❌ Reference voice file not found: {ref_path}")

    except Exception as e:
        print(f"🔥 Neural TTS Error: {e}")

    # 2. FALLBACK: gTTS (Ensures user always gets audio)
    try:
        print("🔄 Falling back to gTTS...")
        tts = gTTS(text=text, lang='hi')
        audio_io = io.BytesIO()
        tts.write_to_fp(audio_io)
        audio_io.seek(0)
        return send_file(audio_io, mimetype='audio/mpeg')
    except Exception as e:
        return f"Audio generation failed: {str(e)}", 500