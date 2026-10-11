import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = '8946691836:AAFXJKUA450DvodtATk-ZU9pfMyqboWIm1s' # මෙතැනට ඔබේ Token එක දෙන්න

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "සාදරයෙන් පිළිගන්නවා! 🎬\n\nමත ඕනෑම TikTok Video එකක Link එක එවන්න. මම Watermark එක නැතුව වීඩියෝ එක Download කරලා දෙන්නම්."
    )

# TikTok Link එක Process කරන Function එක
async def download_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    # TikTok Link එකක්දැයි පරීක්ෂා කිරීම
    if "tiktok.com" not in url:
        await update.message.reply_text("කරුණාකර නිවැරදි TikTok Link එකක් එවන්න.")
        return

    status_msg = await update.message.reply_text("වීඩියෝ එක Download වෙමින් පවතී... කරුණාකර රැඳී සිටින්න ⏳")

    output_file = f"video_{update.message.chat_id}.mp4"

    # yt-dlp Settings
    ydl_opts = {
        'format': 'best',
        'outtmpl': output_file,
        'quiet': True,
    }

    try:
        # Video එක Download කිරීම
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Telegram එකට Video එක Send කිරීම
        await update.message.reply_video(
            video=open(output_file, 'rb'),
            caption="මෙන්න ඔබේ වීඩියෝ එක! 🚀"
        )
        
        # Status message එක ඉවත් කිරීම
        await status_msg.delete()

    except Exception as e:
        await update.message.reply_text("")
        print(f"Error: {e}")

    finally:
        # Download වූ File එක PC එකෙන් Delete කිරීම
        if os.path.exists(output_file):
            os.remove(output_file)

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_tiktok))

    print("Bot කියාත්මක වෙමින් පවතී...")
    app.run_polling()

if __name__ == '__main__':
    main()