import telebot
import yt_dlp
import os
import glob
from flask import Flask, request

BOT_TOKEN = "7969052102:AAF4CTb0ALcZv1IUGKlM0s565OGxBLhNv8Q"   # <-- TOKEN SHU YERDA

bot = telebot.TeleBot(BOT_TOKEN)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

user_states = {}
app = Flask(__name__)

# ------------------------------
#          WEBHOOK (RENDER)
# ------------------------------
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def receive_update():
    data = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(data)
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/", methods=["GET"])
def home():
    return "Bot is running on Render!", 200


# ------------------------------
#        BOT LOGIKA
# ------------------------------

@bot.message_handler(commands=['start'])
def start_cmd(msg):
    user_states[msg.from_user.id] = "waiting"
    bot.reply_to(msg, "🎵 Qo‘shiq nomini yuboring!")

@bot.message_handler(func=lambda m: True)
def all_messages(msg):
    user_id = msg.from_user.id
    if user_states.get(user_id) != "waiting":
        user_states[user_id] = "waiting"
    search_download(msg)

def search_download(msg):
    user_id = msg.from_user.id
    query = msg.text.strip()
    user_states[user_id] = "busy"

    wait_msg = bot.reply_to(msg, f"🔍 Qidirilmoqda: **{query}** ...", parse_mode='Markdown')

    try:
        # eski fayllarni tozalash
        for f in os.listdir(DOWNLOAD_FOLDER):
            os.remove(os.path.join(DOWNLOAD_FOLDER, f))

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": f"{DOWNLOAD_FOLDER}/song.%(ext)s",
            "noplaylist": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"ytsearch1:{query}"])

        # yuklangan faylni topish
        audio = None
        for ext in ["*.mp3", "*.m4a", "*.webm"]:
            files = glob.glob(f"{DOWNLOAD_FOLDER}/{ext}")
            if files:
                audio = files[0]
                break

        if not audio:
            bot.edit_message_text("❌ Topilmadi!", msg.chat.id, wait_msg.message_id)
            user_states[user_id] = "waiting"
            return

        with open(audio, "rb") as file:
            bot.send_audio(msg.chat.id, file, caption=f"🎵 {query}")

        os.remove(audio)

    except Exception as e:
        print("XATO:", e)
        bot.reply_to(msg, "❌ Xato bo‘ldi. Qayta urinib ko‘ring.")

    user_states[user_id] = "waiting"


# ------------------------------
#        RENDER SERVER START
# ------------------------------
if __name__ == "__main__":
    HOST = os.getenv("RENDER_EXTERNAL_HOSTNAME")

    if HOST is None:
        print("❌ RENDER_EXTERNAL_HOSTNAME topilmadi!")
        print("❗ BU KODNI KOMPYUTERDA ISHLATMANG.")
    else:
        WEBHOOK_URL = f"https://{HOST}/{BOT_TOKEN}"
        print("Webhook o‘rnatilmoqda:", WEBHOOK_URL)

        bot.delete_webhook()
        bot.set_webhook(url=WEBHOOK_URL)

    app.run(host="0.0.0.0", port=10000)
