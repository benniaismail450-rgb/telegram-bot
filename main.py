import telebot

TOKEN = "8311523299:AAEyE-5MVi7Xno5SF7q_9p_QeHZ2a01BsUQ"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك يا إسماعيل! بوت تيليجرام يعمل الآن بنجاح 24/7.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "لقد استلمت رسالتك بنجاح!")

bot.polling()
