# import logging
# import psycopg2
# from telegram import InlineKeyboardButton, InlineKeyboardMarkup
# from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, Filters
# from telegram.update import Update
# from datetime import datetime

# # Logging
# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Configurations
# TOKEN = '7675190858:AAGGJKFuDeL5IsM6TXPW3GW9I1X0EUzkQEY'
# ADMIN_ID = ["1926076672"]
# CHANNEL = "kinolar_kanali_top"  # Faqat username, URL emas
# KINO_CHANNEL = "kinolaruzrushind"

# # PostgreSQL Connection
# try:
#     conn = psycopg2.connect(
#         host="localhost",
#         user="postgres",
#         password="87654321",
#         dbname="username"
#     )
#     cursor = conn.cursor()
#     logger.info("PostgreSQL bazaga muvaffaqiyatli ulandi.")
# except Exception as e:
#     logger.error(f"PostgreSQL ulanishda xato: {e}")
#     conn = None

# # Create Tables
# if conn:
#     cursor.execute("""CREATE TABLE IF NOT EXISTS user_id (
#         id SERIAL PRIMARY KEY,
#         user_id VARCHAR(100),
#         step VARCHAR(200),
#         sana VARCHAR(100)
#     )""")

#     cursor.execute("""CREATE TABLE IF NOT EXISTS data (
#         id SERIAL PRIMARY KEY,
#         code VARCHAR(100),
#         file_name VARCHAR(200),
#         file_id VARCHAR(200)
#     )""")
#     conn.commit()

# # Check DB Connection
# def check_db_connection() -> bool:
#     if conn:
#         try:
#             cursor.execute("SELECT 1")
#             return True
#         except Exception as e:
#             logger.error(f"Bazaga so'rov yuborishda xato: {e}")
#             return False
#     return False

# # Helper Functions
# def is_user_subscribed(context: CallbackContext, user_id: int) -> bool:
#     try:
#         member = context.bot.get_chat_member(chat_id=f"@{CHANNEL}", user_id=user_id)
#         return member.status in ["member", "administrator", "creator"]
#     except Exception as e:
#         logger.error(f"Subscription check failed: {e}")
#         return False

# # Command Handlers
# def start(update: Update, context: CallbackContext):
#     user_id = update.effective_user.id
#     name = update.effective_user.first_name

#     # Check DB Connection
#     if not check_db_connection():
#         update.message.reply_text("⚠️ Bazaga ulanishda xatolik! Iltimos, keyinroq urinib ko‘ring.")
#         return

#     # Check subscription
#     if not is_user_subscribed(context, user_id):
#         update.message.reply_text(
#             f"🔒 <a href='https://t.me/{CHANNEL}'>Kanalga</a> obuna bo'lmasangiz botdan to'liq foydalana olmaysiz!",
#             parse_mode='HTML'
#         )
#         return

#     # Add user to DB
#     cursor.execute("SELECT * FROM user_id WHERE user_id = %s", (str(user_id),))
#     if not cursor.fetchone():
#         sana = datetime.now().strftime("%d.%m.%Y | %H:%M")
#         cursor.execute("INSERT INTO user_id (user_id, step, sana) VALUES (%s, %s, %s)", (str(user_id), '0', sana))
#         conn.commit()

#     keyboard = [[InlineKeyboardButton("🔎 Kodlarni qidirish", url=f"https://t.me/{KINO_CHANNEL}")]]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     update.message.reply_text(
#         f"👋 <b>Salom {name}!</b>\n\n<i>Marhamat, kerakli kodni yuboring:</i>", 
#         parse_mode='HTML', 
#         reply_markup=reply_markup
#     )

# # Admin Command: Add Kino
# def add_kino(update: Update, context: CallbackContext):
#     user_id = str(update.effective_user.id)
#     if user_id not in ADMIN_ID:
#         update.message.reply_text("⛔ Sizda bu buyruqni bajarishga ruxsat yo‘q.")
#         return

#     if not context.args or len(context.args) < 1:
#         update.message.reply_text("⚠️ Kino kodi va faylni yuboring.\nMisol: /add_kino 12345")
#         return

#     code = context.args[0]
#     if update.message.video:
#         file_id = update.message.video.file_id
#         file_name = update.message.video.file_name or "Noma'lum"

#         cursor.execute("INSERT INTO data (code, file_name, file_id) VALUES (%s, %s, %s)", (code, file_name, file_id))
#         conn.commit()

#         update.message.reply_text(f"✅ Kino bazaga qo‘shildi!\n\n<b>Kod:</b> {code}\n<b>Fayl:</b> {file_name}", parse_mode='HTML')
#     else:
#         update.message.reply_text("⚠️ Iltimos, kino videosini yuboring.")

# # Message Handler for Codes
# def handle_message(update: Update, context: CallbackContext):
#     user_id = update.effective_user.id
#     text = update.message.text

