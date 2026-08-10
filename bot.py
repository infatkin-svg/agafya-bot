import http.server
import os
import socketserver
import threading
import telebot
from telebot import types

# 1. ТОКЕН БОТА
BOT_TOKEN = "8839565108:AAFdePAaAR786LZgsjooEgR9CB-9-BhBngM"

# 2. Твой Telegram ID
MY_ID = 716432345

bot = telebot.TeleBot(BOT_TOKEN)

# Пути к файлам (они должны лежать в одной папке с bot.py)
AUDIO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "obereg.mp3")
PDF_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "glava1.pdf")
PDF_CHAPTER_2_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "glava2.pdf")
PDF_CHAPTER_3_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "glava3.pdf")
PDF_CHAPTER_4_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "glava4.pdf")
PDF_CHAPTER_5_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "glava5.pdf")
PDF_CHAPTER_6_1_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "glava6_1.pdf")
PDF_CHAPTER_6_2_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "glava6_2.pdf")
PDF_CHAPTER_6_3_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "glava6_3.pdf")
PDF_CHAPTER_6_4_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "glava6_4.pdf")
PDF_CHAPTER_7_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "glava7.pdf")
PDF_CHAPTER_8_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "glava8.pdf")


# --- КОМАНДА /START ---
@bot.message_handler(commands=["start"])
def send_welcome(message):
    chat_id = message.chat.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name or ""

    welcome_text = (
        f"Здравствуйте, родные! Рада, что вы заглянули в мою избушку. 🌿\n\n"
        "Проходите, располагайтесь у очага. Я приготовила для вас кое-что особое"
        " для уюта, здоровья и защиты дома.\n\n"
        "Выберите ниже, с чего хотите начать:"
    )

    # Кнопки меню
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    btn_obereg = types.InlineKeyboardButton(text="🎧 Получить Звуковой Оберег", callback_data="get_obereg")
    btn_chapter_1 = types.InlineKeyboardButton(text="📖 Читать 1-ю главу (PDF)", callback_data="get_chapter_1")
    btn_chapter_2 = types.InlineKeyboardButton(text="📖 Читать 2-ю главу (PDF)", callback_data="get_chapter_2")
    btn_chapter_3 = types.InlineKeyboardButton(text="📖 Читать 3-ю главу (PDF)", callback_data="get_chapter_3")
    btn_chapter_4 = types.InlineKeyboardButton(text="📖 Читать 4-ю главу (PDF)", callback_data="get_chapter_4")
    btn_chapter_5 = types.InlineKeyboardButton(text="📖 Читать 5-ю главу (PDF)", callback_data="get_chapter_5")
    btn_chapter_6_1 = types.InlineKeyboardButton(text="🌿 Глава 6/1: Отёки и лимфа (PDF)", callback_data="get_chapter_6_1")
    btn_chapter_6_2 = types.InlineKeyboardButton(text="🌿 Глава 6/2: Вздутый живот (PDF)", callback_data="get_chapter_6_2")
    btn_chapter_6_3 = types.InlineKeyboardButton(text="🌿 Глава 6/3: Суставы и желчь (PDF)", callback_data="get_chapter_6_3")
    btn_chapter_6_4 = types.InlineKeyboardButton(text="🌿 Глава 6/4: Полный разгон лимфы (PDF)", callback_data="get_chapter_6_4")
    btn_chapter_7 = types.InlineKeyboardButton(text="🌿 Глава 7: Таёжный щит для спины и грыжи (PDF)", callback_data="get_chapter_7")
    btn_chapter_8 = types.InlineKeyboardButton(text="🌸 Глава 8: Женский сбор от приливов и жара (PDF)", callback_data="get_chapter_8")

    keyboard.add(
        btn_obereg,
        btn_chapter_1,
        btn_chapter_2,
        btn_chapter_3,
        btn_chapter_4,
        btn_chapter_5,
        btn_chapter_6_1,
        btn_chapter_6_2,
        btn_chapter_6_3,
        btn_chapter_6_4,
        btn_chapter_7,
        btn_chapter_8,
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
            print(f"Ошибка записи в файл: {fs_error}")

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


# --- ОБЕРЕГ ---
@bot.callback_query_handler(func=lambda call: call.data == "get_obereg")
def send_obereg(call):
    chat_id = call.message.chat.id
    try:
        bot.answer_callback_query(call.id)
        obereg_text = (
            "Ниже прикрепила ваш Звуковой Оберег \"Сумерки в избушке\". Это 7 минут"
            " мягкого шуршания таежного костра, скрипа половиц и сибирского ветра."
            " Включайте его перед сном, надевайте наушники и пускай все тревоги"
            " этого дня останутся за порогом.\n\n"
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
    except Exception as e:
        print(f"Ошибка оберега: {e}")


# --- 1 ГЛАВА ---
@bot.callback_query_handler(func=lambda call: call.data == "get_chapter_1")
def send_chapter_1(call):
    chat_id = call.message.chat.id
    try:
        bot.answer_callback_query(call.id)
        if os.path.exists(PDF_PATH):
            with open(PDF_PATH, "rb") as doc:
                bot.send_document(chat_id, doc, caption="📖 Первая глава от Агафьи. Приятного чтения!")
        else:
            bot.send_message(chat_id, "⚠️ Файл glava1.pdf не найден!")
    except Exception as e:
        print(f"Ошибка (Глава 1): {e}")


# --- 2 ГЛАВА ---
@bot.callback_query_handler(func=lambda call: call.data == "get_chapter_2")
def send_chapter_2(call):
    chat_id = call.message.chat.id
    try:
        bot.answer_callback_query(call.id)
        if os.path.exists(PDF_CHAPTER_2_PATH):
            with open(PDF_CHAPTER_2_PATH, "rb") as doc:
                bot.send_document(chat_id, doc, caption="📖 Вторая глава «Домашней тетради».")
        else:
            bot.send_message(chat_id, "⚠️ Файл glava2.pdf не найден!")
    except Exception as e:
        print(f"Ошибка (Глава 2): {e}")


# --- 3 ГЛАВА ---
@bot.callback_query_handler(func=lambda call: call.data == "get_chapter_3")
def send_chapter_3(call):
    chat_id = call.message.chat.id
    try:
        bot.answer_callback_query(call.id)
        if os.path.exists(PDF_CHAPTER_3_PATH):
            with open(PDF_CHAPTER_3_PATH, "rb") as doc:
                bot.send_document(chat_id, doc, caption="📖 Третья глава «Домашней тетради».")
        else:
            bot.send_message(chat_id, "⚠️ Файл glava3.pdf не найден!")
    except Exception as e:
        print(f"Ошибка (Глава 3): {e}")


# --- 4 ГЛАВА ---
@bot.callback_query_handler(func=lambda call: call.data == "get_chapter_4")
def send_chapter_4(call):
    chat_id = call.message.chat.id
    try:
        bot.answer_callback_query(call.id)
        if os.path.exists(PDF_CHAPTER_4_PATH):
            with open(PDF_CHAPTER_4_PATH, "rb") as doc:
                bot.send_document(chat_id, doc, caption="📖 Четвертая глава «Домашней тетради».")
        else:
            bot.send_message(chat_id, "⚠️ Файл glava4.pdf не найден!")
    except Exception as e:
        print(f"Ошибка (Глава 4): {e}")


# --- 5 ГЛАВА ---
@bot.callback_query_handler(func=lambda call: call.data == "get_chapter_5")
def send_chapter_5(call):
    chat_id = call.message.chat.id
    try:
        bot.answer_callback_query(call.id)
        if os.path.exists(PDF_CHAPTER_5_PATH):
            with open(PDF_CHAPTER_5_PATH, "rb") as doc:
                bot.send_document(chat_id, doc, caption="📖 Пятая глава «Домашней тетради» — про опасные вещи и очищение дома.")
        else:
            bot.send_message(chat_id, "⚠️ Файл glava5.pdf не найден!")
    except Exception as e:
        print(f"Ошибка (Глава 5): {e}")


# --- ГЛАВА 6/1 ---
@bot.callback_query_handler(func=lambda call: call.data == "get_chapter_6_1")
def send_chapter_6_1(call):
    chat_id = call.message.chat.id
    try:
        bot.answer_callback_query(call.id)
        if os.path.exists(PDF_CHAPTER_6_1_PATH):
            with open(PDF_CHAPTER_6_1_PATH, "rb") as doc:
                bot.send_document(chat_id, doc, caption="🌿 Глава № 6/1 «Свод таёжных правил: Отёк и мешки под глазами». Полезного чтения!")
        else:
            bot.send_message(chat_id, "⚠️ Файл glava6_1.pdf не найден!")
    except Exception as e:
        print(f"Ошибка (Глава 6/1): {e}")


# --- ГЛАВА 6/2 ---
@bot.callback_query_handler(func=lambda call: call.data == "get_chapter_6_2")
def send_chapter_6_2(call):
    chat_id = call.message.chat.id
    try:
        bot.answer_callback_query(call.id)
        if os.path.exists(PDF_CHAPTER_6_2_PATH):
            with open(PDF_CHAPTER_6_2_PATH, "rb") as doc:
                bot.send_document(chat_id, doc, caption="🌿 Глава № 6/2 «Свод таёжных правил: Вздутый живот — не жир». Полезного чтения!")
        else:
            bot.send_message(chat_id, "⚠️ Файл glava6_2.pdf не найден!")
    except Exception as e:
        print(f"Ошибка (Глава 6/2): {e}")


# --- ГЛАВА 6/3 ---
@bot.callback_query_handler(func=lambda call: call.data == "get_chapter_6_3")
def send_chapter_6_3(call):
    chat_id = call.message.chat.id
    try:
        bot.answer_callback_query(call.id)
        if os.path.exists(PDF_CHAPTER_6_3_PATH):
            with open(PDF_CHAPTER_6_3_PATH, "rb") as doc:
                bot.send_document(chat_id, doc, caption="🌿 Глава № 6/3 «Свод таёжных правил: Ломота в суставах и чистка печени». Полезного чтения!")
        else:
            bot.send_message(chat_id, "⚠️ Файл glava6_3.pdf не найден!")
    except Exception as e:
        print(f"Ошибка (Глава 6/3): {e}")


# --- ГЛАВА 6/4 ---
@bot.callback_query_handler(func=lambda call: call.data == "get_chapter_6_4")
def send_chapter_6_4(call):
    chat_id = call.message.chat.id
    try:
        bot.answer_callback_query(call.id)
        if os.path.exists(PDF_CHAPTER_6_4_PATH):
            with open(PDF_CHAPTER_6_4_PATH, "rb") as doc:
                bot.send_document(chat_id, doc, caption="🌿 Глава № 6/4 «Свод таёжных правил: Разгон лимфы и лёгкость тела». Полезного чтения!")
        else:
            bot.send_message(chat_id, "⚠️ Файл glava6_4.pdf не найден!")
    except Exception as e:
        print(f"Ошибка (Глава 6/4): {e}")


# --- ГЛАВА 7 ---
@bot.callback_query_handler(func=lambda call: call.data == "get_chapter_7")
def send_chapter_7(call):
    chat_id = call.message.chat.id
    try:
        bot.answer_callback_query(call.id)
        if os.path.exists(PDF_CHAPTER_7_PATH):
            with open(PDF_CHAPTER_7_PATH, "rb") as doc:
                bot.send_document(
                    chat_id,
                    doc,
                    caption="🌿 Глава № 7 «Таёжный щит для позвоночника: Как размочить усохший диск и снять защемление без уколов». Приятного и полезного чтения!",
                )
        else:
            bot.send_message(chat_id, "⚠️ Файл glava7.pdf не найден!")
    except Exception as e:
        print(f"Ошибка (Глава 7): {e}")


# --- ГЛАВА 8 ---
@bot.callback_query_handler(func=lambda call: call.data == "get_chapter_8")
def send_chapter_8(call):
    chat_id = call.message.chat.id
    try:
        bot.answer_callback_query(call.id)
        if os.path.exists(PDF_CHAPTER_8_PATH):
            with open(PDF_CHAPTER_8_PATH, "rb") as doc:
                bot.send_document(
                    chat_id,
                    doc,
                    caption="🌸 Глава № 8 «Женский таёжный покров: Как потушить приливы, жар и вернуть спокойный сон». Полезного чтения, Родная!",
                )
        else:
            bot.send_message(chat_id, "⚠️ Файл glava8.pdf не найден!")
    except Exception as e:
        print(f"Ошибка (Глава 8): {e}")


# --- ВЕБ-СЕРВЕР ДЛЯ РЕНДЕРА ИЛИ ХОСТИНГА ---
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
