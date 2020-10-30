from flask import Flask, request
import os
import telebot
from apscheduler.schedulers.background import BackgroundScheduler
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import requests
import time
import database_api as db
import business_logic as bl
import datetime

TOKEN_TG = os.getenv('TOKEN_TG')
TOKEN_APP_HEROKU = os.getenv('TOKEN_APP_HEROKU', '')
HEROKU = os.getenv('HEROKU', '')
CHROME_BINARY = os.getenv('CHROME_BINARY', '')
CHROME_DRIVER_PATH = os.getenv('CHROME_DRIVER_PATH', '')

URL = 'https://finviz.com/map.ashx'

data = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/50.0.2661.102 Safari/537.36'}

bot = telebot.TeleBot(TOKEN_TG)

CHROME_OPTIONS = ''
print("TOKEN_TG", TOKEN_TG)
print("TOKEN_APP_HEROKU", TOKEN_APP_HEROKU)
print("CHROME_BINARY", CHROME_BINARY)
print("CHROME_DRIVER_PATH", CHROME_DRIVER_PATH)



def init_chrome_options():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = CHROME_BINARY
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")  # overcome limited resource problems
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    return chrome_options


def get_chrome_options():
    return CHROME_OPTIONS


def get_heat_map(url):
    """Thi function make request to finviz and get link for heat-map"""
    driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, options=get_chrome_options())
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
    driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, options=get_chrome_options())
    driver.get(url)
    driver.find_element_by_id("share-map").click()
    element = WebDriverWait(driver, timeout=3).until(lambda d: d.find_element_by_id("static"))
    url_png = element.get_attribute("value")
    print(element.get_attribute("value"))
    driver.quit()
    return url_png


def send_message_by_scheldier():
    print("Schediler")
    list_chat_id = db.select_users_for_mail()
    print(list_chat_id)
    get_heat_map(URL)
    for chat_id in list_chat_id:
        with open("image.png", 'rb') as image:
            bot.send_photo(chat_id=chat_id[0], photo=image)


sched = BackgroundScheduler(deamon=True)
sched.add_job(send_message_by_scheldier, 'cron', year='*', month='*',
                      day='*', week='*', day_of_week='*',
                      hour='10,16', minute='*', second=30)
sched.add_job(send_message_by_scheldier, 'cron', year='*', month='*',
                      day='*', week='*', day_of_week='*',
                      hour='*', minute='*', second='0,10,20,30,40,50')
sched.start()


@bot.message_handler(commands=['start'])
def start(message):
    db_req = db.select_users_for_mail()
    print(db_req)
    for chat_id in db_req:
        print(chat_id[0])
    db.add_user(user_id=message.chat.id, lang_code=message.from_user.language_code,
                first_name=message.from_user.first_name)
    keyboard = bl.create_keyboard_is_photo()
    bot.send_message(chat_id=message.chat.id, text="Okay, do you want to receive  daily email?",
                     reply_markup=keyboard)
    bl.update_state(message, bl.ASK_USER)


@bot.callback_query_handler(func=lambda x: bl.get_state(x.message) == bl.ASK_USER)
def callback_handler_photo(callback_query):
    message = callback_query.message
    text = callback_query.data
    if text == "Yes":
        bot.send_message(chat_id=message.chat.id, text="Ok, we will send you HeatMap at 10.05 am and"
                                                       "at 4.05 pm")
        bl.update_state(message, bl.ADD_BD)
        db.change_state_email(user_id=message.chat.id, is_mailing=True)
    else:
        bot.send_message(chat_id=message.chat.id, text="Ok, we won't send you HeatMap")
    help_f(message)


@bot.message_handler(commands=['stop'])
def stop(message):
    db.change_state_email(user_id=message.chat.id, is_mailing=False)
    bot.send_message(chat_id=message.chat.id, text="Ok, now we won't send you HeatMap")


@bot.message_handler(commands=['schedule'])
def help_f(message):
    bot.send_message(chat_id=message.chat.id, text="#TODO")
    users = db.select_users_for_mail()
    text = "users:"
    for user in users:
        text += str(user[0]) + " "
    bot.send_message(chat_id=353688371, text=text)


