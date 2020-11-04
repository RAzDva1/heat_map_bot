from telebot import types
from collections import defaultdict

header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/50.0.2661.102 Safari/537.36'}

START, ASK_USER, ADD_BD = range(3)

USER_STATE = defaultdict(lambda: START)


def get_state(message):
    return USER_STATE[message.chat.id]


def update_state(message, state):
    USER_STATE[message.chat.id] = state


def create_keyboard_is_mail():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(text=c, callback_data=c) for c in ["Yes", "No"]]
    keyboard.add(*buttons)
    return keyboard


def switch_command(command):
    return {
        "/SP500_d": ['', 'today'],
        "/SP500_w": ['?t=sec&st=w1', 'last week'],
        "/SP500_1m": ['?t=sec&st=w4', 'last month'],
        "/SP500_3m": ['?t=sec&st=w13', 'last three months'],
        "/SP500_6m": ['?t=sec&st=w26', 'last six months'],
        "/SP500_1y": ['?t=sec&st=w52', 'last year'],
        "/SP500_ytd": ['?t=sec&st=ytd', 'year to date']
    }.get(command, ['', 'today'])


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
            "/info - better do not touch it:)"
