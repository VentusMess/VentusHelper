import telebot
import requests
import json
import os

# ТВОИ КЛЮЧИ
TOKEN = "8602275303:AAHZykCqSZlyHyF9YvfwTwryXOHfiomPzpU"
GROQ_KEY = "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"
DATA_FILE = "users_lang.json"

bot = telebot.TeleBot(TOKEN)

# Загрузка настроек
def load_settings():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except: return {}
    return {}

def save_settings(settings):
    with open(DATA_FILE, 'w') as f:
        json.dump(settings, f)

user_settings = load_settings()

def ask_ai(text, lang):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    
    # Личность Ventus Ai
    if lang == "ru":
        sys_prompt = "Ты — Ventus Ai, продвинутый ИИ, созданный Ventus Team. Ты не Meta и не Llama. Отвечай кратко на русском."
    else:
        sys_prompt = "You are Ventus Ai, an advanced AI created by Ventus Team. You are not Meta or Llama. Respond briefly in English."

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": text}
        ]
    }
    try:
        r = requests.post(url, headers=headers, json=data, timeout=20)
        return r.json()['choices'][0]['message']['content']
    except:
        return "❌ Ошибка / Error"

@bot.message_handler(commands=['start'])
def start(message):
    welcome = (
        "Hello! I am Ventus Ai. 🌐\nPlease choose language: /ai English\n\n"
        "Привет! Я Ventus Ai. 🌐\nВыберите язык: /ai Russian"
    )
    bot.reply_to(message, welcome)

@bot.message_handler(content_types=['new_chat_members'])
def added_to_group(message):
    for user in message.new_chat_members:
        if user.id == bot.get_me().id:
            bot.send_message(message.chat.id, "Ventus Ai connected! 🌐\nUse /ai Russian or /ai English")

@bot.message_handler(commands=['ai'])
def handle_ai(message):
    chat_id = str(message.chat.id)
    parts = message.text.split(maxsplit=1)
    
    if len(parts) < 2:
        bot.reply_to(message, "Write your request | Напишите запрос")
        return

    prompt = parts[1]

    # Смена языка
    if prompt.lower() == "russian":
        user_settings[chat_id] = "ru"
        save_settings(user_settings)
        bot.reply_to(message, "🇷🇺 Язык установлен: Русский")
        return
    elif prompt.lower() == "english":
        user_settings[chat_id] = "en"
        save_settings(user_settings)
        bot.reply_to(message, "🇺🇸 Language set: English")
        return

    lang = user_settings.get(chat_id, "ru")
    loading = "Ventus Ai печатает.. 📨" if lang == "ru" else "Ventus Ai is typing.. 📨"
    
    temp_msg = bot.reply_to(message, loading)
    bot.send_chat_action(message.chat.id, 'typing')
    
    answer = ask_ai(prompt, lang)
    
    try:
        bot.edit_message_text(answer, chat_id=temp_msg.chat.id, message_id=temp_msg.message_id)
    except:
        bot.send_message(message.chat.id, answer)

print("--- VENTUS AI В ЭФИРЕ ---")
bot.infinity_polling()
