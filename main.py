import os
from flask import Flask
import telebot
import threading
import pytesseract
from PIL import Image
import requests
from io import BytesIO

TOKEN = "8311523299:AAEyE-5MVi7Xno5SF7q_9p_QeHZ2a01BsUQ"
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك يا إسماعيل! أرسل لي أي صورة تحتوي على نص وسأقوم باستخراجه لك فوراً 24/7.")

@server.route('/')
def webhook():
    return "Bot is running!", 200

# استقبال الصور واستخراج النص منها
@bot.message_handler(content_types=['photo'])
def handle_image(message):
    try:
        bot.reply_to(message, "⏳ جاري قراءة الصورة واستخراج النص...")
        
        # الحصول على أعلى دقة للصورة المرسلة
        fileID = message.photo[-1].file_id
        file_info = bot.get_file(fileID)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # فتح الصورة باستخدام PIL
        image = Image.open(BytesIO(downloaded_file))
        
        # استخراج النص (يدعم العربية والإنجليزية)
        extracted_text = pytesseract.image_to_string(image, lang='ara+eng')
        
        if extracted_text.strip():
            bot.reply_to(message, f"📝 **النص المستخرج:**\n\n{extracted_text}")
        else:
            bot.reply_to(message, "⚠️ لم أتمكن من العثور على نص واضح في هذه الصورة.")
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ أثناء معالجة الصورة: {str(e)}")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "أرسل لي صورة وسأقوم باستخراج النص الموجود فيها!")

if __name__ == "__main__":
    # تشغيل التيليجرام في الخلفية
    t = threading.Thread(target=bot.infinity_polling)
    t.start()
    # تشغيل خادم الويب على المنفذ المطلوب
    port = int(os.environ.get("PORT", 5000))
    server.run(host="0.0.0.0", port=port)