#     if text.isdigit():
#         cursor.execute("SELECT file_name, file_id FROM data WHERE code = %s", (text,))
#         result = cursor.fetchone()
#         if result:
#             file_name, file_id = result
#             update.message.reply_video(video=file_id, caption=f"{file_name}\n\n@{context.bot.username} <b>bot yaratish xizmati!</b>", parse_mode='HTML')
#         else:
#             update.message.reply_text(f"{text} <b>mavjud emas!</b>\n\nQayta urinib ko'ring:", parse_mode='HTML')
#     else:
#         update.message.reply_text("<b>Faqat raqamlardan foydalaning!</b>", parse_mode='HTML')

# # Admin Command: /stat
# def stat(update: Update, context: CallbackContext):
#     user_id = update.effective_user.id
#     if str(user_id) not in ADMIN_ID:
#         return

#     cursor.execute("SELECT COUNT(*) FROM user_id")
#     user_count = cursor.fetchone()[0]

#     cursor.execute("SELECT COUNT(*) FROM data")
#     kino_count = cursor.fetchone()[0]

#     update.message.reply_text(f"• <b>Foydalanuvchilar:</b> {user_count} ta\n• <b>Yuklangan kinolar:</b> {kino_count} ta", parse_mode='HTML')

# # Main Function
# def main():
#     updater = Updater(TOKEN, use_context=True)
#     dp = updater.dispatcher

#     # Handlers
#     dp.add_handler(CommandHandler("start", start))
#     dp.add_handler(CommandHandler("stat", stat))
#     dp.add_handler(CommandHandler("add_kino", add_kino))
#     dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

#     # Start Bot
#     updater.start_polling()
#     updater.idle()

# if __name__ == '__main__':
#     main()


# import logging
# import psycopg2
# from telegram import InlineKeyboardButton, InlineKeyboardMarkup
# from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, Filters
# from telegram.update import Update
# from datetime import datetime

# # Logging
# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Configurations
# TOKEN = '7675190858:AAGGJKFuDeL5IsM6TXPW3GW9I1X0EUzkQEY'
# ADMIN_ID = ["1926076672"]
# CHANNEL = "kinolar_kanali_top"  # Faqat username, URL emas
# KINO_CHANNEL = "kinolaruzrushind"

# # PostgreSQL Connection
# try:
#     conn = psycopg2.connect(
#         host="localhost",
#         user="postgres",
#         password="87654321",
#         dbname="username"
#     )
#     cursor = conn.cursor()
#     logger.info("PostgreSQL bazaga muvaffaqiyatli ulandi.")
# except Exception as e:
#     logger.error(f"PostgreSQL ulanishda xato: {e}")
#     conn = None

# # Create Tables
# if conn:
#     cursor.execute("""CREATE TABLE IF NOT EXISTS user_id (
#         id SERIAL PRIMARY KEY,
#         user_id VARCHAR(100),
#         step VARCHAR(200),
#         sana VARCHAR(100)
#     )""")

#     cursor.execute("""CREATE TABLE IF NOT EXISTS data (
#         id SERIAL PRIMARY KEY,
#         code VARCHAR(100),
#         file_name VARCHAR(200),
#         file_id VARCHAR(200)
#     )""")
#     conn.commit()

# # Check DB Connection
# def check_db_connection() -> bool:
#     if conn:
#         try:
#             cursor.execute("SELECT 1")
#             return True
#         except Exception as e:
#             logger.error(f"Bazaga so'rov yuborishda xato: {e}")
#             return False
#     return False

# # Helper Functions
# def is_user_subscribed(context: CallbackContext, user_id: int) -> bool:
#     try:
#         member = context.bot.get_chat_member(chat_id=f"@{CHANNEL}", user_id=user_id)
#         return member.status in ["member", "administrator", "creator"]
#     except Exception as e:
#         logger.error(f"Subscription check failed: {e}")
#         return False

# # Command Handlers
# def start(update: Update, context: CallbackContext):
#     user_id = update.effective_user.id
#     name = update.effective_user.first_name

#     # Check DB Connection
#     if not check_db_connection():
#         update.message.reply_text("⚠️ Bazaga ulanishda xatolik! Iltimos, keyinroq urinib ko‘ring.")
#         return

#     # Check subscription
#     if not is_user_subscribed(context, user_id):
#         update.message.reply_text(
#             f"🔒 <a href='https://t.me/{CHANNEL}'>Kanalga</a> obuna bo'lmasangiz botdan to'liq foydalana olmaysiz!",
#             parse_mode='HTML'
#         )
#         return

