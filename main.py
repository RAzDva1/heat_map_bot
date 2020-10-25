from flask import Flask, request
import os
import telebot
from apscheduler.schedulers.background import BackgroundScheduler

TOKEN_TG = os.getenv('TOKEN_TG')
TOKEN_APP_HEROKU = os.getenv('TOKEN_APP_HEROKU', '')
HEROKU = os.getenv('HEROKU', '')

bot = telebot.TeleBot(TOKEN_TG)
print("TOKEN_TG", TOKEN_TG)
print("TOKEN_APP_HEROKU", TOKEN_APP_HEROKU)

sched = BackgroundScheduler()


def send_message_by_scheldier(chat_id):
    print("Schediler")
    bot.send_message(chat_id=chat_id, text="This message send you by scheduler")


sched.add_job(send_message_by_scheldier, 'cron', args=[353688371], year='*', month='*',
              day='*', week='*', day_of_week='*',
              hour='*', minute='*', second=15)

sched.add_job(send_message_by_scheldier, 'cron', args=[353688371], year='*', month='*',
              day='*', week='*', day_of_week='*',
              hour='*', minute='*', second=30)

sched.add_job(send_message_by_scheldier, 'cron', args=[353688371], year='*', month='*',
              day='*', week='*', day_of_week='*',
              hour='*', minute='*', second=45)

sched.start()


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 'Hello, ' + message.from_user.first_name)
    sched.add_job(send_message_by_scheldier, 'cron', args=[message.chat.id], year='*', month='*',
                  day='*', week='*', day_of_week='*',
                  hour='*', minute='*', second=50)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    print("echo")
    bot.reply_to(message, message.text)
    print(message)


if HEROKU:
    print("HEROKU!!!")

    app = Flask(__name__)


    @app.route('/{}'.format(TOKEN_TG), methods=['POST'])
    def getMessage_():
        print("getMessage/token")
        bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
        return "?", 200


    @app.route("/")
    def webhook():
        print("webhook")
        bot.remove_webhook()
        print("SET WEBHOOK", bot.set_webhook(url='https://{}.herokuapp.com/'.format(TOKEN_APP_HEROKU) + TOKEN_TG))
        return "!", 200


    if __name__ == "__main__":
        app.run()


else:
    print("LOCAL!!!")
    if __name__ == "__main__":
        bot.remove_webhook()
        bot.polling()
