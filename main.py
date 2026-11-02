import os
import telebot
import yt_dlp
from flask import Flask

TOKEN = "9024426042:AAHvLk97IkiWEdmOEyL5Fyr80x4KXaNaK-4"
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is active and running!"

def download_video(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.mp4',
        'max_filesize': 50 * 1024 * 1024, # حد أقصى 50 ميجابايت لتناسب تيليجرام
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return 'video.mp4'
    except Exception as e:
        return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك يا إسماعيل! أرسل لي رابط أي ريلز أو فيديو وسأقوم بتحميله وإرساله لك فوراً.")

@bot.message_handler(func=lambda message: message.text and message.text.startswith('http'))
def handle_url(message):
    try:
        url = message.text.strip()
        bot.reply_to(message, "⏳ جاري تحميل الفيديو من الرابط...")
        
        video_file = download_video(url)
        
        if video_file and os.path.exists(video_file):
            with open(video_file, 'rb') as video:
                bot.send_video(message.chat.id, video, caption="تم التحميل بنجاح بواسطة البوت ✨")
            os.remove(video_file) # حذف الملف بعد إرساله لتوفير المساحة
        else:
            bot.reply_to(message, "عذراً، لم أستطع تحميل الفيديو. تأكد من صحة الرابط أو أن الفيديو متاح للعامة.")
    except Exception as e:
        bot.reply_to(message, "حدث خطأ أثناء معالجة الرابط.")

if __name__ == "__main__":
    import threading
    def run_bot():
        bot.infinity_polling()
    
    t = threading.Thread(target=run_bot)
    t.start()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
