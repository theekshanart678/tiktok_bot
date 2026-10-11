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
        "මට ඕනෑම TikTok Link එකක් එවන්න. ඔබට අවශ්‍ය Format එකෙන් මම Download කරලා දෙන්නම්! 🚀"
    )

# TikTok Link එකක් ලැබුණු විට Buttons පෙන්වීම
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    if "tiktok.com" in url:
        keyboard = [
            [
                InlineKeyboardButton("🎬 Video + MP3 (දෙකම)", callback_data=f"both|{url}"),
                InlineKeyboardButton("🎵 Only MP3 (සින්දුව විතරක්)", callback_data=f"aud|{url}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("ඔබට Download කරගැනීමට අවශ්‍ය ආකාරය තෝරන්න:", reply_markup=reply_markup)
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
    
    filename_base = f"download_{query.from_user.id}"
    
    try:
        # Option 1: Video + MP3 (දෙකම Download කිරීම)
        if download_type == "both":
            await query.edit_message_text("⬇️ Video එක සහ MP3 එක Download වෙමින් පවතී...")
            
            # 1. Download Video
            ydl_opts_video = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': f'{filename_base}_vid.%(ext)s',
                'quiet': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
                info_vid = ydl.extract_info(url, download=True)
                video_file = ydl.prepare_filename(info_vid)
                
            # 2. Extract MP3 Audio
            ydl_opts_audio = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': f'{filename_base}_aud.%(ext)s',
                'quiet': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
                ydl.extract_info(url, download=True)
            mp3_file = f"{filename_base}_aud.mp3"

            # Uploading files
            await query.edit_message_text("⬆️ Upload වෙමින් පවතී...")
            
            # Send Video
            with open(video_file, 'rb') as v_file:
                await query.message.reply_video(video=v_file, caption="🎬 TikTok Video එක")
                
            # Send MP3
            with open(mp3_file, 'rb') as a_file:
                await query.message.reply_audio(audio=a_file, caption="🎵 TikTok MP3 Audio එක")

            # Delete temporary files
            if os.path.exists(video_file):
                os.remove(video_file)
            if os.path.exists(mp3_file):
                os.remove(mp3_file)

        # Option 2: Only MP3 (සින්දුව විතරක් Download කිරීම)
        elif download_type == "aud":
            await query.edit_message_text("⬇️ MP3 එක Download වෙමින් පවතී...")
            
            ydl_opts_audio = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': f'{filename_base}_aud.%(ext)s',
                'quiet': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
                ydl.extract_info(url, download=True)
            mp3_file = f"{filename_base}_aud.mp3"

            await query.edit_message_text("⬆️ MP3 එක Upload වෙමින් පවතී...")
            with open(mp3_file, 'rb') as a_file:
                await query.message.reply_audio(audio=a_file, caption="🎵 මෙන්න ඔබේ MP3 Audio එක!")

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
