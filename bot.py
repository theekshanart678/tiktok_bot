
import os
import json
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

# ⚠️ මෙතැනට ඔබේ Telegram User ID එක යොදන්න (උදා: ADMIN_ID = 987654321)
ADMIN_ID = 5620315302  

USERS_FILE = "users.json"

def save_user(user_id):
    users = set()
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                users = set(json.load(f))
        except Exception:
            users = set()
            
    if user_id not in users:
        users.add(user_id)
        with open(USERS_FILE, "w") as f:
            json.dump(list(users), f)

def get_user_count():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                users = json.load(f)
                return len(users)
        except Exception:
            return 0
    return 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user(user_id)
    
    await update.message.reply_text(
        "👋 සාදරයෙන් පිළිගන්නවා!\n\n"
        "මට ඕනෑම TikTok Link එකක් එවන්න. මම Video එක සහ MP3 Audio එක එකවරම Automatic Download කරලා දෙන්නම්! 🚀"
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == ADMIN_ID:
        count = get_user_count()
        await update.message.reply_text(f"📊 **Bot Statistics**\n\n👤 මුළු Users ලා ගණන: **{count}**", parse_mode="Markdown")
    else:
        await update.message.reply_text("⚠️ ඔබට මෙම Command එක භාවිතා කිරීමට අවසර නැත.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user(user_id)
    
    url = update.message.text.strip()
    
    if "tiktok.com" not in url:
        await update.message.reply_text("⚠️ කරුණාකර වලංගු TikTok Link එකක් එවන්න.")
        return

    status_msg = await update.message.reply_text("⏳ Processing... මදක් රැඳී සිටින්න.")
    filename_base = f"download_{user_id}"

    try:
        await status_msg.edit_text("⬇️ Video එක සහ MP3 එක Download වෙමින් පවතී...")

        # 1. Video Download
        ydl_opts_video = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': f'{filename_base}_vid.%(ext)s',
            'quiet': True,
        }
        video_file = None
        with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
            info_vid = ydl.extract_info(url, download=True)
            video_file = ydl.prepare_filename(info_vid)

        # 2. Audio MP3 Extract
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

        await status_msg.edit_text("⬆️ Upload වෙමින් පවතී...")

        # Send Video
        if video_file and os.path.exists(video_file):
            with open(video_file, 'rb') as v_file:
                await update.message.reply_video(video=v_file, caption="🎬 TikTok Video එක")
            os.remove(video_file)

        # Send MP3
        if os.path.exists(mp3_file):
            with open(mp3_file, 'rb') as a_file:
                await update.message.reply_audio(audio=a_file, caption="🎵 TikTok MP3 Audio එක")
            os.remove(mp3_file)

        await status_msg.delete()

    except Exception as e:
        logging.error(f"Error: {e}")
        await status_msg.edit_text(f"❌ Download කිරීමට නොහැකි විය: {str(e)}")

def main():
    if not BOT_TOKEN:
        print("BOT_TOKEN set කර නැත!")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
