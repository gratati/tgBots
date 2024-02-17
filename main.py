import os
import telebot
from gtts import gTTS
from openai import OpenAI

# Инициализация клиента API OpenAI с вашим API ключом
openai_client = OpenAI(
    api_key="sk-qY1e6pDtlVsPTYdGvIU9cr5Je6WSjtqB",  # Замените на ваш API ключ
    base_url="https://api.proxyapi.ru/openai/v1",
)

# Инициализация телеграм бота с вашим токеном
TELEGRAM_BOT_TOKEN = '6292915409:AAGD2odL0Dl5H8ND7PjlrnooadiVmsdUo50'  # Замените на токен вашего бота
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Словарь для хранения истории разговора с каждым пользователем
conversation_histories = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот, который может поддержать разговор на любую тему.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    user_input = message.text

    # Если история для пользователя не существует, создаем новую
    if user_id not in conversation_histories:
        conversation_histories[user_id] = []

    # Добавление ввода пользователя в историю разговора
    conversation_history = conversation_histories[user_id]
    conversation_history.append({"role": "user", "content": user_input})

    # Отправка запроса в нейронную сеть
    chat_completion = openai_client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=conversation_history
    )

    # Извлечение и ответ на сообщение пользователя
    ai_response_content = chat_completion.choices[0].message.content

    # Создаем объект gTTS для преобразования текста в речь
    tts = gTTS(ai_response_content, lang='ru')  # Можете изменить язык на нужный вам
    # Создаем временный файл для сохранения аудио
    temp_file = "temp_audio.mp3"
    tts.save(temp_file)

    # Отправляем аудио-сообщение пользователю
    with open(temp_file, 'rb') as audio:
        bot.send_voice(message.chat.id, audio)

    # Удаляем временный файл
    os.remove(temp_file)

    # Добавление ответа нейронной сети в историю разговора
    conversation_history.append({"role": "system", "content": ai_response_content})

if __name__ == '__main__':
    bot.infinity_polling()