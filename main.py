import os
import telebot
from gtts import gTTS
from openai import OpenAI

# Инициализация клиента API OpenAI с вашим API ключом
openai_client = OpenAI(
    api_key="ваш API ключ",
    base_url="https://api.proxyapi.ru/openai/v1",
)

# Установите свой токен от BotFather
BOT_TOKEN = 'TELEGRAM_BOT_TOKEN '

# Создаем экземпляр бота
bot = telebot.TeleBot(BOT_TOKEN)

# Словарь для хранения истории разговора с каждым пользователем
conversation_histories = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот, который может перевернуть текст, превратить его в верхний регистр, убрать гласные, "
                          "подсчитать количество символов без пробелов и поддержать разговор на любую тему.")

@bot.message_handler(commands=['palindrom'])
def palindrom(message):
    text = message.text[11:]
    reversed_text = text[::-1]
    bot.reply_to(message, f"Перевернутый текст: {reversed_text}")

@bot.message_handler(commands=['caps'])
def caps(message):
    text = message.text[6:]
    upper_text = text.upper()
    bot.reply_to(message, f"Текст в верхнем регистре: {upper_text}")

@bot.message_handler(commands=['letter'])
def letter(message):
    text = message.text[8:]
    vowels = ['a', 'e', 'i', 'o', 'u', 'а', 'е', 'и', 'о', 'ю', 'у', 'я']
    filtered_text = ''.join([letter for letter in text if letter.lower() not in vowels])
    bot.reply_to(message, f"Текст без гласных букв: {filtered_text}")

@bot.message_handler(commands=['calc'])
def calc(message):
    text = message.text[6:]
    count = len(text.replace(" ", ""))
    bot.reply_to(message, f"Количество символов без пробелов: {count}")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    user_input = message.text

    if user_id not in conversation_histories:
        conversation_histories[user_id] = []

    conversation_history = conversation_histories[user_id]
    conversation_history.append({"role": "user", "content": user_input})

    chat_completion = openai_client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=conversation_history
    )

    ai_response_content = chat_completion.choices[0].message.content

    tts = gTTS(ai_response_content, lang='ru')
    temp_file = "temp_audio.mp3"
    tts.save(temp_file)

    with open(temp_file, 'rb') as audio:
        bot.send_voice(message.chat.id, audio)

    os.remove(temp_file)

    conversation_history.append({"role": "system", "content": ai_response_content})
