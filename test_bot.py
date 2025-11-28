import telebot
import yt_dlp
import os
import glob
from telebot.types import Message

BOT_TOKEN = "7969052102:AAF4CTb0ALcZv1IUGKlM0s565OGxBLhNv8Q"
bot = telebot.TeleBot(BOT_TOKEN)

DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@bot.message_handler(commands=['start'])
def start_message(message: Message):
    bot.reply_to(message, 
    "🎵 **Qo'shiq Bot**ga xush kelibsiz!\n\n"
    "🎤 **Qo'shiq nomini yozing:**\n"
    "`Ozodbek Nazarbekov - Yiglama`\n\n"
    "✅ **Audio 10 soniyada keladi!**"
    , parse_mode='Markdown')

@bot.message_handler(func=lambda message: True and not message.text.startswith('/'))
def search_and_download(message: Message):
    query = message.text.strip()
    
    # 1-QADAM: Qidirishimport telebot
import yt_dlp
import os
import glob
import time
from telebot.types import Message

BOT_TOKEN = "7969052102:AAF4CTb0ALcZv1IUGKlM0s565OGxBLhNv8Q"
bot = telebot.TeleBot(BOT_TOKEN)

DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

user_states = {}  # Foydalanuvchi holatini saqlash

@bot.message_handler(commands=['start'])
def start_message(message: Message):
    user_id = message.from_user.id
    user_states[user_id] = "waiting_for_song"  # Holatni o'rnatish
    
    bot.reply_to(message, 
    "🎵 **Qo'shiq Bot**ga xush kelibsiz!\n\n"
    "🎤 **ENDI qo'shiq nomini yozing:**\n"
    "`Ozodbek Nazarbekov - Yiglama`\n\n"
    "✅ **Audio 10 soniyada keladi!**"
    , parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message: Message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    # Agar /start bo'lmasa va holat waiting_for_song bo'lsa
    if user_id not in user_states or user_states[user_id] != "waiting_for_song":
        if not text.startswith('/'):
            # Qo'shiq qidirish
            search_and_download(message)
        # return
    
    # Startdan keyin birinchi xabar - qo'shiq nomi
    if user_states[user_id] == "waiting_for_song" and len(text) > 3 and not text.startswith('/'):
        search_and_download(message)
    else:
        bot.reply_to(message, "🎤 **Qo'shiq nomini yozing!**\n`Ozodbek - Yiglama`", parse_mode='Markdown')

def search_and_download(message: Message):
    user_id = message.from_user.id
    query = message.text.strip()
    
    # Holatni o'zgartirish
    user_states[user_id] = "searching"
    
    # 1-QADAM: Qidirish
    search_msg = bot.reply_to(message, f"🔍 **'{query}'** qidirilmoqda...")
    
    try:
        # PAPKANI TOZALASH
        for file in os.listdir(DOWNLOAD_FOLDER):
            try:
                os.remove(os.path.join(DOWNLOAD_FOLDER, file))
            except:
                pass
        
        # 2-QADAM: AUDIO YUKLASH
        bot.edit_message_text(
            f"📥 **'{query}'** yuklanmoqda...\n⏳ 5-10 soniya...", 
            message.chat.id, 
            search_msg.message_id,
            parse_mode='Markdown'
        )
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{DOWNLOAD_FOLDER}/qoshiq.%(ext)s',
            'noplaylist': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"ytsearch1:{query}"])
        
        # AUDIO FAYL TOPISH
        audio_extensions = ['*.webm', '*.m4a', '*.mp4', '*.mp3', '*.m4b']
        audio_path = None
        
        for ext in audio_extensions:
            files = glob.glob(f"{DOWNLOAD_FOLDER}/{ext}")
            if files:
                audio_path = files[0]
                break
        
        if not audio_path:
            bot.edit_message_text(
                "❌ Audio fayl topilmadi!\n🔄 Boshqa qo'shiq urinib ko'ring", 
                message.chat.id, 
                search_msg.message_id,
                parse_mode='Markdown'
            )
            user_states[user_id] = "waiting_for_song"
            return
        
        # MA'LUMOT OLISH
        info_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(info_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            if info['entries']:
                title = info['entries'][0].get('title', query)
                uploader = info['entries'][0].get('uploader', 'Q\'o\'shiqchi')
                duration = info['entries'][0].get('duration', 180)
            else:
                title = query
                uploader = "Qo'shiqchi"
                duration = 180
        
        # 3-QADAM: AUDIO YUBORISH
        with open(audio_path, 'rb') as audio:
            bot.send_audio(
                message.chat.id,
                audio,
                title=title,
                performer=uploader,
                duration=duration,
                caption=f"🎵 **{title}**\n\n"
                       f"🎤 **{uploader}**\n"
                       f"⏱️ **{duration//60}:{duration%60:02d}**\n"
                       f"🔍 **{query}**",
                parse_mode='Markdown'
            )
        
        # Eski xabarni o'chirish
        try:
            bot.delete_message(message.chat.id, search_msg.message_id)
        except:
            pass
        
        # FAYLNI O'CHIRISH
        os.remove(audio_path)
        
        # Holatni qaytarish
        user_states[user_id] = "waiting_for_song"
        
        # Tayyor xabar
        bot.send_message(
            message.chat.id,
            "🎵 **Yana qo'shiq yuboring!**\n\n"
            "`Ozodbek Nazarbekov - Yiglama`",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        try:
            bot.delete_message(message.chat.id, search_msg.message_id)
        except:
            pass
        bot.reply_to(message, "❌ Xatolik!\n🔄 Qayta urinib ko'ring.")
        print(f"XATO: {e}")
        user_states[user_id] = "waiting_for_song"

@bot.message_handler(commands=['top'])
def top_songs(message: Message):
    bot.reply_to(message, 
    "🔥 **TOP QO'SHIQLAR:**\n\n"
    "1. `Ozodbek Nazarbekov - Yiglama`\n"
    "2. `Manzar - Yurak`\n"
    "3. `Sevara Nazarkhan - Yor`\n"
    "4. `Shohruhxon - Sevgi`\n\n"
    "**Nomini yozing!**", 
    parse_mode='Markdown')

if __name__ == "__main__":
    print("🤖 Qo'shiq bot ishga tushdi! 🎵")
    bot.infinity_polling()
    search_msg = bot.reply_to(message, f"🔍 **'{query}'** qidirilmoqda...")
    
    try:
        # PAPKANI TOZALASH
        for file in os.listdir(DOWNLOAD_FOLDER):
            try:
                os.remove(os.path.join(DOWNLOAD_FOLDER, file))
            except:
                pass
        
        # 2-QADAM: AUDIO YUKLASH (FFmpeg KERAK EMAS!)
        loading_msg = bot.send_message(message.chat.id, "📥 **Audio yuklanmoqda...**")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'noplaylist': True,
            # FFmpeg KERAK EMAS - WEBM/M4A to'g'ridan-to'g'ri yuboramiz
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Qidirish + yuklash BIR VAQTDAN
            ydl.download([f"ytsearch1:{query}"])
        
        # BARCHA AUDIO FAYLLARNI QIDIRISH
        audio_extensions = ['*.webm', '*.m4a', '*.mp4', '*.mp3']
        audio_path = None
        
        for ext in audio_extensions:
            files = glob.glob(f"{DOWNLOAD_FOLDER}/{ext}")
            if files:
                audio_path = files[0]
                break
        
        if not audio_path:
            bot.delete_message(message.chat.id, loading_msg.message_id)
            bot.send_message(message.chat.id, "❌ Audio fayl topilmadi!")
            # return
        
        # VIDEO MA'LUMOTINI OLISH (sarlavha uchun)
        ydl_info = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_info) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            if info['entries']:
                title = info['entries'][0].get('title', query)
                uploader = info['entries'][0].get('uploader', 'Q\'o\'shiqchi')
                duration = info['entries'][0].get('duration', 0)
            else:
                title = query
                uploader = "Qo'shiqchi"
                duration = 0
        
        # 3-QADAM: AUDIO YUBORISH
        bot.delete_message(message.chat.id, loading_msg.message_id)
        
        # Fayl hajmini tekshirish
        file_size = os.path.getsize(audio_path)
        if file_size > 50 * 1024 * 1024:  # 50MB dan katta bo'lsa
            os.remove(audio_path)
            bot.send_message(message.chat.id, "❌ Fayl juda katta!")
            # return
        
        with open(audio_path, 'rb') as audio:
            bot.send_audio(
                message.chat.id,
                audio,
                title=title,
                performer=uploader,
                duration=duration,
                caption=f"🎵 **{title}**\n\n"
                       f"🎤 **{uploader}**\n"
                       f"⏱️ **{duration//60}:{duration%60:02d}**\n"
                       f"🔍 **{query}**",
                parse_mode='Markdown'
            )
        
        # 1-QADAM XABARINI O'CHIRISH
        bot.delete_message(message.chat.id, search_msg.message_id)
        
        # FAYLNI O'CHIRISH
        os.remove(audio_path)
        
    except Exception as e:
        try:
            bot.delete_message(message.chat.id, search_msg.message_id)
            bot.delete_message(message.chat.id, loading_msg.message_id)
        except:
            pass
        bot.reply_to(message, f"❌ Xatolik yuz berdi!\n🔄 Qayta urinib ko'ring.")
        print(f"XATO: {e}")

@bot.message_handler(commands=['top'])
def top_songs(message: Message):
    bot.reply_to(message, 
    "🔥 **TOP QO'SHIQLAR:**\n\n"
    "🎵 `Ozodbek Nazarbekov - Yiglama`\n"
    "🎵 `Manzar - Yurak`\n"
    "🎵 `Sevara Nazarkhan - Yor`\n\n"
    "**Qo'shiq nomini yozing!**", 
    parse_mode='Markdown')

if __name__ == "__main__":
    print("🤖 Qo'shiq bot ishga tushdi! 🎵 FFmpeg KERAK EMAS!")
    bot.infinity_polling()