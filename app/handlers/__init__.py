from telegram.ext import Application
from .compression import register as register_compression
from .cutting import register as register_cutting
from .splitting import register as register_splitting
from .watermark import register as register_watermark

def register_handlers(application: Application):
    """Register all handlers with the Telegram application"""
    register_compression(application)
    register_cutting(application)
    register_splitting(application)
    register_watermark(application)
