import http.server
import os
import socketserver
import sqlite3
import threading
import time
from datetime import datetime

import telebot
from telebot import types


# ============================================================
# 1. ТОКЕН БОТА И АДМИН
# ============================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
MY_ID = 716432345

bot = telebot.TeleBot(BOT_TOKEN)


# ============================================================
# 2. ПУТИ К ФАЙЛАМ
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "users.db")
MASTER_USERS_PATH = os.path.join(BASE_DIR, "users_master.txt")

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

# НОВАЯ ГЛАВА №10
PDF_CHAPTER_10_PATH = os.path.join(BASE_DIR, "glava10.pdf")

# НОВАЯ ГЛАВА №11
PDF_CHAPTER_11_PATH = os.path.join(BASE_DIR, "glava11.pdf")


# ============================================================
# 3. MASTER-СПИСОК ПОЛЬЗОВАТЕЛЕЙ
# ============================================================

def load_master_users():
    """Читает уникальные Telegram chat_id из users_master.txt."""
    users = set()

    if not os.path.exists(MASTER_USERS_PATH):
        print("ВНИМАНИЕ: users_master.txt не найден")
        return []

    try:
        with open(MASTER_USERS_PATH, "r", encoding="utf-8-sig") as f:
            for line in f:
                value = line.strip()

                if not value:
                    continue

                if value.isdigit():
                    users.add(int(value))
                else:
                    print(f"Пропущена некорректная строка users_master.txt: {value}")

    except Exception as e:
        print(f"Ошибка чтения users_master.txt: {e}")
        return []

    result = sorted(users)
    print(f"Master-список загружен: {len(result)} пользователей")
    return result


INITIAL_GUESTS = load_master_users()


# ============================================================
# 4. БАЗА ДАННЫХ
# ============================================================

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Основная таблица пользователей
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT
        )
        """
    )

    # --------------------------------------------------------
    # Обновляем СТАРУЮ базу, не удаляя существующих людей.
    # Добавляем created_at и source, если этих полей ещё нет.
    # --------------------------------------------------------

    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]

    if "created_at" not in columns:
        cursor.execute(
            """
            ALTER TABLE users
            ADD COLUMN created_at TEXT
            """
        )

    if "source" not in columns:
        cursor.execute(
            """
            ALTER TABLE users
            ADD COLUMN source TEXT
            """
        )

    # --------------------------------------------------------
    # Таблица событий
    #
    # Здесь будем видеть:
    # START
    # CHAPTER_10
    # CHAPTER_11
    #
    # А завтра можно добавить:
    # OFFER_299
    # PAY_CLICK
    # PAID
    # --------------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            event TEXT,
            source TEXT,
            created_at TEXT
        )
        """
    )

    # Наполняем базу прошлыми гостями
    for gid in INITIAL_GUESTS:
        cursor.execute(
            """
            INSERT OR IGNORE INTO users
            (chat_id, username, first_name, created_at, source)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                gid,
                "",
                "Старый гость",
                "",
                "old_guest",
            ),
        )

    conn.commit()
    conn.close()


def add_user(chat_id, username, first_name, source="direct"):
    """
    Добавляет нового человека.

    Если человек уже есть в базе:
    обновляем username/имя,
    но НЕ перезаписываем первый источник прихода.
    """

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(
            """
            SELECT chat_id, source
            FROM users
            WHERE chat_id = ?
            """,
            (chat_id,),
        )

        existing = cursor.fetchone()

        if existing is None:
            cursor.execute(
                """
                INSERT INTO users
                (
                    chat_id,
                    username,
                    first_name,
                    created_at,
                    source
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    chat_id,
                    username or "",
                    first_name or "",
                    now,
                    source,
                ),
            )

        else:
            cursor.execute(
                """
                UPDATE users
                SET username = ?,
                    first_name = ?
                WHERE chat_id = ?
                """,
                (
                    username or "",
                    first_name or "",
                    chat_id,
                ),
            )

        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Ошибка БД add_user: {e}")


def log_event(chat_id, event, source=""):
    """
    Записываем действия пользователя.
    """

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(
            """
            INSERT INTO events
            (
                chat_id,
                event,
                source,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                chat_id,
                event,
                source,
                now,
            ),
        )

        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Ошибка БД log_event: {e}")


def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT chat_id
        FROM users
        """
    )

    rows = cursor.fetchall()

    conn.close()

    return [r[0] for r in rows]


# Запускаем/обновляем базу
init_db()


