
import logging
import psycopg2
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, filters
from telegram.update import Update
from datetime import datetime

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurations
TOKEN = '7675190858:AAGGJKFuDeL5IsM6TXPW3GW9I1X0EUzkQEY'
ADMIN_ID = ["1926076672"]
CHANNEL = "https://t.me/kinolar_kanali_top"
KINO_CHANNEL = "https://t.me/kinolaruzrushind"

# PostgreSQL Connection
conn = psycopg2.connect(
    host="localhost",
    user="username",
    password="password",
    dbname="username"
)
cursor = conn.cursor()

# Create Tables
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
    file_id VARCHAR(200)
)""")
conn.commit()

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
    
    # Check subscription
    if not is_user_subscribed(context, user_id):
        update.message.reply_text(f"🔒 @{CHANNEL} ga obuna bo'lmasangiz botdan to'liq foydalana olmaysiz!")
        return

    # Add user to DB
    cursor.execute("SELECT * FROM user_id WHERE user_id = %s", (str(user_id),))
    if not cursor.fetchone():
        sana = datetime.now().strftime("%d.%m.%Y | %H:%M")
        cursor.execute("INSERT INTO user_id (user_id, step, sana) VALUES (%s, %s, %s)", (str(user_id), '0', sana))
        conn.commit()

    keyboard = [[InlineKeyboardButton("🔎 Kodlarni qidirish", url=f"https://t.me/{KINO_CHANNEL}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(f"👋 <b>Salom {name}!</b>\n\n<i>Marhamat, kerakli kodni yuboring:</i>", parse_mode='HTML', reply_markup=reply_markup)

# Message Handler for Codes
def handle_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    text = update.message.text

    if text.isdigit():
        cursor.execute("SELECT file_name, file_id FROM data WHERE code = %s", (text,))
        result = cursor.fetchone()
        if result:
            file_name, file_id = result
            update.message.reply_video(video=file_id, caption=f"{file_name}\n\n@{context.bot.username} <b>bot yaratish xizmati!</b>", parse_mode='HTML')
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

    # Handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stat", stat))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Start Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

