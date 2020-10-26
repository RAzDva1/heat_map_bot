from flask import Flask, request
import os
import telebot
from apscheduler.schedulers.background import BackgroundScheduler
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

TOKEN_TG = os.getenv('TOKEN_TG')
TOKEN_APP_HEROKU = os.getenv('TOKEN_APP_HEROKU', '')
HEROKU = os.getenv('HEROKU', '')
CHROME_BINARY = os.getenv('CHROME_BINARY', '')
CHROME_DRIVER_PATH = os.getenv('CHROME_DRIVER_PATH', '')

URL = 'https://finviz.com/map.ashx'

data = {'User-Agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/50.0.2661.102 Safari/537.36'}

bot = telebot.TeleBot(TOKEN_TG)
print("TOKEN_TG", TOKEN_TG)
print("TOKEN_APP_HEROKU", TOKEN_APP_HEROKU)
print("CHROME_BINARY", CHROME_BINARY)
print("CHROME_DRIVER_PATH", CHROME_DRIVER_PATH)

def get_heat_map():
    """Thi function make request to finviz and get link for heat-map"""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = CHROME_BINARY
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")  # overcome limited resource problems
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, options=chrome_options)
    driver.get(URL)
    driver.find_element_by_id("share-map").click()
    element = WebDriverWait(driver, timeout=3).until(lambda d: d.find_element_by_id("static"))
    url_png = element.get_attribute("value")
    print(element.get_attribute("value"))
    driver.quit()
    return url_png


def send_message_by_scheldier(chat_id):
    print("Schediler")
    url_png = get_heat_map()
    bot.send_message(chat_id=chat_id, text=url_png)


sched = BackgroundScheduler(deamon=True)

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
        print("run")
        app.run()


else:
    print("LOCAL!!!")
    if __name__ == "__main__":
        print("run")
        bot.remove_webhook()
        bot.polling()
