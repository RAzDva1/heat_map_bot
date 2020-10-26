from flask import Flask, request
import os
import telebot
from apscheduler.schedulers.background import BackgroundScheduler
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import requests
import time

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

def get_heat_map(url):
    """Thi function make request to finviz and get link for heat-map"""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = CHROME_BINARY
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")  # overcome limited resource problems
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, options=chrome_options)
    driver.get(url)
    driver.find_element_by_id("share-map").click()
    element = WebDriverWait(driver, timeout=3).until(lambda d: d.find_element_by_id("static"))
    url_png = element.get_attribute("value")
    print(element.get_attribute("value"))
    driver.quit()
    req = requests.get(url_png, headers=data)
    with open("image.png", 'wb') as image:
        image.write(req.content)
    return url_png


def get_heat_map_link(url):
    """Thi function make request to finviz and get link for heat-map"""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = CHROME_BINARY
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")  # overcome limited resource problems
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, options=chrome_options)
    driver.get(url)
    driver.find_element_by_id("share-map").click()
    element = WebDriverWait(driver, timeout=3).until(lambda d: d.find_element_by_id("static"))
    url_png = element.get_attribute("value")
    print(element.get_attribute("value"))
    driver.quit()
    return url_png


def send_message_by_scheldier(chat_id):
    print("Schediler")
    url_png = get_heat_map(URL)
    bot.send_message(chat_id=chat_id, text=url_png)


sched = BackgroundScheduler(deamon=True)

'''
sched.add_job(send_message_by_scheldier, 'cron', args=[353688371], year='*', month='*',
              day='*', week='*', day_of_week='*',
              hour='*', minute='*', second=15)

sched.add_job(send_message_by_scheldier, 'cron', args=[353688371], year='*', month='*',
              day='*', week='*', day_of_week='*',
              hour='*', minute='*', second=30)

sched.add_job(send_message_by_scheldier, 'cron', args=[353688371], year='*', month='*',
              day='*', week='*', day_of_week='*',
              hour='*', minute='*', second=45)
              '''

sched.start()


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 'Hello, ' + message.from_user.first_name)
    sched.add_job(send_message_by_scheldier, 'cron', args=[message.chat.id], year='*', month='*',
                  day='*', week='*', day_of_week='*',
                  hour='*', minute='*', second=50)


TEXT_HELP = "I can execute several commands: \n " \
            "/SP500_d - S&P500 today \n" \
            "/SP500_w - S&P500 last week \n" \
            "/SP500_1m - S&P500 last month \n" \
            "/SP500_3m - S&P500 last 3 months\n" \
            "/SP500_6m - S&P500 last 6 months\n" \
            "/SP500_1y - S&P500 last year\n" \
            "/SP500_ydp - S&P500 year to date perfomance\n" \
            "/help - commands list"


@bot.message_handler(commands=['help'])
def start(message):
    bot.send_message(chat_id=message.chat.id, text=TEXT_HELP)


@bot.message_handler(commands=['SP500_d'])
def start(message):
    url_png = get_heat_map(URL)
    with open("image.png", 'rb') as image:
        bot.send_message(chat_id=message.chat.id, text="SP500 today")
        bot.send_photo(chat_id=message.chat.id, photo=image)


@bot.message_handler(commands=['SP500_w'])
def start(message):
    url_png = get_heat_map(URL + '?t=sec&st=w1')
    with open("image.png", 'rb') as image:
        bot.send_message(chat_id=message.chat.id, text="SP500 last week")
        bot.send_photo(chat_id=message.chat.id, photo=image)


@bot.message_handler(commands=['SP500_1m'])
def start(message):
    url_png = get_heat_map(URL + '?t=sec&st=w4')
    with open("image.png", 'rb') as image:
        bot.send_message(chat_id=message.chat.id, text="SP500 last month")
        bot.send_photo(chat_id=message.chat.id, photo=image)


@bot.message_handler(commands=['SP500_3m'])
def start(message):
    url_png = get_heat_map(URL + '?t=sec&st=w13')
    with open("image.png", 'rb') as image:
        bot.send_message(chat_id=message.chat.id, text="SP500 last three months")
        bot.send_photo(chat_id=message.chat.id, photo=image)


@bot.message_handler(commands=['SP500_6m'])
def start(message):
    url_png = get_heat_map(URL + '?t=sec&st=w26')
    with open("image.png", 'rb') as image:
        bot.send_message(chat_id=message.chat.id, text="SP500 last six months")
        bot.send_photo(chat_id=message.chat.id, photo=image)


@bot.message_handler(commands=['SP500_1y'])
def start(message):
    url_png = get_heat_map(URL + '?t=sec&st=w52')
    with open("image.png", 'rb') as image:
        bot.send_message(chat_id=message.chat.id, text="SP500 last year")
        bot.send_photo(chat_id=message.chat.id, photo=image)


@bot.message_handler(commands=['SP500_ydp'])
def start(message):
    url_png = get_heat_map(URL + '?t=sec&st=ytd')
    with open("image.png", 'rb') as image:
        bot.send_message(chat_id=message.chat.id, text="SP500 yaer to date perfomance")
        bot.send_photo(chat_id=message.chat.id, photo=image)


@bot.message_handler(commands=['SP500_tst_link'])
def start(message):
    start = time.time()
    amount = 20
    for _ in range(amount):
        url_png = get_heat_map_link(URL + '?t=sec&st=ytd')
        bot.send_message(chat_id=message.chat.id, text="Test {}".format(_))
        bot.send_message(chat_id=message.chat.id, text=url_png)
    delta = (time.time() - start)/amount
    print(delta)
    bot.send_message(chat_id=message.chat.id, text="I try to make {} requests send link. {} is mean "
                                                   "of 1 request".format(amount, round(delta, 4)))


@bot.message_handler(commands=['SP500_tst_file'])
def start(message):
    start = time.time()
    amount = 20
    for _ in range(amount):
        url_png = get_heat_map_link(URL + '?t=sec&st=ytd')
        with open("image.png", 'rb') as image:
            bot.send_message(chat_id=message.chat.id, text="Test {}".format(_))
            bot.send_photo(chat_id=message.chat.id, photo=image)
    delta = (time.time() - start)/amount
    print(delta)
    bot.send_message(chat_id=message.chat.id, text="I try to make {} requests save image. {} is mean "
                                                   "of 1 request and save".format(amount, round(delta, 4)))


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

#TODO
''' 
American stocks exchange open at 16:00 (Moscow) and close at 23:00
HeatMap, [26.10.20 20:14]
[In reply to Valentin]
I try to make 20 requests send link. 7.6293 is mean of 1 request

HeatMap, [26.10.20 20:14]
[In reply to Valentin]
I try to make 20 requests save image. 7.439 is mean of 1 request and save
'''
