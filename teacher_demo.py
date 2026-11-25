"""Демонстрація на початку уроку. Зупини перед запуском bot.py!"""

import random

import telebot

from config import require_token

bot = telebot.TeleBot(require_token())
quiz_waiting = set()  # chat_id користувачів, які відповідають на вікторину
hero_health = {}      # chat_id -> здоров'я героя


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "Вітаю в Python Quest! Команди: /roll, /quiz, /fight, /help",
    )


@bot.message_handler(commands=["help"])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "/roll - кубик; /quiz - питання; /fight - битва з монстром",
    )


@bot.message_handler(commands=["roll"])
def roll(message):
    bot.send_message(message.chat.id, f"Кубик: {random.randint(1, 6)}")


@bot.message_handler(commands=["quiz"])
def quiz(message):
    quiz_waiting.add(message.chat.id)
    bot.send_message(
        message.chat.id,
        "Яка команда в Python виводить текст на екран? Напиши її назву.",
    )


@bot.message_handler(commands=["fight"])
def fight(message):
    chat_id = message.chat.id
    hp = hero_health.get(chat_id, 10)
    damage = random.randint(1, 4)
    hp = max(0, hp - damage)
    hero_health[chat_id] = hp
    if hp == 0:
        hero_health[chat_id] = 10
        bot.send_message(chat_id, f"Монстр завдав {damage} шкоди. Герой програв! ")
        bot.send_message(chat_id, "Нова спроба: здоров'я знову 10.")
    else:
        bot.send_message(chat_id, f"Монстр завдав {damage}. Залишилося HP: {hp}.")


@bot.message_handler(content_types=["text"])
def check_reply(message):
    if message.chat.id in quiz_waiting:
        quiz_waiting.remove(message.chat.id)
        answer = (message.text or "").strip().lower()
        if answer in {"print", "print()"}:
            bot.send_message(message.chat.id, "Правильно! Вітаю!")
        else:
            bot.send_message(message.chat.id, "Поки ні. Правильна відповідь: print.")
    else:
        bot.send_message(message.chat.id, "Не знаю такої команди. Введи /help.")


if __name__ == "__main__":
    print("Демонстраційний бот запущений. Ctrl+C - зупинити")
    bot.infinity_polling(skip_pending=True)
