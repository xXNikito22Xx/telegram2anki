#!/usr/bin/env python3
"""
Telegram Bot Webhook Handler

This script runs a simple webhook server to receive Telegram messages
and store them in a JSON file for later processing.

For production use with GitHub Actions, we use Telegram's getUpdates API instead.
This webhook handler is useful for local development and testing.
"""
import os
import json
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes


# File to store pending messages
MESSAGES_FILE = "messages.json"


def load_messages() -> list:
    """Load messages from JSON file."""
    if os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_messages(messages: list):
    """Save messages to JSON file."""
    with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)


def add_message(text: str, chat_id: int, message_id: int):
    """Add a new message to the storage."""
    messages = load_messages()
    messages.append({
        "text": text,
        "chat_id": chat_id,
        "message_id": message_id,
        "timestamp": datetime.now().isoformat(),
        "processed": False
    })
    save_messages(messages)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text(
        "👋 ¡Hola! Soy tu bot Telegram2Anki.\n\n"
        "📝 Envíame cualquier dato curioso que quieras recordar.\n"
        "Cada semana generaré tarjetas de Anki automáticamente.\n\n"
        "Comandos:\n"
        "/start - Ver este mensaje\n"
        "/pending - Ver mensajes pendientes\n"
        "/clear - Limpiar mensajes pendientes"
    )


async def pending_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /pending command - show pending messages."""
    messages = load_messages()
    pending = [m for m in messages if not m.get("processed")]
    
    if not pending:
        await update.message.reply_text("📭 No hay mensajes pendientes.")
        return
    
    text = f"📬 <b>Mensajes pendientes: {len(pending)}</b>\n\n"
    for i, msg in enumerate(pending[-10:], 1):  # Show last 10
        preview = msg["text"][:50] + "..." if len(msg["text"]) > 50 else msg["text"]
        text += f"{i}. {preview}\n"
    
    if len(pending) > 10:
        text += f"\n<i>...y {len(pending) - 10} más</i>"
    
    await update.message.reply_html(text)


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /clear command - clear all pending messages."""
    save_messages([])
    await update.message.reply_text("🧹 Mensajes pendientes eliminados.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming text messages."""
    message = update.message
    
    if not message or not message.text:
        return
    
    # Ignore messages that are commands
    if message.text.startswith("/"):
        return
    
    # Store the message
    add_message(
        text=message.text,
        chat_id=message.chat.id,
        message_id=message.message_id
    )
    
    # Send confirmation
    await message.reply_text("✅ Guardado para Anki")


def main():
    """Run the bot."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    
    if not token:
        print("❌ Error: TELEGRAM_BOT_TOKEN not set")
        print("Set it with: export TELEGRAM_BOT_TOKEN=your_token")
        return
    
    print("🤖 Starting Telegram2Anki Bot...")
    print("Send /start to the bot to begin.")
    
    # Create application
    app = Application.builder().token(token).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("pending", pending_command))
    app.add_handler(CommandHandler("clear", clear_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Run bot
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
