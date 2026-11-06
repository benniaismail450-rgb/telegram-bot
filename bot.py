import os
import telebot
import yt_dlp
import requests
from flask import Flask, request

TOKEN = "9024426042:AAHvLk97IkiWEdmOEyL5Fyr80x4KXaNaK-4"
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

# معرف القناة الخاصة بك للاشتراك الإجباري
CHANNEL_USERNAME = "@bot1234569"

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "!", 200
    else:
        return "Internal Server Error", 403

@app.route('/')
def home():
    return "Bot is active and running!"

# دالة التحقق من اشتراك المستخدم في القناة
def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
    except Exception as e:
        print(f"Error checking subscription: {e}")
    return False

def download_video(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.mp4',
        'max_filesize': 50 * 1024 * 1024, # حد أقصى 50 ميجابايت لتناسب تيليجرام
        'extractor_args': {'instagram': {'include_stories': True}} # السماح بتحميل القصص والملفات الشخصية
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return 'video.mp4'
    except Exception as e:
        print(f"Download error: {e}")
        return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    
    # فحص الاشتراك الإجباري
    if not check_subscription(user_id):
        markup = telebot.types.InlineKeyboardMarkup()
        btn_channel = telebot.types.InlineKeyboardButton("📢 اشترك في القناة", url="https://t.me/bot1234569")
        btn_check = telebot.types.InlineKeyboardButton("✅ لقد انضممت، تحقق", callback_data="check_sub")
        markup.add(btn_channel)
        markup.add(btn_check)
        
        bot.reply_to(message, "🚨 **عذراً يا إسماعيل!** لاستخدام هذا البوت، يجب عليك الانضمام إلى قناتنا أولاً:\n\n🔗 https://t.me/bot1234569", 
                     reply_markup=markup, parse_mode="Markdown")
        return

    bot.reply_to(message, "أهلاً بك يا إسماعيل! أرسل لي رابط أي ريلز، فيديو، أو رابط ملف شخصي لتحميل القصص وسأقوم بإرسالها لك فوراً.")

# التعامل مع زر التحقق من الاشتراك
@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def callback_query(call):
    user_id = call.from_user.id
    if check_subscription(user_id):
        bot.answer_callback_query(call.id, "✅ شكراً لاشتراكك! يمكنك الآن استخدام البوت.")
        bot.send_message(call.id, "أهلاً بك مجدداً! أرسل لي الرابط الآن للتحميل.")
    else:
        bot.answer_callback_query(call.id, "❌ لم تقم بالانضمام للقناة بعد!", show_alert=True)

@bot.message_handler(func=lambda message: message.text and message.text.startswith('http'))
def handle_url(message):
    user_id = message.from_user.id
    
    # التحقق من الاشتراك قبل بدء التحميل
    if not check_subscription(user_id):
        markup = telebot.types.InlineKeyboardMarkup()
        btn_channel = telebot.types.InlineKeyboardButton("📢 اشترك في القناة", url="https://t.me/bot1234569")
        markup.add(btn_channel)
        bot.reply_to(message, "🚨 يجب عليك الاشتراك في القناة أولاً لتتمكن من استخدام البوت وتحميل الملفات:\n\n🔗 https://t.me/bot1234569", reply_markup=markup)
        return

    try:
        url = message.text.strip()
        bot.reply_to(message, "⏳ جاري التحميل من الرابط (سواء فيديو أو قصة)...")
        
        video_file = download_video(url)
        
        if video_file and os.path.exists(video_file):
            with open(video_file, 'rb') as video:
                bot.send_video(message.chat.id, video, caption="تم التحميل بنجاح بواسطة البوت ✨")
            os.remove(video_file)
        else:
            bot.reply_to(message, "عذراً، لم أستطع تحميل المحتوى. تأكد من أن الحساب عام وأن الرابط صحيحي (رابط ريلز أو قصة متاحة للعامة).")
    except Exception as e:
        bot.reply_to(message, "حدث خطأ أثناء معالجة الرابط.")

if __name__ == "__main__":
    RENDER_URL = os.getenv("RENDER_EXTERNAL_URL", "https://telegram-bot-1-iv7n.onrender.com")
    
    bot.remove_webhook()
    bot.set_webhook(url=f"{RENDER_URL}/{TOKEN}")
    print(f"Webhook successfully set to: {RENDER_URL}/{TOKEN}")
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
