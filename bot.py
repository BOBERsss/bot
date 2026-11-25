"""Точка входу: приймає команди й кнопки та передає їх у handlers."""

import random

import telebot
from telebot import types

import handlers
from config import require_token

bot = telebot.TeleBot(require_token())

BUTTONS = {
    "Магазин": lambda m, uid: handlers.shop_html(uid),
    "Рерол": lambda m, uid: handlers.reroll_shop_html(uid),
    "Мій інвентар": lambda m, uid: handlers.bag_html(uid),
    "Мій баланс": lambda m, uid: handlers.balance_text(uid),
    "Кубик": lambda m, uid: handlers.roll_text(uid, random.randint(1, 6)),
    "Допомога": lambda m, uid: handlers.help_text(),
}


def send(chat_id, text, markup=None):
    bot.send_message(
        chat_id,
        text,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=markup,
    )


def uid_from(message):
    return message.from_user.id if message.from_user else message.chat.id


def arg_from(message):
    parts = (message.text or "").split(maxsplit=1)
    return parts[1] if len(parts) > 1 else ""


def keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("Магазин", "Рерол", "Мій інвентар", "Мій баланс", "Кубик", "Допомога")
    return kb


@bot.message_handler(commands=["start"])
def on_start(message):
    name = message.from_user.first_name if message.from_user else None
    send(message.chat.id, handlers.start_text(name), keyboard())


@bot.message_handler(commands=["help"])
def on_help(message):
    send(message.chat.id, handlers.help_text())


@bot.message_handler(commands=["shop"])
def on_shop(message):
    send(message.chat.id, handlers.shop_html(uid_from(message)))


@bot.message_handler(commands=["reroll"])
def on_reroll(message):
    send(message.chat.id, handlers.reroll_shop_html(uid_from(message)))


@bot.message_handler(commands=["balance"])
def on_balance(message):
    send(message.chat.id, handlers.balance_text(uid_from(message)))


@bot.message_handler(commands=["bag"])
def on_bag(message):
    send(message.chat.id, handlers.bag_html(uid_from(message)))


@bot.message_handler(commands=["buy"])
def on_buy(message):
    send(message.chat.id, handlers.buy_item_text(uid_from(message), arg_from(message)))


@bot.message_handler(commands=["sell"])
def on_sell(message):
    send(message.chat.id, handlers.sell_item_text(uid_from(message), arg_from(message)))


@bot.message_handler(commands=["roll"])
def on_roll(message):
    send(message.chat.id, handlers.roll_text(uid_from(message), random.randint(1, 6)))


@bot.message_handler(content_types=["text"])
def on_text(message):
    action = BUTTONS.get((message.text or "").strip())
    if action:
        send(message.chat.id, action(message, uid_from(message)))
    else:
        send(message.chat.id, handlers.unknown_text())


if __name__ == "__main__":
    print("Бот запущений. Зупинити: Ctrl+C")
    bot.infinity_polling(skip_pending=True)