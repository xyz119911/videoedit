import logging
from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from app.services.ffmpeg import FFmpegService
from app.services.storage import StorageService
from app.utils.validators import validate_file_size
from app.utils.logger import log_command

logger = logging.getLogger(__name__)

@log_command
@validate_file_size
async def handle_compression(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.effective_message
    
    try:
        # Prepare files
        with StorageService.temp_directory() as temp_dir:
            input_path = temp_dir / "input.mp4"
            output_path = temp_dir / "compressed.mp4"
            
            # Download file
            await message.reply_text("📥 Downloading your video...")
            file = await StorageService.download_telegram_file(
                message.video or message.document,
                input_path
            )
            
            # Process
            await message.reply_text("⚙️ Compressing your video...")
            FFmpegService.compress(input_path, output_path)
            
            # Upload result
            await message.reply_text("📤 Uploading result...")
            await StorageService.upload_telegram_file(
                message.chat_id,
                output_path,
                caption="Your compressed video is ready!"
            )
            
    except Exception as e:
        logger.error(f"Compression failed for {user.id}: {str(e)}")
        await message.reply_text(
            "❌ Failed to process your video. Please try a smaller file or try again later."
        )
        raise

def register(application):
    application.add_handler(
        MessageHandler(
            filters.VIDEO | filters.Document.MP4,
            handle_compression
        )
    )
