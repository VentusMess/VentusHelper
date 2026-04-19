import telebot
import requests
import json
import os
from flask import Flask
from threading import Thread

# --- НАСТРОЙКИ ВЕБ-СЕРВЕРА ---
app = Flask('')

@app.route('/')
def home():
    return "Ventus Ai is alive!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# --- ТВОЙ БОТ ---
TOKEN = "8602275303:AAHZykCqSZlyHyF9YvfwTwryXOHfiomPzpU"
GROQ_KEY = "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"
DATA_FILE = "users_lang.json"

bot = telebot.TeleBot(TOKEN)
user_settings = {}

if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, 'r') as f:
            user_settings = json.load(f)
    except: user_settings = {}

def ask_ai(text, lang):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    sys_prompt = "You are Ventus Ai by Loren. Not Meta, not Llama."
    if lang == "ru":
        sys_prompt = "Ты — Ventus Ai, создан Loren. Не Meta и не Llama. Отвечай кратко на русском."
    
    data = {"model": "llama-3.1-8b-instant", "messages": [{"role": "system", "content": sys_prompt}, {"role": "user", "content": text}]}
    try:
        r = requests.post(url, headers=headers, json=data, timeout=20)
        return r.json()['choices'][0]['message']['content']
    except: return "Error"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Ventus Ai 🌐\nChoose language: /ai English or /ai Russian")

@bot.message_handler(commands=['ai'])
def handle(message):
    chat_id = str(message.chat.id)
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2: return
    
    prompt = parts[1].lower()
    if "russian" in prompt:
        user_settings[chat_id] = "ru"
        bot.reply_to(message, "🇷🇺 Русский язык установлен")
        return
    elif "english" in prompt:
        user_settings[chat_id] = "en"
        bot.reply_to(message, "🇺🇸 English language set")
        return

    lang = user_settings.get(chat_id, "ru")
    temp_msg = bot.reply_to(message, "Ventus Ai...")
    answer = ask_ai(parts[1], lang)
    bot.edit_message_text(answer, chat_id=temp_msg.chat.id, message_id=temp_msg.message_id)

if __name__ == "__main__":
    keep_alive() # Запускаем веб-сервер в фоне
    print("Ventus Ai is running...")
    bot.infinity_polling()
