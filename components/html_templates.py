from decimal import Decimal
import math
from collections import defaultdict

from logic.get_client_goods import get_user_data, get_check_track_code_user

with open("components/html/description.html", "r", encoding="utf-8") as file:
    DESCRIPTION_MESSAGE = file.read()


with open("components/html/issue_info_next.html", "r", encoding="utf-8") as file:
    ISSUE_INFO_NEXT_MESSAGE = file.read()


with open("components/html/update_bot.html", "r", encoding="utf-8") as file:
    UPDATE_TEXT_BOT = file.read()


async def get_goods_client(goods_data):
    with open("components/html/issue_info.html", "r", encoding="utf-8") as file:
        ISSUE_INFO_MESSAGE = file.read()

    name = goods_data["client_data"]["name"]
    goods = goods_data["client_data"]["goods"]
    full_price = int(float(goods_data["client_data"]["full_price"].replace(",", ".")) // 1 + 1)
    full_height = goods_data["client_data"]["full_height"]

    # Количество товаров
    total_goods_count = len(goods)
    full_total_price = math.ceil(sum(float(good['price'].replace(",", ".")) for good in goods))
    full_height_price = round(float(sum(Decimal(good['height'].replace(",", ".")) for good in goods)), 2)

    # Группируем по дате прибытия
    grouped_goods = defaultdict(list)
    for item in goods:
        arrival_date = item.get("arrival_date", "Неизвестная дата")  # Обязательно наличие даты
        grouped_goods[arrival_date].append(item)

    # Формируем текст по группам
    goods_text = "<b>📦Товары к получению:</b>\n\n"
    for date in sorted(grouped_goods.keys()):
        goods_text += f"<b>🗓️Дата прибытия - {date}</b>\n\n"
        for item in grouped_goods[date]:
            weight = item['height'].replace(".", ",")
            price = math.ceil(float(item['price'].replace(",", ".")))
            goods_text += (
                f"Трек-код: {item['track_code']}\n"
                f"Вес посылки: {weight} кг\n"
                f"Цена доставки: {price} сом\n\n"
            )

    # Подставляем в шаблон
    content = ISSUE_INFO_MESSAGE.format(name, goods_data["client_data"]["KK"], full_total_price, full_height_price, total_goods_count, goods_text.strip())
    return content


async def get_send_data_message(data):
    with open("components/html/send_cargo_data.html", "r", encoding="utf-8") as file:
        SEND_DATA_TEMPLATE = file.read()

    content = SEND_DATA_TEMPLATE.format(
        data["data"]["data"]["wlOrder"]["waybillNumber"],
        data["data"]["data"]["wlOrder"]["quantity"],
    )
    for dt in data["data"]["data"]["wlMessageList"][::-1]:
        track_code = dt["orderId"]
        mess = dt["elsAddress"]
        date = dt["dateTime"]
        print(mess)
        if "Код склада в Китае" in mess:
            mess = (
                "Посылка доставлена на наш склад в Китае и сейчас на этапе сортировки."
            )
            content += f"\n<b>Время: {date}</b>\n<b>Статус:</b> <i>{mess}</i>\n"

        elif "склад в Бишкеке" in mess:
            mess = ("Товар поступил на склад в Бишкеке и вот-вот начнется сортировка. Персонал уведомит наш офис КАРГО в течение 24 часов. Посылки доедут на наш пункт выдачи и будут доступны к получению в течение 72 часов.")
            content += f"\n<b>Время: {date}</b>\n<b>Статус:</b> <i>{mess}</i>\n"

            if get_check_track_code_user(track_code):
                new_status = "Посылка готова к выдачи. Вы можете забрать ее по адресу: город Ош, ул. Курманжан датка 236.\n\nhttps://go.2gis.com/5yJuh"
                content += f"\n<b>✅ Статус:</b> <i>{new_status}</i>\n"            
        else:
            content += f"\n<b>Время: {date}</b>\n<b>Статус:</b> <i>{mess}</i>\n"

    return content


async def get_goods_client_for_admin(goods_data):
    with open("components/html/admin_template.html", "r", encoding="utf-8") as file:
        ISSUE_INFO_MESSAGE_FOR_ADMIN = file.read()

    name = goods_data["client_data"]["name"]
    goods = goods_data["client_data"]["goods"]
    full_price = int(float(goods_data["client_data"]["full_price"].replace(",", ".")) // 1 + 1)
    full_height = goods_data["client_data"]["full_height"]

    full_total_price = math.ceil(sum(float(good['price'].replace(",", ".")) for good in goods))
    full_height_price = round(float(sum(Decimal(good['height'].replace(",", ".")) for good in goods)), 2)
    
    print(full_total_price)

    user_data = get_user_data(goods_data["client_data"]["KK"])
    surname = user_data[2]
    phone_number = user_data[3]

    # Количество товаров
    total_goods_count = len(goods)

    # Группировка по дате прибытия
    grouped_goods = defaultdict(list)
    for item in goods:
        arrival_date = item.get("arrival_date", "Неизвестная дата")
        grouped_goods[arrival_date].append(item)

    # Формируем блок с посылками
    goods_text = ""
    for date in sorted(grouped_goods.keys()):
        goods_text += f"<b>🗓️Дата прибытия - {date}</b>\n\n"
        for item in grouped_goods[date]:
            weight = item['height'].replace(".", ",")
            price = math.ceil(float(item['price'].replace(",", ".")))
            goods_text += (
                f"Трек-код: {item['track_code']}\n"
                f"Вес посылки: {weight} кг\n"
                f"Цена доставки: {price} сом\n\n"
            )

    # Формируем сообщение
    content = ISSUE_INFO_MESSAGE_FOR_ADMIN.format(
        name, surname, phone_number, goods_data["client_data"]["KK"], full_total_price, full_height_price, total_goods_count, goods_text.strip()
    )

    return content
