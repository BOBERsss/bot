import pytest
import handlers


@pytest.fixture(autouse=True)
def reset_state():
    """Очищає стан магазину, балансів та інвентарю перед кожним тестом."""
    handlers.shop.clear()
    handlers.balances.clear()
    handlers.inventory.clear()


def test_start_and_help():
    assert "Олег" in handlers.start_text("Олег")
    assert "друже" in handlers.start_text("")
    assert "друже" in handlers.start_text(None)
    assert "/shop" in handlers.help_text()
    assert "/roll" in handlers.help_text()


def test_roll_adds_balance():
    uid = 101
    assert handlers.get_balance(uid) == 0

    res = handlers.roll_text(uid, 5)
    assert "5" in res
    assert handlers.get_balance(uid) == 5

    handlers.roll_text(uid, 3)
    assert handlers.get_balance(uid) == 8


def test_roll_invalid_number():
    with pytest.raises(ValueError):
        handlers.roll_text(101, 7)
    with pytest.raises(ValueError):
        handlers.roll_text(101, 0)


def test_shop_generation_and_reroll():
    uid = 101
    text = handlers.shop_html(uid)
    assert len(handlers.shop) == handlers.SHOP_SIZE
    assert "Магазин:" in text

    reroll_text = handlers.reroll_shop_html(uid)
    assert "Магазин оновлено!" in reroll_text
    assert len(handlers.shop) == handlers.SHOP_SIZE


def test_buy_item_success_and_insufficient_funds():
    uid = 101
    handlers.shop["1"] = {
        "name": "Pixel Pebble",
        "num": 777,
        "bg": "Gold",
        "price": 10,
        "url": "https://ton.org/nft",
    }

    # Спроба купити без грошей
    fail_msg = handlers.buy_item_text(uid, "1")
    assert "Не вистачає TON" in fail_msg
    assert len(handlers.inventory.get(uid, [])) == 0

    # Поповнюємо баланс і купуємо
    handlers.balances[uid] = 15
    ok_msg = handlers.buy_item_text(uid, "1")
    assert "Куплено" in ok_msg
    assert "Pixel Pebble #777" in ok_msg
    assert handlers.get_balance(uid) == 5
    assert len(handlers.inventory[uid]) == 1


def test_buy_invalid_slot():
    msg = handlers.buy_item_text(101, "99")
    assert "Немає такого номера" in msg


def test_bag_and_sell_item():
    uid = 101
    assert "Порожньо." in handlers.bag_html(uid)

    handlers.balances[uid] = 20
    handlers.inventory[uid] = [
        {
            "name": "Cyber Katana",
            "num": 1234,
            "bg": "Black",
            "price": 10,
            "url": "https://getgems.io",
        }
    ]

    bag = handlers.bag_html(uid)
    assert "Cyber Katana #1234" in bag
    assert "8 TON" in bag  # 10 * 0.8 = 8

    sell_msg = handlers.sell_item_text(uid, "1")
    assert "Продано" in sell_msg
    assert "+8 TON" in sell_msg
    assert handlers.get_balance(uid) == 28
    assert handlers.inventory[uid] == []


def test_sell_invalid_slot():
    assert "Невірний номер" in handlers.sell_item_text(101, "1")
    assert "Невірний номер" in handlers.sell_item_text(101, "abc")


def test_lucky_mult():
    assert handlers._lucky_mult(777) == 1.5
    assert handlers._lucky_mult(1111) == 1.5
    assert handlers._lucky_mult(1234) == 1.0