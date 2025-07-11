
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from handlers import db, force_sub, downloader, admin_panel, security

TOKEN = "7775250276:AAGZqjnyMOc5w8n0C1sx6Ghypq-QRwtiqeQ"
ADMIN_ID = 5784688641
FORCE_SUB_CHANNEL = "DownloadKing_Arsalan"

def start(update: Update, context: CallbackContext):
    user = update.effective_user
    user_id = user.id

    if not force_sub.check_force_join(update, context, FORCE_SUB_CHANNEL):
        return

    db.add_user(user_id)

    buttons = [[KeyboardButton("🇮🇷 فارسی"), KeyboardButton("🇬🇧 English")]]
    if user_id == ADMIN_ID:
        buttons.append([KeyboardButton("🛠 تنظیمات مدیریت")])
    update.message.reply_text(
        "لطفاً زبان خود را انتخاب کنید:\nPlease choose your language:",
        reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    )

def handle_language(update: Update, context: CallbackContext):
    if not security.check_spam(update, context):
        return

    user = update.effective_user
    user_id = user.id
    text = update.message.text

    if not force_sub.check_force_join(update, context, FORCE_SUB_CHANNEL):
        return

    if text == "🇮🇷 فارسی":
        db.set_language(user_id, "fa")
        update.message.reply_text(
            "✅ زبان شما به فارسی تنظیم شد.\n\nبرای درخواست نسخه VIP، روی دکمه زیر کلیک کنید:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📩 درخواست VIP", callback_data="vip_request")]
            ])
        )
    elif text == "🇬🇧 English":
        db.set_language(user_id, "en")
        update.message.reply_text(
            "✅ Language set to English.\n\nTo request VIP access, click below:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📩 Request VIP", callback_data="vip_request")]
            ])
        )
    elif text == "🛠 تنظیمات مدیریت" and user_id == ADMIN_ID:
        admin_panel.show_admin_panel(update, context, ADMIN_ID)
    else:
        downloader.process_link(update, context, text)

def handle_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data

    if data == "vip_request":
        if db.request_vip(user_id):
            query.edit_message_text("✅ درخواست VIP شما ثبت شد. منتظر تأیید مدیر باشید.")
        else:
            query.edit_message_text("⚠ شما قبلاً درخواست داده‌اید یا VIP هستید.")
    else:
        admin_panel.handle_callback(update, context, ADMIN_ID)

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_language))
    dp.add_handler(CallbackQueryHandler(handle_callback))
    dp.add_handler(MessageHandler(Filters.text & Filters.user(user_id=ADMIN_ID),
                                   lambda u, c: admin_panel.handle_text(u, c, ADMIN_ID)))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
