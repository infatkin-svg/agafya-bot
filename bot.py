import http.server
import os
import socketserver
import threading
import telebot
from telebot import types

# 1. ТОКЕН БОТА И АДМИН
BOT_TOKEN = "8839565108:AAFdePAaAR786LZgsjooEgR9CB-9-BhBngM"
MY_ID = 716432345

bot = telebot.TeleBot(BOT_TOKEN)

# Пути к файлам
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_PATH = os.path.join(BASE_DIR, "obereg.mp3")
PDF_PATH = os.path.join(BASE_DIR, "glava1.pdf")
PDF_CHAPTER_2_PATH = os.path.join(BASE_DIR, "glava2.pdf")
PDF_CHAPTER_3_PATH = os.path.join(BASE_DIR, "glava3.pdf")
PDF_CHAPTER_4_PATH = os.path.join(BASE_DIR, "glava4.pdf")
PDF_CHAPTER_5_PATH = os.path.join(BASE_DIR, "glava5.pdf")
PDF_CHAPTER_6_1_PATH = os.path.join(BASE_DIR, "glava6_1.pdf")
PDF_CHAPTER_6_2_PATH = os.path.join(BASE_DIR, "glava6_2.pdf")
PDF_CHAPTER_6_3_PATH = os.path.join(BASE_DIR, "glava6_3.pdf")
PDF_CHAPTER_6_4_PATH = os.path.join(BASE_DIR, "glava6_4.pdf")
PDF_CHAPTER_7_PATH = os.path.join(BASE_DIR, "glava7.pdf")
PDF_CHAPTER_8_PATH = os.path.join(BASE_DIR, "glava8.pdf")
PDF_CHAPTER_9_PATH = os.path.join(BASE_DIR, "glava9.pdf")


# --- Вспомогательная функция отправки файлов ---
def safe_send_doc(chat_id, file_path, caption_text, err_msg):
    if os.path.exists(file_path):
        with open(file_path, "rb") as doc:
            bot.send_document(chat_id, doc, caption=caption_text)
    else:
        bot.send_message(chat_id, err_msg)


# --- КОМАНДА /START ---
@bot.message_handler(commands=["start"])
def send_welcome(message):
    chat_id = message.chat.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name or ""

    welcome_text = (
        f"Здравствуйте, родные! Рада, что вы заглянули в мою избушку. 🌿\n\n"
        "Проходите, располагайтесь у очага. Я приготовила для вас кое-что особое "
        "для уюта, здоровья и защиты дома.\n\n"
        "Выберите ниже, с чего хотите начать, или просто напишите свой вопрос прямо сюда в чат "
        "— я обязательно прочту и отвечу вам! 🤎"
    )

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(text="🎧 Получить Звуковой Оберег", callback_data="get_obereg"),
        types.InlineKeyboardButton(text="📖 Читать 1-ю главу (PDF)", callback_data="get_chapter_1"),
        types.InlineKeyboardButton(text="📖 Читать 2-ю главу (PDF)", callback_data="get_chapter_2"),
        types.InlineKeyboardButton(text="📖 Читать 3-ю главу (PDF)", callback_data="get_chapter_3"),
        types.InlineKeyboardButton(text="📖 Читать 4-ю главу (PDF)", callback_data="get_chapter_4"),
        types.InlineKeyboardButton(text="📖 Читать 5-ю главу (PDF)", callback_data="get_chapter_5"),
        types.InlineKeyboardButton(text="🌿 Глава 6/1: Отёки и лимфа (PDF)", callback_data="get_chapter_6_1"),
        types.InlineKeyboardButton(text="🌿 Глава 6/2: Вздутый живот (PDF)", callback_data="get_chapter_6_2"),
        types.InlineKeyboardButton(text="🌿 Глава 6/3: Суставы и желчь (PDF)", callback_data="get_chapter_6_3"),
        types.InlineKeyboardButton(text="🌿 Глава 6/4: Полный разгон лимфы (PDF)", callback_data="get_chapter_6_4"),
        types.InlineKeyboardButton(text="🌿 Глава 7: Таёжный щит для спины и грыжи (PDF)", callback_data="get_chapter_7"),
        types.InlineKeyboardButton(text="🌸 Глава 8: Женский сбор от приливов и жара (PDF)", callback_data="get_chapter_8"),
        types.InlineKeyboardButton(text="🌿 Глава 9: Корень солодки от тёмных пятнышек (PDF)", callback_data="get_chapter_9"),
    )

    try:
        bot.send_message(chat_id, welcome_text, reply_markup=keyboard)

        # Запись в users.txt
        try:
            with open("users.txt", "a+", encoding="utf-8") as f:
                f.seek(0)
                existing_users = f.read()
                user_entry = f"{chat_id}|@{username}|{first_name}\n"
                if str(chat_id) not in existing_users:
                    f.write(user_entry)
        except Exception as fs_error:
            print(f"Ошибка записи: {fs_error}")

        # Уведомление владельцу
        user_link = f"@{username}" if username else f"ID: {chat_id}"
        notification = (
            "🔔 <b>Новый гость в избушке!</b>\n"
            f"👤 Имя: {first_name} {last_name}\n"
            f"🔗 Профиль: {user_link}\n"
            f"🆔 Чат ID: {chat_id}"
        )
        bot.send_message(MY_ID, notification, parse_mode="HTML")

    except Exception as e:
        print(f"Ошибка при старте: {e}")


