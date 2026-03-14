import os

class Config:
    # Use a secret key for session security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'nexa-secret-ai-key-2026'
    
    # Define the database location
    # This creates a file named nexa.db in your project root
    'SQLALCHEMY_DATABASE_URI' = 'postgresql://postgres.lberqoazxfxarczjogdd:Hireberth%401502@aws-1-ap-south-1.pooler.supabase.com:5432/postgres' #'sqlite:///nexa.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False