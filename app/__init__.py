import os
import sys
from flask import Flask
from extensions import db
from dotenv import load_dotenv

# 1. Load variables from your .env file into system memory
load_dotenv() 

def create_app():
    app = Flask(__name__)

    # 2. Dynamically get the URI: 
    # Use POSTGRES_URL (set by Vercel) or fallback to DATABASE_URL (from your .env)
    database_uri = os.environ.get('POSTGRES_URL') or os.environ.get('DATABASE_URL')
    
    # 3. Fix the prefix if necessary (SQLAlchemy requires 'postgresql://')
    if database_uri and database_uri.startswith("postgres://"):
        database_uri = database_uri.replace("postgres://", "postgresql://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)

    # Registering the Blueprints
    from app.routes.blog_routes import blog_bp
    from app.routes.main_routes import main_bp
    
    app.register_blueprint(blog_bp)
    app.register_blueprint(main_bp)

    # Get the absolute path to the root 'LuxTTS' directory
    lux_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'LuxTTS'))
    if lux_path not in sys.path:
        sys.path.append(lux_path)

        
    return app
