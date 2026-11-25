"""Логіка магазину NFT/подарунків: баланс, кубик, фони, номери та продаж."""

import random

ITEMS = [
    ("Pixel Pebble", 1, 3, "https://ton.org/nft"),
    ("Tiny Sticker", 1, 4, "https://getgems.io"),
    ("Rusty Bolt", 2, 4, "https://fragment.com"),
    ("Mini Spark", 2, 5, "https://getgems.io"),
    ("Snoop Mini", 5, 9, "https://fragment.com"),
    ("Shadow Core", 6, 11, "https://ton.org/nft"),
    ("Snoop Smoke", 8, 13, "https://fragment.com"),
    ("Cyber Katana", 9, 15, "https://getgems.io"),
    ("Snoop Crown", 10, 16, "https://ton.org/nft"),
    ("Pepe Spark", 18, 28, "https://getgems.io"),
    ("Pepe Chill", 22, 34, "https://getgems.io"),
    ("Neon Spider", 25, 40, "https://fragment.com"),
    ("Pepe King", 30, 48, "https://getgems.io"),
    ("Pepe Sovereign", 36, 55, "https://getgems.io"),
]

BACKGROUNDS = {"White": 1.0, "Silver": 1.2, "Gold": 1.5, "Black": 2.0}
SHOP_SIZE = 7
SELL_RATE = 0.8

shop = {}       # "1".."7" -> поточний лот
balances = {}   # user_id -> баланс у TON
inventory = {}  # user_id -> список куплених лотів


def _fmt(num):
    num = round(num, 2)
    return int(num) if float(num).is_integer() else num


def _lucky_mult(number):
    digits = str(number)
    return 1.5 if len(digits) >= 2 and len(set(digits)) == 1 else 1.0


def _make_lot(gift):
    name, lo, hi, url = gift
    num = random.randint(100, 9999)
    bg, bg_mult = random.choice(list(BACKGROUNDS.items()))
    base = random.uniform(lo, hi)
    price = _fmt(base * bg_mult * _lucky_mult(num))
    return {"name": name, "num": num, "bg": bg, "price": price, "url": url}


def _fill_shop():
    shop.clear()
    picked = random.sample(ITEMS, k=min(SHOP_SIZE, len(ITEMS)))
    random.shuffle(picked)
    for i, gift in enumerate(picked, start=1):
        shop[str(i)] = _make_lot(gift)


def get_balance(user_id):
    return balances.get(user_id, 0)


def start_text(first_name):
    name = (first_name or "друже").strip() or "друже"
    return f"Привіт, <b>{name}</b>! Кидай кубик, крути рерол і купуй подарунки."


def help_text():
    return (
        "<b>Команди:</b>\n"
        "/shop — магазин\n"
        "/reroll — перемішати й оновити магазин\n"
        "/balance — баланс\n"
        "/buy 1 — купити лот №1\n"
        "/bag — інвентар\n"
        "/sell 1 — продати предмет №1 з інвентарю\n"
        "/roll — кубик (+1..6 TON)"
    )


def balance_text(user_id):
    return f"Твій баланс: <b>{get_balance(user_id)} TON</b>"


def shop_html(user_id):
    if not shop:
        _fill_shop()
    lines = [f"Твій баланс: <b>{get_balance(user_id)} TON</b>", "", "<b>Магазин:</b>"]
    for k, lot in shop.items():
        lines.append(
            f'[{k}] <a href="{lot["url"]}">{lot["name"]} #{lot["num"]}</a> — '
            f'<b>{lot["price"]} TON</b> (фон: <b>{lot["bg"]}</b>)'
        )
    lines.append("\nКупити: <code>/buy 1</code> | Оновити: /reroll")
    return "\n".join(lines)


def reroll_shop_html(user_id):
    _fill_shop()
    return "<b>Магазин оновлено!</b>\n\n" + shop_html(user_id)


def buy_item_text(user_id, item_id):
    if not shop:
        _fill_shop()
    lot = shop.get(str(item_id).strip())
    if not lot:
        return "Немає такого номера в магазині. Відкрий /shop."

    bal = get_balance(user_id)
    if bal < lot["price"]:
        return f"Не вистачає TON (треба <b>{lot['price']}</b>, є <b>{bal}</b>). Кидай /roll!"

    balances[user_id] = _fmt(bal - lot["price"])
    inventory.setdefault(user_id, []).append(dict(lot))
    _fill_shop()  # оновлюємо і перемішуємо вітрину після покупки

    return (
        f'Куплено <a href="{lot["url"]}">{lot["name"]} #{lot["num"]}</a> '
        f'(<b>{lot["bg"]}</b>) за <b>{lot["price"]} TON</b>.\n'
        f'Баланс: <b>{balances[user_id]} TON</b>'
    )


def bag_html(user_id):
    items = inventory.get(user_id, [])
    lines = [f"Твій баланс: <b>{get_balance(user_id)} TON</b>", "", "<b>Інвентар:</b>"]
    if not items:
        lines.append("Порожньо.")
        return "\n".join(lines)

    for i, lot in enumerate(items, start=1):
        sell_price = _fmt(lot["price"] * SELL_RATE)
        lines.append(
            f'{i}. <a href="{lot["url"]}">{lot["name"]} #{lot["num"]}</a> — '
            f'<b>{lot["bg"]}</b>, <b>{lot["price"]} TON</b> (продаж: <b>{sell_price} TON</b>)'
        )
    lines.append("\nПродати: <code>/sell 1</code>")
    return "\n".join(lines)


def sell_item_text(user_id, slot_number):
    items = inventory.get(user_id, [])
    try:
        idx = int(str(slot_number).strip()) - 1
        lot = items.pop(idx)
    except (ValueError, IndexError):
        return "Невірний номер предмета. Перевір /bag і напиши, наприклад, <code>/sell 1</code>."

    refund = _fmt(lot["price"] * SELL_RATE)
    balances[user_id] = _fmt(get_balance(user_id) + refund)
    return (
        f'Продано <a href="{lot["url"]}">{lot["name"]} #{lot["num"]}</a> за <b>+{refund} TON</b>.\n'
        f'Баланс: <b>{balances[user_id]} TON</b>'
    )


def roll_text(user_id, number):
    if not isinstance(number, int) or not 1 <= number <= 6:
        raise ValueError("Число має бути від 1 до 6")
    new_bal = _fmt(get_balance(user_id) + number)
    balances[user_id] = new_bal
    return f"Кубик: <b>{number}</b> (+<b>{number} TON</b>). Баланс: <b>{new_bal} TON</b>"


def unknown_text():
    return "Невідома команда. Натисни <b>Допомога</b> або /help."