# --- ОБРАБОТКА ВОПРОСОВ И ОТВЕТОВ (ОБРАТНАЯ СВЯЗЬ) ---

# 1. Ответ админа пользователю (через Reply)
@bot.message_handler(func=lambda m: m.chat.id == MY_ID and m.reply_to_message is not None)
def handle_admin_reply(message):
    try:
        reply_text = message.reply_to_message.text or message.reply_to_message.caption or ""
        target_chat_id = None
        for line in reply_text.split("\n"):
            if "🆔 ID:" in line:
                target_chat_id = line.split("🆔 ID:")[1].strip()
                break

        if target_chat_id:
            bot.copy_message(chat_id=target_chat_id, from_chat_id=MY_ID, message_id=message.message_id)
            bot.send_message(MY_ID, "✅ Ответ успешно отправлен пользователю от имени Агафьи!")
        else:
            bot.send_message(MY_ID, "⚠️ Не удалось определить ID. Отвечайте на карточку с вопросом.")
    except Exception as e:
        bot.send_message(MY_ID, f"❌ Ошибка отправки: {e}")


# 2. Вопросы от пользователей (пересылка админу)
@bot.message_handler(func=lambda m: m.chat.id != MY_ID)
def forward_user_question(message):
    chat_id = message.chat.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name or ""
    user_link = f"@{username}" if username else "без юзернейма"

    info_card = (
        "💬 <b>Новое сообщение от гостя!</b>\n"
        f"👤 Имя: {first_name} {last_name} ({user_link})\n"
        f"🆔 ID: {chat_id}\n\n"
        "<i>Нажмите «Ответить» (Reply) на это сообщение, чтобы написать человеку!</i>"
    )

    try:
        bot.send_message(MY_ID, info_card, parse_mode="HTML")
        bot.copy_message(chat_id=MY_ID, from_chat_id=chat_id, message_id=message.message_id)
        bot.send_message(chat_id, "Благодарю за весточку, родная! 🌿 Я приняла твой вопрос и скоро отвечу.")
    except Exception as e:
        print(f"Ошибка пересылки: {e}")


