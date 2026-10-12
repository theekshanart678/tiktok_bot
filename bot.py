import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 සාදරයෙන් පිළිගන්නවා!\n\n"
        "මට ඕනෑම  **TikTok** Link එකක් එවන්න. මම Video එක සහ Audio එක Download කරලා දෙන්නම්! 🚀"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    url = update.message.text.strip()
    
    # YouTube සහ TikTok Links විතරක් Check කිරීම
    if not ("tiktok.com" in url or "youtube.com" in url or "youtu.be" in url):
        await update.message.reply_text("⚠️ කරුණාකර වලංගු TikTok හෝ YouTube Link එකක් එවන්න.")
        return

    status_msg = await update.message.reply_text("⏳ Processing... මදක් රැඳී සිටින්න.")
    filename_vid = f"media_{user_id}.mp4"

    try:
        await status_msg.edit_text("⬇️ Video එක Download වෙමින් පවතී...")

        # Direct stream download options (FFmpeg අත්‍යවශ්‍ය නොවේ)
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': filename_vid,
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        await status_msg.edit_text("⬆️ Telegram එකට Upload වෙමින් පවතී...")

        # Video එක Send කිරීම
        if os.path.exists(filename_vid):
            with open(filename_vid, 'rb') as v_file:
                await update.message.reply_video(video=v_file, caption="🎬 Downloader Video")
            
            # Audio Stream එකක් ලෙස Send කිරීම
            with open(filename_vid, 'rb') as a_file:
                await update.message.reply_audio(audio=a_file, caption="🎵 Downloader Audio")

            # File එක Delete කිරීම
            os.remove(filename_vid)

        await status_msg.delete()

    except Exception as e:
        logging.error(f"Error: {e}")
        await status_msg.edit_text(f"❌ Download කිරීමට නොහැකි විය. Link එක පරීක්ෂා කරන්න.\n\nError: {str(e)}")

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
