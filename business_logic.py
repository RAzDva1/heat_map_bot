from telebot import types
from collections import defaultdict


START, ASK_USER, ADD_BD = range(3)

USER_STATE = defaultdict(lambda: START)


def get_state(message):
    return USER_STATE[message.chat.id]


def update_state(message, state):
    USER_STATE[message.chat.id] = state


def create_keyboard_is_photo():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(text=c, callback_data=c) for c in ["Yes", "No"]]
    keyboard.add(*buttons)
    return keyboard