# --- ОБРАБОТКА КНОПОК ---
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    data = call.data
    try:
        bot.answer_callback_query(call.id)

        if data == "get_obereg":
            obereg_text = (
                "Ниже прикрепила ваш Звуковой Оберег \"Сумерки в избушке\". Это 7 минут "
                "мягкого шуршания таежного костра, скрипа половиц и сибирского ветра. "
                "Включайте его перед сном, надевайте наушники и пускай все тревоги "
                "этого дня останутся за порогом.\n\n"
                "Доброй и мирной вам ночи! Спасайтесь покоем. ✨"
            )
            bot.send_message(chat_id, obereg_text)
            if os.path.exists(AUDIO_PATH):
                with open(AUDIO_PATH, "rb") as audio:
                    bot.send_audio(
                        chat_id,
                        audio,
                        caption="✨ Твой Звуковой Оберег от Агафьи",
                        title="Сумерки в избушке",
                        performer="Агафья Травница",
                    )
            else:
                bot.send_message(chat_id, "⚠️ Ой, звуковой файл obereg.mp3 не найден!")

        elif data == "get_chapter_1":
            safe_send_doc(chat_id, PDF_PATH, "📖 Первая глава от Агафьи. Приятного чтения!", "⚠️ Файл glava1.pdf не найден!")
        elif data == "get_chapter_2":
            safe_send_doc(chat_id, PDF_CHAPTER_2_PATH, "📖 Вторая глава «Домашней тетради».", "⚠️ Файл glava2.pdf не найден!")
        elif data == "get_chapter_3":
            safe_send_doc(chat_id, PDF_CHAPTER_3_PATH, "📖 Третья глава «Домашней тетради».", "⚠️ Файл glava3.pdf не найден!")
        elif data == "get_chapter_4":
            safe_send_doc(chat_id, PDF_CHAPTER_4_PATH, "📖 Четвертая глава «Домашней тетради».", "⚠️ Файл glava4.pdf не найден!")
        elif data == "get_chapter_5":
            safe_send_doc(chat_id, PDF_CHAPTER_5_PATH, "📖 Пятая глава «Домашней тетради» — про опасные вещи и очищение дома.", "⚠️ Файл glava5.pdf не найден!")
        elif data == "get_chapter_6_1":
            safe_send_doc(chat_id, PDF_CHAPTER_6_1_PATH, "🌿 Глава № 6/1 «Свод таёжных правил: Отёк и мешки под глазами».", "⚠️ Файл glava6_1.pdf не найден!")
        elif data == "get_chapter_6_2":
            safe_send_doc(chat_id, PDF_CHAPTER_6_2_PATH, "🌿 Глава № 6/2 «Свод таёжных правил: Вздутый живот — не жир».", "⚠️ Файл glava6_2.pdf не найден!")
        elif data == "get_chapter_6_3":
            safe_send_doc(chat_id, PDF_CHAPTER_6_3_PATH, "🌿 Глава № 6/3 «Свод таёжных правил: Ломота в суставах и чистка печени».", "⚠️ Файл glava6_3.pdf не найден!")
        elif data == "get_chapter_6_4":
            safe_send_doc(chat_id, PDF_CHAPTER_6_4_PATH, "🌿 Глава № 6/4 «Свод таёжных правил: Разгон лимфы и лёгкость тела».", "⚠️ Файл glava6_4.pdf не найден!")
        elif data == "get_chapter_7":
            safe_send_doc(chat_id, PDF_CHAPTER_7_PATH, "🌿 Глава № 7 «Таёжный щит для позвоночника».", "⚠️ Файл glava7.pdf не найден!")
        elif data == "get_chapter_8":
            safe_send_doc(chat_id, PDF_CHAPTER_8_PATH, "🌸 Глава № 8 «Женский таёжный покров: Как потушить приливы и жар».", "⚠️ Файл glava8.pdf не найден!")
        elif data == "get_chapter_9":
            safe_send_doc(chat_id, PDF_CHAPTER_9_PATH, "🌿 Глава № 9 «Следы солнца: старый рецепт с корнем солодки от тёмных пятнышек».", "⚠️ Файл glava9.pdf не найден!")

    except Exception as e:
        print(f"Ошибка колбэка: {e}")


# --- ВЕБ-СЕРВЕР ДЛЯ РЕНДЕРА ---
def run_dummy_server():
    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")

    port = int(os.environ.get("PORT", 10000))
    try:
        with socketserver.TCPServer(("", port), Handler) as httpd:
            httpd.serve_forever()
    except Exception as server_error:
        print(f"Ошибка сервера: {server_error}")


if __name__ == "__main__":
    threading.Thread(target=run_dummy_server, daemon=True).start()
    print("Агафья запущена...")
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"Сбой сети: {e}")
