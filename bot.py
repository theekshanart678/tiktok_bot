import os
import logging
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# Logging සකස් කිරීම
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.environ.get("BOT_TOKEN")

# --- Render Free Web Service එක සඳහා Web Server එක ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()
# ---------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ආයුබෝවන්! මට TikTok Video Link එකක් එවන්න. මම Watermark නැතුව Download කරලා දෙන්නම්.")

async def download_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    
    if "tiktok.com" not in url:
        await update.message.reply_text("කරුණාකර නිවැරදි TikTok Link එකක් එවන්න.")
        return

    msg = await update.message.reply_text(" වීඩියෝ එක ඩවුන්ලෝඩ් වෙමින් පවතී, මඳක් රැඳී සිටින්න...")

    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.mp4',
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        with open('video.mp4', 'rb') as video_file:
            await update.message.reply_video(video=video_file, caption="මෙන්න ඔබ ඉල්ලූ වීඩියෝ එක! ")

        if os.path.exists('video.mp4'):
            os.remove('video.mp4')
            
        await msg.delete()

    except Exception as e:
        await update.message.reply_text(f"වීඩියෝ එක ඩවුන්ලෝඩ් කිරීමට නොහැකි විය. Error: {str(e)}")

def main():
    # Web server එක Start කිරීම (Free hosting සඳහා)
    keep_alive()
    
    # Telegram Bot එක Start කිරීම
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_tiktok))

    print("Bot සාර්ථකව Start විය...")
    bot_app.run_polling()

if __name__ == '__main__':
    main()
