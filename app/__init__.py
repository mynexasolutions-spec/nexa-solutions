from flask import Flask
from extensions import db
from app.routes.blog_routes import blog_bp

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres.lberqoazxfxarczjogdd:Hireberth%401502@aws-1-ap-south-1.pooler.supabase.com:5432/postgres'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)

    # Registering the Blueprints
    from app.routes.blog_routes import blog_bp
    from app.routes.main_routes import main_bp
    
    app.register_blueprint(blog_bp)
    app.register_blueprint(main_bp)

    return app