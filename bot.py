import http.server
import os
import socketserver
import threading
import telebot
from telebot import types

# 1. ВСТАВЬ СЮДА СВОЙ ТОКЕН В КАВЫЧКАХ
BOT_TOKEN = "8839565108:AAFdePAaAR786LZgsjooEgR9CB-9-BhBngM"

# 2. Твой Telegram ID
MY_ID = 716432345

bot = telebot.TeleBot(BOT_TOKEN)

# Пути к файлам (они должны лежать в папке с bot.py)
AUDIO_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "obereg.mp3"
)
PDF_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "glava1.pdf"
)
PDF_CHAPTER_2_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "glava2.pdf"
)
PDF_CHAPTER_3_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "glava3.pdf"
)


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
        " для уюта и защиты дома.\n\n"
        "Выберите ниже, с чего хотите начать:"
    )

    # Четыре кнопки
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    btn_obereg = types.InlineKeyboardButton(
        text="🎧 Получить Звуковой Оберег", callback_data="get_obereg"
    )
    btn_chapter_1 = types.InlineKeyboardButton(
        text="📖 Читать 1-ю главу (PDF)", callback_data="get_chapter_1"
    )
    btn_chapter_2 = types.InlineKeyboardButton(
        text="📖 Читать 2-ю главу (PDF)", callback_data="get_chapter_2"
    )
    btn_chapter_3 = types.InlineKeyboardButton(
        text="📖 Читать 3-ю главу (PDF)", callback_data="get_chapter_3"
    )
    keyboard.add(btn_obereg, btn_chapter_1, btn_chapter_2, btn_chapter_3)

    try:
        # Приветствие с кнопками
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

        # Уведомление тебе
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


# --- НАЖАТИЕ НА "ОБЕРЕГ" ---
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
            bot.send_message(
                chat_id,
                "⚠️ Ой, звуковой файл obereg.mp3 не найден на сервере! Проверь,"
                " загружен ли он.",
            )

    except Exception as e:
        print(f"Ошибка при отправке оберега: {e}")


# --- НАЖАТИЕ НА "1 ГЛАВА" ---
@bot.callback_query_handler(func=lambda call: call.data == "get_chapter_1")
def send_chapter_1(call):
    chat_id = call.message.chat.id
    try:
        bot.answer_callback_query(call.id)

        if os.path.exists(PDF_PATH):
            with open(PDF_PATH, "rb") as doc:
                bot.send_document(
                    chat_id,
                    doc,
                    caption="📖 Первая глава от Агафьи. Приятного и душевного чтения!",
                )
        else:
            bot.send_message(
                chat_id,
                "⚠️ Ой, файл glava1.pdf не найден на сервере! Проверь, загружен ли"
                " файл в GitHub.",
            )

    except Exception as e:
        print(f"Ошибка при отправке PDF (Глава 1): {e}")


# --- НАЖАТИЕ НА "2 ГЛАВА" ---
@bot.callback_query_handler(func=lambda call: call.data == "get_chapter_2")
def send_chapter_2(call):
    chat_id = call.message.chat.id
    try:
        bot.answer_callback_query(call.id)

        if os.path.exists(PDF_CHAPTER_2_PATH):
            with open(PDF_CHAPTER_2_PATH, "rb") as doc:
                bot.send_document(
                    chat_id,
                    doc,
                    caption="📖 Вторая глава «Домашней тетради». Забирайте в свою копилочку уютных мудростей!",
                )
        else:
            bot.send_message(
                chat_id,
                "⚠️ Ой, файл glava2.pdf не найден на сервере! Проверь, загружен ли"
                " файл в GitHub.",
            )

    except Exception as e:
        print(f"Ошибка при отправке PDF (Глава 2): {e}")


# --- НАЖАТИЕ НА "3 ГЛАВА" ---
@bot.callback_query_handler(func=lambda call: call.data == "get_chapter_3")
def send_chapter_3(call):
    chat_id = call.message.chat.id
    try:
        bot.answer_callback_query(call.id)

        if os.path.exists(PDF_CHAPTER_3_PATH):
            with open(PDF_CHAPTER_3_PATH, "rb") as doc:
                bot.send_document(
                    chat_id,
                    doc,
                    caption="📖 Третья глава «Домашней тетради» — про свежий воздух и легкий сон. Приятного чтения!",
                )
        else:
            bot.send_message(
                chat_id,
                "⚠️ Ой, файл glava3.pdf не найден на сервере! Проверь, загружен ли"
                " файл в GitHub.",
            )

    except Exception as e:
        print(f"Ошибка при отправке PDF (Глава 3): {e}")


# --- ВЕБ-СЕРВЕР ДЛЯ RENDER ---
def run_dummy_server():
    class Handler(http.server.SimpleHTTPRequestHandler):

        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")

    port = int(os.environ.get("PORT", 10000))
    try:
        with socketserver.
