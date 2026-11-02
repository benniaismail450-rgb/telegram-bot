import os
import telebot
import requests
from flask import Flask

TOKEN = "9024426042:AAHvLk97IkiWEdmOEyL5Fyr80x4KXaNaK-4"
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
        print("OCR API Response:", result)
        
        if result.get('ParsedResults') and len(result['ParsedResults']) > 0:
            parsed_text = result['ParsedResults'][0].get('ParsedText', '').strip()
            if parsed_text:
                return parsed_text
        
        error_msgs = result.get('ErrorMessage')
        if error_msgs:
            return f"خطأ من موقع OCR: {error_msgs}"
            
        return "لم يتم العثور على نص واضح في الصورة."
    except Exception as e:
        return f"حدث خطأ تقني: {str(e)}"

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        bot.reply_to(message, "⏳ جاري قراءة النص من الصورة...")
        fileID = message.photo[-1].file_id
        file_info = bot.get_file(fileID)
        downloaded_file = bot.download_file(file_info.file_path)
        
        extracted_text = extract_text_from_image(downloaded_file)
        bot.reply_to(message, f"📄 النص المستخرج:\n\n{extracted_text}")
    except Exception as e:
        bot.reply_to(message, "حدث خطأ أثناء تحميل الصورة.")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك! أرسل لي أي صورة تحتوي على نص وسأقوم باستخراجه لك.")

if __name__ == "__main__":
    import threading
    def run_bot():
        bot.infinity_polling()
    
    t = threading.Thread(target=run_bot)
    t.start()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