TEXT_HELP = "I can execute several commands: \n" \
            "/SP500_d - S&P500 today \n" \
            "/SP500_w - S&P500 last week \n" \
            "/SP500_1m - S&P500 last month \n" \
            "/SP500_3m - S&P500 last 3 months\n" \
            "/SP500_6m - S&P500 last 6 months\n" \
            "/SP500_1y - S&P500 last year\n" \
            "/SP500_ytd - S&P500 year to date\n" \
            "/help - commands list\n" \
            "/start - start sending daily HeatMap\n" \
            "/stop - stop sending daily HeatMap\n" \
            "/schedule - custom time to get HeatMap"


@bot.message_handler(commands=['help'])
def help_f(message):
    bot.send_message(chat_id=message.chat.id, text=TEXT_HELP)


def switch_command(command):
    return {
        "/SP500_d": ['', 'today'],
        "/SP500_w": ['?t=sec&st=w1', 'last week'],
        "/SP500_1m": ['?t=sec&st=w4', 'last month'],
        "/SP500_3m": ['?t=sec&st=w13', 'last three months'],
        "/SP500_6m": ['?t=sec&st=w26', 'last six months'],
        "/SP500_1y": ['?t=sec&st=w52', 'last year'],
        "/SP500_ytd": ['?t=sec&st=ytd', 'year to date']
    }.get(command, '')


@bot.message_handler(commands=['SP500_d', 'SP500_w', 'SP500_1m', 'SP500_3m', 'SP500_6m', 'SP500_1y', 'SP500_ytd'])
def sp500_d(message):
    get_heat_map(URL + switch_command(message.text)[0])
    with open("image.png", 'rb') as image:
        bot.send_photo(chat_id=message.chat.id, photo=image, caption="SP500 {}".
                       format(switch_command(message.text)[1]))


@bot.message_handler(commands=['SP500_tst_link'])
def sp500_tst_link(message):
    start_t = time.time()
    amount = 20
    for _ in range(amount):
        url_png = get_heat_map_link(URL + '?t=sec&st=ytd')
        bot.send_message(chat_id=message.chat.id, text="Test {}".format(_))
        bot.send_message(chat_id=message.chat.id, text=url_png)
    delta = (time.time() - start_t) / amount
    print(delta)
    bot.send_message(chat_id=message.chat.id, text="I try to make {} requests send link. {} is mean "
                                                   "of 1 request".format(amount, round(delta, 4)))


@bot.message_handler(commands=['SP500_tst_file'])
def sp500_tst_file(message):
    start_t = time.time()
    amount = 20
    for _ in range(amount):
        get_heat_map_link(URL + '?t=sec&st=ytd')
        with open("image.png", 'rb') as image:
            bot.send_message(chat_id=message.chat.id, text="Test {}".format(_))
            bot.send_photo(chat_id=message.chat.id, photo=image)
    delta = (time.time() - start_t) / amount
    print(delta)
    bot.send_message(chat_id=message.chat.id, text="I try to make {} requests save image. {} is mean "
                                                   "of 1 request and save".format(amount, round(delta, 4)))


@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    print("echo")
    bot.reply_to(message, message.text)


if HEROKU:
    print("HEROKU!!!")
    print("TIME: ", datetime.datetime.now())

    app = Flask(__name__)
    CHROME_OPTIONS = init_chrome_options()
    db.init_db()
    sched = BackgroundScheduler(deamon=True)
    sched.add_job(send_message_by_scheldier, 'cron', year='*', month='*',
                  day='*', week='*', day_of_week='*',
                  hour='*', minute='05', second=30)
    sched.start()


    @app.route("/plug")
    def plug():
        print("plug")
        return "!!!", 200


    @app.route('/{}'.format(TOKEN_TG), methods=['POST'])
    def get_message():
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
        print("TIME: ", datetime.datetime.now())
        CHROME_OPTIONS = init_chrome_options()
        db.init_db()

        bot.remove_webhook()
        bot.polling()

# TODO
''' 
American stocks exchange open at 16:00 (Moscow) and close at 23:00
HeatMap, [26.10.20 20:14]
[In reply to Valentin]
I try to make 20 requests send link. 7.6293 is mean of 1 request

HeatMap, [26.10.20 20:14]
[In reply to Valentin]
I try to make 20 requests save image. 7.439 is mean of 1 request and save
'''
