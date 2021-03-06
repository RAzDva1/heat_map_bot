from flask import Flask, request
import os
import telebot
from apscheduler.schedulers.background import BackgroundScheduler
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import requests
import time
import database_api as db
import config as bl
import datetime
from flask import render_template
from telebot.apihelper import ApiException

TOKEN_TG = os.getenv('TOKEN_TG')
TOKEN_APP_HEROKU = os.getenv('TOKEN_APP_HEROKU', '')
HEROKU = os.getenv('HEROKU', '')
CHROME_BINARY = os.getenv('CHROME_BINARY', '')
CHROME_DRIVER_PATH = os.getenv('CHROME_DRIVER_PATH', '')

URL = 'https://finviz.com/map.ashx'

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
    req = requests.get(url_png, headers=bl.header)
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


def send_message_by_scheldier(command=''):
    print("Schediler")
    print(command)
    list_chat_id = db.select_users_for_mail()
    print(list_chat_id)
    get_heat_map(URL + bl.switch_command(command)[0])
    for chat_id in list_chat_id:
        with open("image.png", 'rb') as image:
            try:
                bot.send_photo(chat_id=chat_id[0], photo=image, caption='end of week' if command == '/SP500_w' else '')
            except ApiException:
                print("Can't send to {}".format(chat_id[0]))
                db.change_state_email(user_id=chat_id[0], is_mailing=False)


@bot.message_handler(commands=['start'])
def start(message):
    db.add_user(user_id=message.chat.id, lang_code=message.from_user.language_code,
                first_name=message.from_user.first_name)
    keyboard = bl.create_keyboard_is_mail()
    bot.send_message(chat_id=message.chat.id, text="Okay, do you want to receive daily email at 10.05 am, "
                                                   "4.05 pm and in Friday at 23.05 pm (week frame)",
                     reply_markup=keyboard)
    bl.update_state(message, bl.ASK_USER)


@bot.callback_query_handler(func=lambda x: bl.get_state(x.message) == bl.ASK_USER)
def callback_handler_photo(callback_query):
    message = callback_query.message
    text = callback_query.data
    if text == "Yes":
        bot.send_message(chat_id=message.chat.id, text="Ok, we will send you daily HeatMap")
        bl.update_state(message, bl.ADD_BD)
        db.change_state_email(user_id=message.chat.id, is_mailing=True)
    else:
        bot.send_message(chat_id=message.chat.id, text="Ok, we won't send you HeatMap")
    help_f(message)


@bot.message_handler(commands=['stop'])
def stop(message):
    db.change_state_email(user_id=message.chat.id, is_mailing=False)
    bot.send_message(chat_id=message.chat.id, text="Ok, now we won't send you HeatMap")


@bot.message_handler(commands=['info'])
def info(message):
    text = "Ok, you can send me you suggestions about improving this bot.\n" \
           "Also if you have interest ideas about automating actions in stock market by bots, " \
           "that really excite you, so write me, and we implement them together!\n" \
           "With best regards, @RazDva_12"
    bot.send_message(chat_id=message.chat.id, text=text)


@bot.message_handler(commands=['help'])
def help_f(message):
    bot.send_message(chat_id=message.chat.id, text=bl.TEXT_HELP)


@bot.message_handler(commands=['SP500_d', 'SP500_w', 'SP500_1m', 'SP500_3m', 'SP500_6m', 'SP500_1y', 'SP500_ytd'])
def sp500_d(message):
    print("SW:", bl.switch_command(message.text))
    get_heat_map(URL + bl.switch_command(message.text)[0])
    with open("image.png", 'rb') as image:
        try:
            bot.send_photo(chat_id=message.chat.id, photo=image, caption="SP500 {}".
                           format(bl.switch_command(message.text)[1]))
        except ApiException:
            print("Can't send to {}".format(message.chat.id))
            db.change_state_email(user_id=message.chat.id, is_mailing=False)


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
                  day='*', week='*', day_of_week='0-4',
                  hour='7,13', minute='05', second=30)
    sched.add_job(send_message_by_scheldier, 'cron', args=['/SP500_w'], year='*', month='*',
                  day='*', week='*', day_of_week='4',
                  hour='20', minute='5', second='10')
    sched.start()


    @app.route("/admino4ka")
    def admin():
        print("admino4ka")
        amount_all_usres = db.get_count_all_users()[0]
        amount_active_usres = db.get_count_active_users()[0]
        amount_russians_users = db.get_count_russian_users()[0]

        return render_template('index.html', content=[
            {'designation': 'Amount of all users', 'value': amount_all_usres},
            {'designation': 'Amount of active users', 'value': amount_active_usres},
            {'designation': 'Percentage of Russians user',
             'value': '{}%'.format(round(amount_russians_users / amount_all_usres * 100, 2))}
        ])


    @app.route("/plug")
    def plug():
        print("plug")
        return "!!!", 200


    @app.route('/{}'.format(TOKEN_TG), methods=['POST'])
    def get_message():
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
        sched = BackgroundScheduler(deamon=True)
        sched.add_job(send_message_by_scheldier, 'cron', args=['/SP500_d'], year='*', month='*',
                      day='*', week='*', day_of_week='*',
                      hour='10,16', minute='*', second=30)
        sched.add_job(send_message_by_scheldier, 'cron', year='*', month='*',
                      day='*', week='*', day_of_week='*',
                      hour='*', minute='35', second='50')
        sched.add_job(send_message_by_scheldier, 'cron', args=['/SP500_w'], year='*', month='*',
                      day='*', week='*', day_of_week='*',
                      hour='*', minute='5', second='20')
        sched.start()
        bot.remove_webhook()
        bot.polling()