# ============================================================
# 5. ОТПРАВКА PDF
# ============================================================

def safe_send_doc(chat_id, file_path, caption_text, err_msg):
    if os.path.exists(file_path):

        with open(file_path, "rb") as doc:
            bot.send_document(
                chat_id,
                doc,
                caption=caption_text,
            )

    else:
        bot.send_message(
            chat_id,
            err_msg,
        )


# ============================================================
# 6. СТАТИСТИКА ПОЛЬЗОВАТЕЛЕЙ
# ============================================================

@bot.message_handler(commands=["users"])
def users_stats(message):

    if message.chat.id != MY_ID:
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM users
            WHERE source = 'old_guest'
            """
        )
        master_users = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM users
            WHERE source IS NOT NULL
              AND source != ''
              AND source != 'old_guest'
            """
        )
        tracked_users = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(DISTINCT chat_id)
            FROM events
            WHERE event = 'START'
            """
        )
        started_users = cursor.fetchone()[0]

        conn.close()

        bot.send_message(
            MY_ID,
            "👥 <b>Пользователи Агафьи</b>\n\n"
            f"Всего в базе: <b>{total_users}</b>\n"
            f"Импортировано из master: <b>{master_users}</b>\n"
            f"С известным новым источником: <b>{tracked_users}</b>\n"
            f"Зафиксирован START в events: <b>{started_users}</b>",
            parse_mode="HTML",
        )

    except Exception as e:
        bot.send_message(
            MY_ID,
            f"❌ Ошибка статистики: {e}",
        )


# ============================================================
# 7. МАССОВАЯ РАССЫЛКА
# ============================================================

@bot.message_handler(commands=["broadcast"])
def broadcast_message(message):

    if message.chat.id != MY_ID:
        return

    raw_text = message.text.replace(
        "/broadcast",
        "",
        1,
    ).strip()

    if not raw_text:

        bot.send_message(
            MY_ID,
            "⚠️ <b>Текст рассылки пуст!</b>\n\n"
            "Использование: "
            "<code>/broadcast Ваш текст</code>",
            parse_mode="HTML",
        )

        return

    user_ids = get_all_users()

    success_count = 0
    fail_count = 0

    bot.send_message(
        MY_ID,
        f"🚀 Начинаю рассылку по "
        f"{len(user_ids)} пользователям...",
    )

    for uid in user_ids:

        try:
            bot.send_message(
                uid,
                raw_text,
            )

            success_count += 1

            time.sleep(0.05)

        except Exception as e:

            fail_count += 1

            print(
                f"Ошибка отправки {uid}: {e}"
            )

    report = (
        "✅ <b>Рассылка завершена!</b>\n\n"
        f"📨 Успешно доставлено: {success_count}\n"
        f"❌ Не доставлено: {fail_count}"
    )

    bot.send_message(
        MY_ID,
        report,
        parse_mode="HTML",
    )


# ============================================================
# 8. /START
# ============================================================

@bot.message_handler(commands=["start"])
def send_welcome(message):

    chat_id = message.chat.id

    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name or ""

    # --------------------------------------------------------
    # Определяем источник.
    #
    # Обычная ссылка:
    # t.me/Agafya_Travnitsa_bot
    #
    # Ссылка из ManyChat:
    # t.me/Agafya_Travnitsa_bot?start=zhivot
    # --------------------------------------------------------

    parts = message.text.split(
        maxsplit=1
    )

    source = "direct"

    if len(parts) > 1:
        source = parts[1].strip().lower()

    # Сохраняем пользователя
    add_user(
        chat_id,
        username,
        first_name,
        source,
    )

    # Фиксируем START
    log_event(
        chat_id,
        "START",
        source,
    )

    welcome_text = (
        "Здравствуйте, родные! "
        "Рада, что вы заглянули в мою избушку. 🌿\n\n"

        "Проходите, располагайтесь у очага. "
        "Я приготовила для вас кое-что особое "
        "для уюта, здоровья и защиты дома.\n\n"

        "Выберите ниже, с чего хотите начать, "
        "или просто напишите свой вопрос прямо сюда в чат "
        "— я обязательно прочту и отвечу вам! 🤎"
    )

    keyboard = types.InlineKeyboardMarkup(
        row_width=1
    )

    keyboard.add(

        types.InlineKeyboardButton(
            text="🎧 Получить Звуковой Оберег",
            callback_data="get_obereg",
        ),

        types.InlineKeyboardButton(
            text="📖 Читать 1-ю главу (PDF)",
            callback_data="get_chapter_1",
        ),

        types.InlineKeyboardButton(
            text="📖 Читать 2-ю главу (PDF)",
            callback_data="get_chapter_2",
        ),

        types.InlineKeyboardButton(
            text="📖 Читать 3-ю главу (PDF)",
            callback_data="get_chapter_3",
        ),

        types.InlineKeyboardButton(
            text="📖 Читать 4-ю главу (PDF)",
            callback_data="get_chapter_4",
        ),

        types.InlineKeyboardButton(
            text="📖 Читать 5-ю главу (PDF)",
            callback_data="get_chapter_5",
        ),

        types.InlineKeyboardButton(
            text="🌿 Глава 6/1: Отёки и лимфа (PDF)",
            callback_data="get_chapter_6_1",
        ),

        types.InlineKeyboardButton(
            text="🌿 Глава 6/2: Вздутый живот (PDF)",
            callback_data="get_chapter_6_2",
        ),

        types.InlineKeyboardButton(
            text="🌿 Глава 6/3: Суставы и желчь (PDF)",
            callback_data="get_chapter_6_3",
        ),

        types.InlineKeyboardButton(
            text="🌿 Глава 6/4: Полный разгон лимфы (PDF)",
            callback_data="get_chapter_6_4",
        ),

        types.InlineKeyboardButton(
            text="🌿 Глава 7: Таёжный щит для спины и грыжи (PDF)",
            callback_data="get_chapter_7",
        ),

        types.InlineKeyboardButton(
            text="🌸 Глава 8: Женский сбор от приливов и жара (PDF)",
            callback_data="get_chapter_8",
        ),

        types.InlineKeyboardButton(
            text="🌿 Глава 9: Корень солодки от тёмных пятнышек (PDF)",
            callback_data="get_chapter_9",
        ),

        # НОВАЯ КНОПКА
        types.InlineKeyboardButton(
            text="🌿 Глава 10: Лёгкий живот и псиллиум (PDF)",
            callback_data="get_chapter_10",
        ),

        types.InlineKeyboardButton(
            text="🌸 Глава 11: Женская чистота — 5 вещей, которые лучше не делать (PDF)",
            callback_data="get_chapter_11",
        ),
    )

    try:

        bot.send_message(
            chat_id,
            welcome_text,
            reply_markup=keyboard,
        )

        # Deep-link ?start=uhod — сразу выдаём главу №11
        if source == "uhod":
            log_event(
                chat_id,
                "CHAPTER_11",
                "uhod",
            )

            safe_send_doc(
                chat_id,
                PDF_CHAPTER_11_PATH,
                "🌸 Глава № 11 «Женская чистота: 5 вещей, которые лучше не делать».",
                "⚠️ Файл glava11.pdf не найден!",
            )

        # Уведомление владельцу

        user_link = (
            f"@{username}"
            if username
            else f"ID: {chat_id}"
        )

        notification = (
            "🔔 <b>Новый гость в избушке!</b>\n"
            f"👤 Имя: {first_name} {last_name}\n"
            f"🔗 Профиль: {user_link}\n"
            f"🆔 Чат ID: {chat_id}\n"
            f"📍 Источник: {source}"
        )

        bot.send_message(
            MY_ID,
            notification,
            parse_mode="HTML",
        )

    except Exception as e:

        print(
            f"Ошибка при старте: {e}"
        )


# ============================================================
# 9. ОТВЕТ АДМИНА ПОЛЬЗОВАТЕЛЮ
# ============================================================

@bot.message_handler(
    func=lambda m:
        m.chat.id == MY_ID
        and m.reply_to_message is not None
)
def handle_admin_reply(message):

    try:

        reply_text = (
            message.reply_to_message.text
            or message.reply_to_message.caption
            or ""
        )

        target_chat_id = None

        for line in reply_text.split("\n"):

            if "🆔 ID:" in line:

                target_chat_id = (
                    line.split("🆔 ID:")[1]
                    .strip()
                )

                break

            elif "🆔 Чат ID:" in line:

                target_chat_id = (
                    line.split("🆔 Чат ID:")[1]
                    .strip()
                )

                break

        if target_chat_id:

            bot.copy_message(
                chat_id=target_chat_id,
                from_chat_id=MY_ID,
                message_id=message.message_id,
            )

            bot.send_message(
                MY_ID,
                "✅ Ответ успешно отправлен "
                "пользователю от имени Агафьи!",
            )

        else:

            bot.send_message(
                MY_ID,
                "⚠️ Не удалось определить ID. "
                "Отвечайте на карточку с вопросом.",
            )

    except Exception as e:

        bot.send_message(
            MY_ID,
            f"❌ Ошибка отправки: {e}",
        )


# ============================================================
# 10. СООБЩЕНИЯ ПОЛЬЗОВАТЕЛЕЙ
# ============================================================

@bot.message_handler(
    func=lambda m: m.chat.id != MY_ID
)
def forward_user_question(message):

    chat_id = message.chat.id

    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name or ""

    user_link = (
        f"@{username}"
        if username
        else "без юзернейма"
    )

    # Добавляем человека в БД,
    # если он почему-то написал без /start

    add_user(
        chat_id,
        username,
        first_name,
        "message",
    )

    info_card = (
        "💬 <b>Новое сообщение от гостя!</b>\n"
        f"👤 Имя: {first_name} {last_name} "
        f"({user_link})\n"
        f"🆔 ID: {chat_id}\n\n"
        "<i>Нажмите «Ответить» (Reply) "
        "на это сообщение, чтобы написать человеку!</i>"
    )

    try:

        bot.send_message(
            MY_ID,
            info_card,
            parse_mode="HTML",
        )

        bot.copy_message(
            chat_id=MY_ID,
            from_chat_id=chat_id,
            message_id=message.message_id,
        )

        bot.send_message(
            chat_id,
            "Благодарю за весточку, родная! 🌿 "
            "Я приняла твой вопрос и скоро отвечу.",
        )

    except Exception as e:

        print(
            f"Ошибка пересылки: {e}"
        )


# ============================================================
# 11. КНОПКИ
# ============================================================

@bot.callback_query_handler(
    func=lambda call: True
)
def handle_callbacks(call):

    chat_id = call.message.chat.id
    data = call.data

    try:

        bot.answer_callback_query(
            call.id
        )

        # ----------------------------------------------------
        # ОБЕРЕГ
        # ----------------------------------------------------

        if data == "get_obereg":

            obereg_text = (
                'Ниже прикрепила ваш Звуковой Оберег '
                '"Сумерки в избушке". Это 7 минут '
                "мягкого шуршания таежного костра, "
                "скрипа половиц и сибирского ветра. "
                "Включайте его перед сном, "
                "надевайте наушники и пускай все тревоги "
                "этого дня останутся за порогом.\n\n"
                "Доброй и мирной вам ночи! "
                "Спасайтесь покоем. ✨"
            )

            bot.send_message(
                chat_id,
                obereg_text,
            )

            if os.path.exists(
                AUDIO_PATH
            ):

                with open(
                    AUDIO_PATH,
                    "rb",
                ) as audio:

                    bot.send_audio(
                        chat_id,
                        audio,
                        caption=(
                            "✨ Твой Звуковой Оберег "
                            "от Агафьи"
                        ),
                        title="Сумерки в избушке",
                        performer="Агафья Травница",
                    )

            else:

                bot.send_message(
                    chat_id,
                    "⚠️ Ой, звуковой файл "
                    "obereg.mp3 не найден!",
                )

        # ----------------------------------------------------
        # ГЛАВЫ
        # ----------------------------------------------------

        elif data == "get_chapter_1":

            safe_send_doc(
                chat_id,
                PDF_PATH,
                "📖 Первая глава от Агафьи. "
                "Приятного чтения!",
                "⚠️ Файл glava1.pdf не найден!",
            )

        elif data == "get_chapter_2":

            safe_send_doc(
                chat_id,
                PDF_CHAPTER_2_PATH,
                "📖 Вторая глава «Домашней тетради».",
                "⚠️ Файл glava2.pdf не найден!",
            )

        elif data == "get_chapter_3":

            safe_send_doc(
                chat_id,
                PDF_CHAPTER_3_PATH,
                "📖 Третья глава «Домашней тетради».",
                "⚠️ Файл glava3.pdf не найден!",
            )

        elif data == "get_chapter_4":

            safe_send_doc(
                chat_id,
                PDF_CHAPTER_4_PATH,
                "📖 Четвертая глава «Домашней тетради».",
                "⚠️ Файл glava4.pdf не найден!",
            )

        elif data == "get_chapter_5":

            safe_send_doc(
                chat_id,
                PDF_CHAPTER_5_PATH,
                "📖 Пятая глава «Домашней тетради» "
                "— про опасные вещи и очищение дома.",
                "⚠️ Файл glava5.pdf не найден!",
            )

        elif data == "get_chapter_6_1":

            safe_send_doc(
                chat_id,
                PDF_CHAPTER_6_1_PATH,
                "🌿 Глава № 6/1 "
                "«Свод таёжных правил: "
                "Отёк и мешки под глазами».",
                "⚠️ Файл glava6_1.pdf не найден!",
            )

        elif data == "get_chapter_6_2":

            safe_send_doc(
                chat_id,
                PDF_CHAPTER_6_2_PATH,
                "🌿 Глава № 6/2 "
                "«Свод таёжных правил: "
                "Вздутый живот — не жир».",
                "⚠️ Файл glava6_2.pdf не найден!",
            )

        elif data == "get_chapter_6_3":

            safe_send_doc(
                chat_id,
                PDF_CHAPTER_6_3_PATH,
                "🌿 Глава № 6/3 "
                "«Свод таёжных правил: "
                "Ломота в суставах и чистка печени».",
                "⚠️ Файл glava6_3.pdf не найден!",
            )

        elif data == "get_chapter_6_4":

            safe_send_doc(
                chat_id,
                PDF_CHAPTER_6_4_PATH,
                "🌿 Глава № 6/4 "
                "«Свод таёжных правил: "
                "Разгон лимфы и лёгкость тела».",
                "⚠️ Файл glava6_4.pdf не найден!",
            )

        elif data == "get_chapter_7":

            safe_send_doc(
                chat_id,
                PDF_CHAPTER_7_PATH,
                "🌿 Глава № 7 "
                "«Таёжный щит для позвоночника».",
                "⚠️ Файл glava7.pdf не найден!",
            )

        elif data == "get_chapter_8":

            safe_send_doc(
                chat_id,
                PDF_CHAPTER_8_PATH,
                "🌸 Глава № 8 "
                "«Женский таёжный покров: "
                "Как потушить приливы и жар».",
                "⚠️ Файл glava8.pdf не найден!",
            )

        elif data == "get_chapter_9":

            safe_send_doc(
                chat_id,
                PDF_CHAPTER_9_PATH,
                "🌿 Глава № 9 "
                "«Следы солнца: старый рецепт "
                "с корнем солодки "
                "от тёмных пятнышек».",
                "⚠️ Файл glava9.pdf не найден!",
            )

        # ----------------------------------------------------
        # НОВАЯ ГЛАВА №10
        # ----------------------------------------------------

        elif data == "get_chapter_10":

            # Записываем, что человек реально
            # нажал и запросил главу №10

            log_event(
                chat_id,
                "CHAPTER_10",
                "button",
            )

            safe_send_doc(
                chat_id,
                PDF_CHAPTER_10_PATH,
                "🌿 Глава № 10 "
                "«Когда живот встал: "
                "простой способ с псиллиумом "
                "для мягкой работы кишечника».",
                "⚠️ Файл glava10.pdf не найден!",
            )

        # ----------------------------------------------------
        # НОВАЯ ГЛАВА №11
        # ----------------------------------------------------

        elif data == "get_chapter_11":

            log_event(
                chat_id,
                "CHAPTER_11",
                "button",
            )

            safe_send_doc(
                chat_id,
                PDF_CHAPTER_11_PATH,
                "🌸 Глава № 11 "
                "«Женская чистота: "
                "5 вещей, которые лучше не делать».",
                "⚠️ Файл glava11.pdf не найден!",
            )

    except Exception as e:

        print(
            f"Ошибка колбэка: {e}"
        )


# ============================================================
# 12. ВЕБ-СЕРВЕР ДЛЯ RENDER
# ============================================================

def run_dummy_server():

    class Handler(
        http.server.SimpleHTTPRequestHandler
    ):

        def do_GET(self):

            self.send_response(200)
            self.end_headers()

            self.wfile.write(
                b"OK"
            )

    port = int(
        os.environ.get(
            "PORT",
            10000,
        )
    )

    try:

        with socketserver.TCPServer(
            ("", port),
            Handler,
        ) as httpd:

            httpd.serve_forever()

    except Exception as server_error:

        print(
            f"Ошибка сервера: "
            f"{server_error}"
        )


# ============================================================
# 13. ЗАПУСК
# ============================================================

if __name__ == "__main__":

    threading.Thread(
        target=run_dummy_server,
        daemon=True,
    ).start()

    print(
        "Агафья запущена..."
    )

    try:

        bot.infinity_polling(
            timeout=10,
            long_polling_timeout=5,
        )

    except Exception as e:

        print(
            f"Сбой сети: {e}"
        )
