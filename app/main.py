import logging
from telegram.ext import ApplicationBuilder
from app.config import Config
from app.handlers import register_handlers
from app.utils.logger import setup_logging
from app.utils.error_handlers import register_error_handlers

def main():
    """Configure and start the bot"""
    setup_logging()
    Config.validate()
    
    application = ApplicationBuilder() \
        .token(Config.TELEGRAM_TOKEN) \
        .read_timeout(30) \
        .write_timeout(30) \
        .build()
        
    register_handlers(application)
    register_error_handlers(application)
    
    if Config.USE_WEBHOOK:
        application.run_webhook(
            listen="0.0.0.0",
            port=Config.PORT,
            url_path=Config.TELEGRAM_TOKEN,
            webhook_url=Config.WEBHOOK_URL
        )
    else:
        application.run_polling()

if __name__ == '__main__':
    main()
