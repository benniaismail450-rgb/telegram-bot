import os
import telebot
import yt_dlp
from flask import Flask, request

TOKEN = "9024426042:AAFPUbF80JpK1FgYq0_ZEv9DdBtGkuuWF1I"
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)
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

def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
    except Exception as e:
        print(f"Error checking subscription: {e}")
    return False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if not check_subscription(user_id):
        markup = telebot.types.InlineKeyboardMarkup()
        btn_channel = telebot.types.InlineKeyboardButton("📢 اشترك في القناة", url="https://t.me/bot1234569")
        btn_check = telebot.types.InlineKeyboardButton("✅ لقد انضممت، تحقق", callback_data="check_sub")
        markup.add(btn_channel, btn_check)
        bot.reply_to(message, "🚨 **عذراً يا إسماعيل!** يجب عليك الاشتراك في قناتنا أولاً:\n\n🔗 https://t.me/bot1234569", reply_markup=markup, parse_mode="Markdown")
        return
    bot.reply_to(message, "أهلاً بك يا إسماعيل! البوت يعمل الآن بكامل طاقته بالتوكن الجديد. أرسل لي رابط ريلز أو رابط أي حساب لعرض أزرار التحميل فوراً.")

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def callback_query(call):
    user_id = call.from_user.id
    if check_subscription(user_id):
        bot.answer_callback_query(call.id, "✅ شكراً لاشتراكك!")
        bot.send_message(call.id, "أهلاً بك مجدداً يا إسماعيل! أرسل الرابط الآن.")
    else:
        bot.answer_callback_query(call.id, "❌ لم تقم بالانضمام للقناة بعد!", show_alert=True)

@bot.message_handler(func=lambda message: message.text and message.text.startswith('http'))
def handle_url(message):
    user_id = message.from_user.id
    if not check_subscription(user_id):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("📢 اشترك في القناة", url="https://t.me/bot1234569"))
        bot.reply_to(message, "🚨 يجب عليك الاشتراك في القناة أولاً لتتمكن من استخدام البوت:\n\n🔗 https://t.me/bot1234569", reply_markup=markup)
        return

    raw_url = message.text.strip()
    clean_url = raw_url.split('?')[0]

    if "reel" in clean_url or "p/" in clean_url:
        bot.reply_to(message, "⏳ جاري تحميل الفيديو...")
        try:
            ydl_opts = {'format': 'best', 'outtmpl': 'video.mp4', 'max_filesize': 50 * 1024 * 1024}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([clean_url])
            if os.path.exists('video.mp4'):
                with open('video.mp4', 'rb') as video:
                    bot.send_video(message.chat.id, video, caption="تم التحميل بنجاح ✨")
                os.remove('video.mp4')
            else:
                bot.reply_to(message, "عذراً، لم أستطع تحميل الملف.")
        except Exception as e:
            bot.reply_to(message, f"حدث خطأ: {e}")
    else:
        text = (
            f"👤 **تم استلام رابط الحساب بنجاح!**\n\n"
            f"اختر ما تريد تحميله أدناه:"
        )
        markup = telebot.types.InlineKeyboardMarkup()
        btn_posts = telebot.types.InlineKeyboardButton("📥 تحميل المنشورات", callback_data=f"dl_posts_{clean_url}")
        btn_stories = telebot.types.InlineKeyboardButton("📸 تحميل القصص", callback_data=f"dl_stories_{clean_url}")
        markup.add(btn_posts, btn_stories)
        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('dl_'))
def handle_download_actions(call):
    action_data = call.data.split('_', 2)
    action_type = action_data[1]
    target_url = action_data[2]
    
    if action_type == "posts":
        bot.answer_callback_query(call.id, "جاري تحضير المنشورات...")
        bot.send_message(call.message.chat.id, "⏳ جارِ سحب أحدث منشورات الحساب...")
        try:
            ydl_opts = {'format': 'best', 'outtmpl': 'post.mp4', 'max_filesize': 50 * 1024 * 1024, 'playlistend': 1}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([target_url])
            if os.path.exists('post.mp4'):
                with open('post.mp4', 'rb') as f:
                    bot.send_video(call.message.chat.id, f, caption="آخر منشور تم تحميله بنجاح ✨")
                os.remove('post.mp4')
            else:
                bot.send_message(call.message.chat.id, "لم يتم العثور على منشورات قابلة للتحميل.")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"حدث خطأ أثناء تحميل المنشورات: {e}")
            
    elif action_type == "stories":
        bot.answer_callback_query(call.id, "جاري البحث عن القصص...")
        bot.send_message(call.message.chat.id, "⏳ جاري محاولة جلب قصص الحساب (Stories)...")
        try:
            ydl_opts = {
                'format': 'best', 
                'outtmpl': 'story.mp4', 
                'max_filesize': 50 * 1024 * 1024, 
                'extractor_args': {'instagram': {'include_stories': True}}
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([target_url])
            if os.path.exists('story.mp4'):
                with open('story.mp4', 'rb') as f:
                    bot.send_video(call.message.chat.id, f, caption="تم تحميل القصة بنجاح ✨")
                os.remove('story.mp4')
            else:
                bot.send_message(call.message.chat.id, "❌ لا توجد قصص نشطة حالياً لهذا الحساب.")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"عذراً، فشل تحميل القصص: {e}")

if __name__ == "__main__":
    RENDER_URL = os.getenv("RENDER_EXTERNAL_URL", "https://telegram-bot-1-iv7n.onrender.com")
    bot.remove_webhook()
    bot.set_webhook(url=f"{RENDER_URL}/{TOKEN}")
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
