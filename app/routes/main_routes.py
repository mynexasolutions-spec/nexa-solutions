from flask import Blueprint, render_template
from app.models.blog import BlogPost
from flask import request, send_file
from PIL import Image
import io
import pillow_heif

main_bp = Blueprint('main', __name__)

# Register HEIF opener so Pillow can read iPhone photos
pillow_heif.register_heif_opener()

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