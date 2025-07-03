import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x]
    
    # Processing
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 2 * 1024 * 1024 * 1024))  # 2GB
    TEMP_DIR = os.getenv("TEMP_DIR", "/tmp/video_bot")
    TIMEOUT = int(os.getenv("TIMEOUT", 600))  # 10 minutes
    
    # Deployment
    USE_WEBHOOK = os.getenv("USE_WEBHOOK", "false").lower() == "true"
    PORT = int(os.getenv("PORT", 8443))
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    
    @classmethod
    def validate(cls):
        required = [cls.TELEGRAM_TOKEN]
        if cls.USE_WEBHOOK and not cls.WEBHOOK_URL:
            raise ValueError("WEBHOOK_URL required when using webhook")
        
        for var in required:
            if not var:
                raise ValueError(f"Missing required config: {var}")
        
        Path(cls.TEMP_DIR).mkdir(parents=True, exist_ok=True)
