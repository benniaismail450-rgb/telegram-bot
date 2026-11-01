import os
import telebot
import requests
from flask import Flask

TOKEN = "8311523299:AAEyE-5MVi7Xno5SF7q_9"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is active and running!"

def extract_text_from_image(image_bytes):
    url = 'https://api.ocr.space/parse/image'
    payload = {
        'apikey': 'helloworld',
        'language': 'ara',
        'isOverlayRequired': False
    }
    files = {'file': ('image.jpg', image_bytes, 'image/jpeg')}
    try:
        response = requests.post(url, data=payload, files=files)
        result = response.json()
        if result.get('ParsedResults'):
            return result['ParsedResults'][0]['ParsedText']
        else:
            return "لم يتم العثور على أي نص واضح في الصورة."
    except Exception as e:
        return f"حدث خطأ أثناء الاتصال: {str(e)}"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك يا إسماعيل! البوت يعمل الآن بنجاح. أرسل لي أي صورة وسأستخرج منها النص فوراً.")

@bot.message_handler(content_types=['photo'])
def handle_image(message):
    bot.reply_to(message, "⏳ جاري قراءة الصورة واستخراج النص...")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        extracted_text = extract_text_from_image(downloaded_file)
        bot.reply_to(message, f"📄 **النص المستخرج:**\n\n{extracted_text}")
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ أثناء معالجة الصورة: {str(e)}")

if __name__ == '__main__':
    import threading
    port = int(os.environ.get('PORT', 5000))
    # تشغيل فلاسك في خلفية منفصلة
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)).start()
    # تشغيل البوت بشكل مباشر
    bot.infinity_polling(skip_pending=True)