#     # Add user to DB
#     cursor.execute("SELECT * FROM user_id WHERE user_id = %s", (str(user_id),))
#     if not cursor.fetchone():
#         sana = datetime.now().strftime("%d.%m.%Y | %H:%M")
#         cursor.execute("INSERT INTO user_id (user_id, step, sana) VALUES (%s, %s, %s)", (str(user_id), '0', sana))
#         conn.commit()

#     keyboard = [[InlineKeyboardButton("🔎 Kodlarni qidirish", url=f"https://t.me/{KINO_CHANNEL}")]]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     update.message.reply_text(
#         f"👋 <b>Salom {name}!</b>\n\n<i>Marhamat, kerakli kodni yuboring:</i>", 
#         parse_mode='HTML', 
#         reply_markup=reply_markup
#     )

# # Admin Command: Add Kino
# def add_kino(update: Update, context: CallbackContext):
#     user_id = str(update.effective_user.id)
#     if user_id not in ADMIN_ID:
#         update.message.reply_text("⛔ Sizda bu buyruqni bajarishga ruxsat yo‘q.")
#         return

#     if not context.args or len(context.args) < 1:
#         update.message.reply_text("⚠️ Kino kodi va faylni yuboring.\nMisol: /add_kino 12345")
#         return

#     code = context.args[0]
#     if update.message.video:
#         file_id = update.message.video.file_id
#         file_name = update.message.video.file_name or "Noma'lum"

#         # Kino bazaga saqlash
#         cursor.execute("INSERT INTO data (code, file_name, file_id) VALUES (%s, %s, %s)", (code, file_name, file_id))
#         conn.commit()

#         # Kinoni Telegram kanalga yuborish
#         sent_message = context.bot.send_video(
#             chat_id=f"@{KINO_CHANNEL}",
#             video=file_id,
#             caption=f"🎬 {file_name}\n\n<b>Kino kodi:</b> <code>{code}</code>",
#             parse_mode='HTML'
#         )

#         # Admin uchun tasdiq xabari
#         update.message.reply_text(
#             f"✅ Kino bazaga va kanalda yuborildi!\n\n<b>Kod:</b> {code}\n<b>Fayl:</b> {file_name}\n<b>Kanal post:</b> <a href='https://t.me/{KINO_CHANNEL}/{sent_message.message_id}'>Ko‘rish</a>",
#             parse_mode='HTML'
#         )
#     else:
#         update.message.reply_text("⚠️ Iltimos, kino videosini yuboring.")

# # Message Handler for Codes
# def handle_message(update: Update, context: CallbackContext):
#     user_id = update.effective_user.id
#     text = update.message.text

#     if text.isdigit():
#         cursor.execute("SELECT file_name, file_id FROM data WHERE code = %s", (text,))
#         result = cursor.fetchone()
#         if result:
#             file_name, file_id = result
#             update.message.reply_video(video=file_id, caption=f"{file_name}\n\n@{context.bot.username} <b>bot yaratish xizmati!</b>", parse_mode='HTML')
#         else:
#             update.message.reply_text(f"{text} <b>mavjud emas!</b>\n\nQayta urinib ko'ring:", parse_mode='HTML')
#     else:
#         update.message.reply_text("<b>Faqat raqamlardan foydalaning!</b>", parse_mode='HTML')

# # Admin Command: /stat
# def stat(update: Update, context: CallbackContext):
#     user_id = update.effective_user.id
#     if str(user_id) not in ADMIN_ID:
#         return

#     cursor.execute("SELECT COUNT(*) FROM user_id")
#     user_count = cursor.fetchone()[0]

#     cursor.execute("SELECT COUNT(*) FROM data")
#     kino_count = cursor.fetchone()[0]

#     update.message.reply_text(f"• <b>Foydalanuvchilar:</b> {user_count} ta\n• <b>Yuklangan kinolar:</b> {kino_count} ta", parse_mode='HTML')

# # Main Function
# def main():
#     updater = Updater(TOKEN, use_context=True)
#     dp = updater.dispatcher

#     # Handlers
#     dp.add_handler(CommandHandler("start", start))
#     dp.add_handler(CommandHandler("stat", stat))
#     dp.add_handler(CommandHandler("add_kino", add_kino))
#     dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

#     # Start Bot
#     updater.start_polling()
#     updater.idle()

# if __name__ == '__main__':
#     main()



import logging
import psycopg2
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, Filters
from telegram.update import Update
from datetime import datetime

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurations
TOKEN = '7675190858:AAGGJKFuDeL5IsM6TXPW3GW9I1X0EUzkQEY'
ADMIN_ID = ["1926076672"]
CHANNEL = "kinolar_kanali_top"
KINO_CHANNEL = "kinolaruzrushind"

# PostgreSQL Connection
try:
    conn = psycopg2.connect(
        host="localhost",
        user="postgres",
        password="87654321",
        dbname="username"
    )
    cursor = conn.cursor()
    logger.info("PostgreSQL bazaga muvaffaqiyatli ulandi.")
