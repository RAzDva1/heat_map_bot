from flask import Flask, request
import os
import telebot

TOKEN_TG = os.getenv('TOKEN_TG_BOT', '')
TOKEN_APP_HEROKU = os.getenv('TOKEN_APP_HEROKU', '')

bot = telebot.TeleBot(TOKEN_TG)
print(TOKEN_TG)
print(TOKEN_APP_HEROKU)

app = Flask(__name__)


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 'Hello, ' + message.from_user.first_name)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    print("echo")
    bot.reply_to(message, message.text)


@app.route('/', methods=['POST'])
def getMessage():
    print("getMessage/")
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@app.route('/{}'.format(TOKEN_TG), methods=['POST'])
def getMessage_():
    print("getMessage/token")
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "?", 200



@app.route("/")
def webhook():
    print("webhook")
    bot.remove_webhook()
    bot.set_webhook(url='https://{}.herokuapp.com/'.format(TOKEN_APP_HEROKU) + TOKEN_TG)
    return "!", 200


if __name__ == "__main__":
    app.run()

