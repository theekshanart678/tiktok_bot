import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import yt_dlp

# Logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 සාදරයෙන් පිළිගන්නවා!\n\n"
        "මට ඕනෑම TikTok Link එකක් එවන්න. මම Video එක හෝ Audio (MP3) එක Download කරලා දෙන්නම්! 🚀"
    )

# TikTok Link එකක් ලැබුණු විට Buttons පෙන්වීම
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    if "tiktok.com" in url:
        # Buttons දෙක සාදාගැනීම
        keyboard = [
            [
                InlineKeyboardButton("🎥 Video Download", callback_data=f"vid|{url}"),
                InlineKeyboardButton("🎵 Audio Only (MP3)", callback_data=f"aud|{url}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("ඔබට Download කරගැනීමට අවශ්‍ය Format එක තෝරන්න:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("⚠️ කරුණාකර වලංගු TikTok Link එකක් එවන්න.")

# Button Click කළ විට Download කර Send කිරීම
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data.split("|")
    download_type = data[0]
    url = data[1]
    
    await query.edit_message_text("⏳ Processing... මදක් රැඳී සිටින්න.")
    
    filename = f"download_{query.from_user.id}"
    
    try:
        if download_type == "vid":
            # Video Download Options
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': f'{filename}.%(ext)s',
                'quiet': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_file = ydl.prepare_filename(info)
            
            await query.edit_message_text("⬆️ Video එක Upload වෙමින් පවතී...")
            with open(downloaded_file, 'rb') as video:
                await query.message.reply_video(video=video, caption="✨ මෙන්න ඔබේ TikTok Video එක!")
            
            if os.path.exists(downloaded_file):
                os.remove(downloaded_file)

        elif download_type == "aud":
            # Audio (MP3) Download Options
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': f'{filename}.%(ext)s',
                'quiet': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(url, download=True)
            
            mp3_file = f"{filename}.mp3"
            
            await query.edit_message_text("⬆️ Audio එක Upload වෙමින් පවතී...")
            with open(mp3_file, 'rb') as audio:
                await query.message.reply_audio(audio=audio, caption="🎵 මෙන්න ඔබේ TikTok Audio (MP3) එක!")
            
            if os.path.exists(mp3_file):
                os.remove(mp3_file)
                
        await query.delete_message()

    except Exception as e:
        logging.error(f"Error: {e}")
        await query.edit_message_text(f"❌ Download කිරීමට නොහැකි විය. Error: {str(e)}")

def main():
    if not BOT_TOKEN:
        print("BOT_TOKEN set කර නැත!")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_click))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
