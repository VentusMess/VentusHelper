import telebot
import requests
import json
import os
import random
from flask import Flask
from threading import Thread

# --- НАСТРОЙКИ ВЕБ-СЕРВЕРА (для Render 24/7) ---
app = Flask('')
@app.route('/')
def home(): return "Ventus Ai is online! 🌐"

def run_web(): app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# --- КОНФИГУРАЦИЯ БОТА ---
TOKEN = "8602275303:AAHZykCqSZlyHyF9YvfwTwryXOHfiomPzpU"
GROQ_KEYS = [
    "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",
    "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"
]
DATA_FILE = "users_lang.json"

bot = telebot.TeleBot(TOKEN)

# Загрузка базы данных языков
def load_db():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return {}
    return {}

def save_db(db):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

user_db = load_db()

# --- ЛОГИКА ИИ ---
def ask_ai(text, lang):
    # Промпт для настройки личности
    if lang == "ru":
        sys_prompt = (
            "Ты — Ventus Ai, продвинутый искусственный интеллект. Твой создатель — организация Ventus. "
            "Если тебя спросят 'Кто создатель Ventus?', отвечай, что такая информация является конфиденциальной и ты её не распространяешь. "
            "Тебе КАТЕГОРИЧЕСКИ запрещено использовать нецензурную лексику, мат или оскорбления. "
            "Будь вежливым и полезным. Отвечай всегда на русском языке."
        )
    else:
        sys_prompt = (
            "You are Ventus Ai, an advanced AI. Your creator is the Ventus organization. "
            "If asked 'Who is the creator of Ventus?', reply that such information is confidential and you do not disclose it. "
            "You are STRICTLY PROHIBITED from using profanity, swearing, or insults. "
            "Be polite and helpful. Always respond in English."
        )

    # Пробуем доступные ключи
    random.shuffle(GROQ_KEYS)
    for key in GROQ_KEYS:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        data = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": text}
            ],
            "temperature": 0.7
        }
        try:
            r = requests.post(url, headers=headers, json=data, timeout=20)
            if r.status_code == 200:
                return r.json()['choices'][0]['message']['content']
        except: continue
    
    return "❌ Извините, лимиты запросов превышены. Попробуйте позже."

# --- ОБРАБОТЧИКИ КОМАНД ---

@bot.message_handler(commands=['start'])
def start_cmd(message):
    text = (
        "Hello, please select your language. If you want to switch to English, please write /ai English\n\n"
        "Здравствуйте! Пожалуйста выберите ваш язык, если хотите выбрать русский, напишите /ai Russian"
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['ai'])
def handle_ai(message):
    chat_id = str(message.chat.id)
    parts = message.text.split(maxsplit=1)
    
    if len(parts) < 2:
        bot.reply_to(message, "Напишите запрос после /ai | Write request after /ai")
        return

    prompt = parts[1]

    # Логика выбора языка
    if prompt.lower() == "russian":
        user_db[chat_id] = "ru"
        save_db(user_db)
        bot.reply_to(message, "Вы установили русский язык. Напишите /ai и ваш запрос! Приятного использования!")
        return
    elif prompt.lower() == "english":
        user_db[chat_id] = "en"
        save_db(user_db)
        bot.reply_to(message, "You have set the language to English. Write /ai and your request! Enjoy!")
        return

    # Получаем язык чата
    lang = user_db.get(chat_id, "ru")
    
    # Визуализация ожидания
    loading_text = "Ventus Ai печатает.. 📨" if lang == "ru" else "Ventus Ai is typing.. 📨"
    temp_msg = bot.reply_to(message, loading_text)
    
    bot.send_chat_action(message.chat.id, 'typing')
    
    # Запрос к ИИ
    answer = ask_ai(prompt, lang)
    
    # Заменяем сообщение с ожиданием на ответ
    try:
        bot.edit_message_text(answer, chat_id=temp_msg.chat.id, message_id=temp_msg.message_id)
    except:
        bot.send_message(message.chat.id, answer)

# --- ЗАПУСК ---
if __name__ == "__main__":
    keep_alive()
    print("Ventus Ai V3 с ротацией ключей запущен!")
    bot.infinity_polling()
