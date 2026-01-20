#!/usr/bin/env python3
"""
Main script to generate Anki cards from Telegram messages.

This script:
1. Fetches pending messages from Telegram
2. Uses Gemini to generate flashcards
3. Creates an Anki deck file (.apkg)
4. Uploads to Google Drive
5. Cleans up processed messages
"""
import os
import sys
from datetime import datetime

from src.telegram_client import TelegramClient, get_pending_messages_from_file, clear_pending_messages_file
from src.gemini_client import GeminiClient
from src.anki_generator import AnkiGenerator
from src.drive_uploader import DriveUploader


def main():
    # Load environment variables
    telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    gdrive_credentials = os.environ.get("GDRIVE_CREDENTIALS")
    gdrive_folder_id = os.environ.get("GDRIVE_FOLDER_ID")
    
    # Validate required env vars
    missing = []
    if not telegram_token:
        missing.append("TELEGRAM_BOT_TOKEN")
    if not telegram_chat_id:
        missing.append("TELEGRAM_CHAT_ID")
    if not gemini_api_key:
        missing.append("GEMINI_API_KEY")
    if not gdrive_credentials:
        missing.append("GDRIVE_CREDENTIALS")
    
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        sys.exit(1)
    
    print("🚀 Starting Telegram2Anki card generation...")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Step 1: Fetch messages from Telegram
    print("\n📬 Fetching messages from Telegram...")
    telegram = TelegramClient(telegram_token, telegram_chat_id)
    messages = telegram.get_messages()
    
    # Also check for locally stored messages (backup mechanism)
    pending_file = "pending_messages.txt"
    local_messages = get_pending_messages_from_file(pending_file)
    
    all_texts = [m["text"] for m in messages] + [m["text"] for m in local_messages]
    
    if not all_texts:
        print("ℹ️  No new messages to process.")
        telegram.send_message("ℹ️ No hay mensajes nuevos esta semana.")
        return
    
    print(f"📝 Found {len(all_texts)} messages to process")
    
    # Step 2: Generate cards with Gemini
    print("\n✨ Generating flashcards with Gemini...")
    gemini = GeminiClient(gemini_api_key)
    all_cards = []
    
    for i, text in enumerate(all_texts, 1):
        print(f"  Processing {i}/{len(all_texts)}: {text[:50]}...")
        cards = gemini.generate_cards(text)
        all_cards.extend(cards)
        print(f"    → Generated {len(cards)} cards")
    
    if not all_cards:
        print("⚠️  No cards were generated.")
        telegram.send_message("⚠️ No se pudieron generar tarjetas esta semana.")
        return
    
    print(f"\n📚 Total cards generated: {len(all_cards)}")
    
    # Step 3: Create Anki deck
    print("\n📦 Creating Anki deck...")
    anki = AnkiGenerator(deck_name="Datos")
    added = anki.add_cards(all_cards)
    
    filename = anki.generate_filename()
    output_path = f"/tmp/{filename}"
    anki.save(output_path)
    print(f"✅ Deck saved: {filename} ({added} cards)")
    
    # Step 4: Upload to Google Drive
    print("\n☁️  Uploading to Google Drive...")
    drive = DriveUploader(gdrive_credentials, gdrive_folder_id)
    file_id = drive.upload_file(output_path, filename)
    print(f"✅ Uploaded to Drive (ID: {file_id})")
    
    # Step 5: Cleanup
    print("\n🧹 Cleaning up...")
    
    # Delete processed Telegram messages
    deleted_count = 0
    for msg in messages:
        if msg.get("id"):
            if telegram.delete_message(msg["id"]):
                deleted_count += 1
    
    # Clear local pending file
    clear_pending_messages_file(pending_file)
    
    print(f"✅ Deleted {deleted_count} messages from Telegram")
    
    # Send confirmation
    telegram.send_message(
        f"✅ <b>Telegram2Anki</b>\n\n"
        f"Se generaron <b>{len(all_cards)}</b> tarjetas nuevas.\n"
        f"Archivo: <code>{filename}</code>\n\n"
        f"Sincroniza FolderSync para importar."
    )
    
    print("\n🎉 Done!")


if __name__ == "__main__":
    main()