except Exception as e:
    logger.error(f"PostgreSQL ulanishda xato: {e}")
    conn = None

# Create Tables
if conn:
    cursor.execute("""CREATE TABLE IF NOT EXISTS user_id (
        id SERIAL PRIMARY KEY,
        user_id VARCHAR(100),
        step VARCHAR(200),
        sana VARCHAR(100)
    )""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS data (
        id SERIAL PRIMARY KEY,
        code VARCHAR(100),
        file_name VARCHAR(200),
        file_id VARCHAR(200),
        link VARCHAR(300)
    )""")
    
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='data' AND column_name='link'")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE data ADD COLUMN link TEXT;")
        conn.commit()
        logger.info("Link ustuni qo‘shildi.")

    conn.commit()

# Check DB Connection
def check_db_connection() -> bool:
    if conn:
        try:
            cursor.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Bazaga so'rov yuborishda xato: {e}")
            return False
    return False

# Helper Functions
def is_user_subscribed(context: CallbackContext, user_id: int) -> bool:
    try:
        member = context.bot.get_chat_member(chat_id=f"@{CHANNEL}", user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logger.error(f"Subscription check failed: {e}")
        return False

# Command Handlers
def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    name = update.effective_user.first_name

    if not check_db_connection():
        update.message.reply_text("⚠️ Bazaga ulanishda xatolik! Iltimos, keyinroq urinib ko‘ring.")
        return

    if not is_user_subscribed(context, user_id):
        update.message.reply_text(
            f"🔒 <a href='https://t.me/{CHANNEL}'>Kanalga</a> obuna bo'lmasangiz botdan to'liq foydalana olmaysiz!",
            parse_mode='HTML'
        )
        return

    cursor.execute("SELECT * FROM user_id WHERE user_id = %s", (str(user_id),))
    if not cursor.fetchone():
        sana = datetime.now().strftime("%d.%m.%Y | %H:%M")
        cursor.execute("INSERT INTO user_id (user_id, step, sana) VALUES (%s, %s, %s)", (str(user_id), '0', sana))
        conn.commit()

    keyboard = [[InlineKeyboardButton("🔎 Kodlarni qidirish", url=f"https://t.me/{KINO_CHANNEL}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        f"👋 <b>Salom {name}!</b>\n\n<i>Marhamat, kerakli kodni yuboring:</i>",
        parse_mode='HTML',
        reply_markup=reply_markup
    )

# Admin Command: Add Kino
def add_kino(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if user_id not in ADMIN_ID:
        update.message.reply_text("⛔ Sizda bu buyruqni bajarishga ruxsat yo‘q.")
        return

    if len(context.args) < 2:
        update.message.reply_text("⚠️ Kino kodi va linkini yuboring.\nMisol: /add_kino 12345 https://t.me/kinolar_kanali_top/233")
        return

    code = context.args[0]
    link = context.args[1]
    file_name = f"Kino {code}"

    cursor.execute("INSERT INTO data (code, file_name, file_id, link) VALUES (%s, %s, %s, %s)", (code, file_name, '', link))
    conn.commit()

    update.message.reply_text(f"✅ Kino bazaga qo‘shildi!\n\n<b>Kod:</b> {code}\n<b>Link:</b> {link}", parse_mode='HTML')

# Message Handler for Codes
def handle_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    if not is_user_subscribed(context, user_id):
        update.message.reply_text(
            f"🔒 <a href='https://t.me/{CHANNEL}'>Kanalga</a> obuna bo'lmasangiz botdan to'liq foydalana olmaysiz!",
            parse_mode='HTML'
        )
        return

    text = update.message.text

    if text.isdigit():
        cursor.execute("SELECT file_name, link FROM data WHERE code = %s", (text,))
        result = cursor.fetchone()
        if result:
            file_name, link = result
            keyboard = [[InlineKeyboardButton("🎬 Kinoni ko'rish", url=link)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"🎬 {file_name}\n📥 Kinoni ko'rish uchun pastdagi tugmani bosing:",
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        else:
            update.message.reply_text(f"{text} <b>mavjud emas!</b>\n\nQayta urinib ko'ring:", parse_mode='HTML')
    else:
        update.message.reply_text("<b>Faqat raqamlardan foydalaning!</b>", parse_mode='HTML')

# Admin Command: /stat
def stat(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if str(user_id) not in ADMIN_ID:
        return

    cursor.execute("SELECT COUNT(*) FROM user_id")
    user_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM data")
    kino_count = cursor.fetchone()[0]

    update.message.reply_text(f"• <b>Foydalanuvchilar:</b> {user_count} ta\n• <b>Yuklangan kinolar:</b> {kino_count} ta", parse_mode='HTML')

# Main Function
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stat", stat))
    dp.add_handler(CommandHandler("add_kino", add_kino))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
