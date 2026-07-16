import telebot
import os

# 1. Вставь сюда токен твоего бота от @BotFather
BOT_TOKEN = "8839565108:AAFdePAaAR786LZgsjooEgR9CB-9-BhBngM"

# 2. Вставь сюда свой личный Telegram ID (цифры), чтобы получать уведомления.
# Получить его можно за секунду в боте @userinfobot
MY_ID = 716432345  # <--- Замени эти цифры на свой ID!

bot = telebot.TeleBot(BOT_TOKEN)

# Путь к твоему звуковому файлу оберега. 
# Положи файл со звуком костра в ту же папку, где лежит bot.py, и назови его "obereg.mp3"
AUDIO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "obereg.mp3")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name or ""
    
    # Красивый текст приветствия, как ты и просил
    welcome_text = (
        "Здравствуйте, родные! Рада, что вы заглянули в мою избушку. 🌿\n\n"
        "Сегодня особенный день, время уюта и защиты дома. Как и обещала, делюсь с вами своей заботой.\n\n"
        "Ниже прикрепила ваш Звуковой Оберег \"Сумерки в избушке\". Это 7 минут мягкого шуршания "
        "таежного костра, скрипа половиц и сибирского ветра. Включайте его перед сном, надевайте "
        "наушники и пускай все тревоги этого дня останутся за порогом.\n\n"
        "Доброй и мирной вам ночи! Спасайтесь покоем."
    )
    
    try:
        # Отправляем душевное текстовое сообщение
        bot.send_message(chat_id, welcome_text)
        
        # Отправляем звуковой оберег
        if os.path.exists(AUDIO_PATH):
            with open(AUDIO_PATH, 'rb') as audio:
                # title и performer — это то, как трек будет подписан в плеере Телеграма
                bot.send_audio(
                    chat_id, 
                    audio, 
                    caption="✨ Твой Звуковой Оберег от Агафьи",
                    title="Сумерки в избушке",
                    performer="Агафья Травница"
                )
        else:
            print(f"Ошибка: Файл {AUDIO_PATH} не найден в папке с ботом!")
            
        # Записываем пользователя в наш файлик (чтобы собирать базу)
        with open("users.txt", "a+", encoding="utf-8") as f:
            f.seek(0)
            existing_users = f.read()
            user_entry = f"{chat_id}|@{username}|{first_name}\n"
            if str(chat_id) not in existing_users:
                f.write(user_entry)
                
        # --- НАШЕ УВЕДОМЛЕНИЕ ТЕБЕ НА ТЕЛЕФОН ---
        user_link = f"@{username}" if username else f"ID: {chat_id}"
        notification = (
            "🔔 **Новый гость в избушке!**\n"
            f"👤 Имя: {first_name} {last_name}\n"
            f"🔗 Профиль: {user_link}\n"
            f"🆔 Чат ID: {chat_id}"
        )
        # Бот шлет сообщение лично тебе
        bot.send_message(MY_ID, notification, parse_mode="HTML")
        
    except Exception as e:
        print(f"Произошла ошибка при обработке команды старт: {e}")

if __name__ == "__main__":
    # 1. Сначала запускаем веб-сервер-"пустышку" для Render, чтобы он не ругался на порты
    import http.server
    import socketserver
    import threading

    def run_dummy_server():
        class Handler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"OK")
        
        import os
        port = int(os.environ.get("PORT", 10000))
        try:
            with socketserver.TCPServer(("", port), Handler) as httpd:
                print(f"Сервер-пустышка запущен на порту {port}")
                httpd.serve_forever()
        except Exception as server_error:
            print(f"Ошибка запуска сервера-пустышки: {server_error}")

    # Запускаем пустышку в отдельном фоновом потоке
    threading.Thread(target=run_dummy_server, daemon=True).start()

    # 2. Теперь спокойно запускаем самого бота
    print("Исправленная Агафья запущена и ждет гостей...")
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"Сбой сети Телеграм, ошибка: {e}")
