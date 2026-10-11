import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
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
        "මට ඕනෑම TikTok Link එකක් එවන්න. මම Video එක සහ MP3 Audio එක එකවරම Automatic Download කරලා දෙන්නම්! 🚀"
    )

# TikTok Link එකක් ලැබුණු විට Video එක සහ MP3 එක එකවර Download කර Send කිරීම
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    if "tiktok.com" not in url:
        await update.message.reply_text("⚠️ කරුණාකර වලංගු TikTok Link එකක් එවන්න.")
        return

    status_msg = await update.message.reply_text("⏳ Processing... මදක් රැඳී සිටින්න.")
    filename_base = f"download_{update.message.from_user.id}"

    try:
        await status_msg.edit_text("⬇️ Video එක සහ MP3 එක Download වෙමින් පවතී...")

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

        # Uploading files to Telegram
        await status_msg.edit_text("⬆️ Upload වෙමින් පවතී...")

        # Send Video
        with open(video_file, 'rb') as v_file:
            await update.message.reply_video(video=v_file, caption="🎬 TikTok Video එක")

        # Send MP3 Audio
        with open(mp3_file, 'rb') as a_file:
            await update.message.reply_audio(audio=a_file, caption="🎵 TikTok MP3 Audio එක")

        # Delete temporary files from server
        if os.path.exists(video_file):
            os.remove(video_file)
        if os.path.exists(mp3_file):
            os.remove(mp3_file)

        # Delete status message
        await status_msg.delete()

    except Exception as e:
        logging.error(f"Error: {e}")
        await status_msg.edit_text(f"❌ Download කිරීමට නොහැකි විය. Error: {str(e)}")

def main():
    if not BOT_TOKEN:
        print("BOT_TOKEN set කර නැත!")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
