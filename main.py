import os
import telebot
import requests
import io

# ضع الرمز المميز (Token) الخاص ببوتك هنا
TOKEN = "8311523299:AAEyE-5MVi7Xno5SF7q_9"
bot = telebot.TeleBot(TOKEN)

# إعداد خادم فلاسك للحفاظ على تشغيل البوت 24/7 على Render
from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "الروبت يعمل !"

# دالة قراءة النصوص من الصور باستخدام خدمة سحابية مجانية
def extract_text_from_image(image_bytes):
    url = 'https://api.ocr.space/parse/image'
    payload = {
        'apikey': 'helloworld',  # مفتاح مجاني عام للاختبار
        'language': 'ara',       # دعم اللغة العربية والإنجليزية
        'isOverlayRequired': False
    }
    files = {'file': ('image.jpg', image_bytes, 'image/jpeg')}
    try:
        response = requests.post(url, data=payload, files=files)
        result = response.json()
        if result.get('ParsedResults'):
            return result['ParsedResults'][0]['ParsedText']
        else:
            return "عذراً، لم أتمكن من استخراج أي نص من الصورة."
    except Exception as e:
        return f"حدث خطأ أثناء الاتصال بخدمة القراءة: {str(e)}"

# استقبال الرسائل النصية والترحيب
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "مرحباً بك! أرسل لي أي صورة تحتوي على نصوص وسأقوم باستخراجه لك فوراً 24/7.")

# استقبال الصور واستخراج النص منها
@bot.message_handler(content_types=['photo'])
def handle_image(message):
    bot.reply_to(message, "⏳ جاري قراءة الصورة واستخراج النص...")
    try:
        # الحصول على أفضل جودة للصورة المرسلة
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # استخراج النص باستخدام الدالة السحابية
        extracted_text = extract_text_from_image(downloaded_file)
        
        if not extracted_text.strip():
            extracted_text = "لم يتم العثور على أي نص واضح في الصورة."
            
        bot.reply_to(message, f"📄 **النص المستخرج:**\n\n{extracted_text}")
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ أثناء معالجة الصورة: {str(e)}")

if __name__ == '__main__':
    # تشغيل البอด وفلاسك معا
    import threading
    def run_flask():
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
        
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    
    bot.infinity_polling()
