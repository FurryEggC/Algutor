import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://knowledge_user:strong_password_123@localhost/knowledge_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
