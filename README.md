# Telegram2Anki

Sistema automatizado para convertir datos curiosos capturados en Telegram a tarjetas de Anki.

## Cómo funciona

1. **Captura**: Compartes texto a tu bot de Telegram
2. **Procesamiento**: Cada semana, GitHub Actions procesa los mensajes con Gemini API
3. **Sincronización**: El archivo `.apkg` se sube a Google Drive y FolderSync lo descarga a AnkiDroid

## Setup

### 1. Crear el bot de Telegram

1. Habla con [@BotFather](https://t.me/BotFather) en Telegram
2. Envía `/newbot`
3. Nombre: `Telegram2Anki Bot`
4. Username: `tu_usuario_Telegram2AnkiBot` (debe ser único)
5. Guarda el token que te da

### 2. Obtener tu Chat ID

1. Envía un mensaje a tu nuevo bot
2. Visita: `https://api.telegram.org/bot<TU_TOKEN>/getUpdates`
3. Busca `"chat":{"id":XXXXXXXX}` - ese es tu Chat ID

### 3. Obtener Gemini API Key

1. Ve a [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Crea una API Key
3. Guárdala

### 4. Configurar Google Drive API

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un proyecto nuevo
3. Habilita "Google Drive API"
4. Crea credenciales → Service Account
5. Descarga el JSON de credenciales
6. Comparte la carpeta de Drive con el email del service account

### 5. Configurar GitHub Secrets

En tu repositorio → Settings → Secrets → Actions, agrega:

| Secret | Valor |
|--------|-------|
| `TELEGRAM_BOT_TOKEN` | Token del bot |
| `TELEGRAM_CHAT_ID` | Tu Chat ID |
| `GEMINI_API_KEY` | API Key de Gemini |
| `GDRIVE_FOLDER_ID` | ID de la carpeta de Drive |
| `GDRIVE_CREDENTIALS` | Contenido del JSON de service account |

### 6. Configurar FolderSync en Android

1. Crea sincronización: Google Drive → AnkiDroid folder
2. Tipo: Unidireccional (remoto → local)
3. Programación: Semanal

## Uso

Simplemente comparte cualquier texto interesante a tu bot de Telegram. Cada domingo se generarán las tarjetas automáticamente.

## Desarrollo local

```bash
pip install -r requirements.txt
python generate_cards.py
```
