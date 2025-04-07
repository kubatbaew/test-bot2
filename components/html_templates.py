from decimal import Decimal
import math

from logic.get_client_goods import get_user_data

with open("components/html/description.html", "r", encoding="utf-8") as file:
    DESCRIPTION_MESSAGE = file.read()


with open("components/html/issue_info_next.html", "r", encoding="utf-8") as file:
    ISSUE_INFO_NEXT_MESSAGE = file.read()


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


    goods_text = "\n".join(
        f"Трек-код: {item['track_code']}\n"
        f"Вес посылки: {item['height']} кг\n"
        f"Цена доставки: {math.ceil(float(item['price'].replace(',', '.')))} сом\n"
        for item in goods
    )

    content = ISSUE_INFO_MESSAGE.format(name, full_total_price, full_height_price, total_goods_count, goods_text)
    return content


async def get_send_data_message(data):
    with open("components/html/send_cargo_data.html", "r", encoding="utf-8") as file:
        SEND_DATA_TEMPLATE = file.read()

    content = SEND_DATA_TEMPLATE.format(
        data["data"]["data"]["wlOrder"]["waybillNumber"],
        data["data"]["data"]["wlOrder"]["quantity"],
    )
    for dt in data["data"]["data"]["wlMessageList"][::-1]:
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
            content += f"\n<b>Время: {date}</b>\n<b>✅ Статус:</b> <i>{mess}</i>\n"
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

    goods_text = "\n".join(
        f"<b>Трек-код:</b> {item['track_code']}\n"
        f"<b>Вес посылки:</b> {item['height']} кг\n"
        f"<b>Цена доставки:</b> {math.ceil(float(item['price'].replace(',', '.')))} сом\n\n"
        for item in goods
    )

    content = ISSUE_INFO_MESSAGE_FOR_ADMIN.format(name, surname, phone_number,full_total_price, full_height_price, total_goods_count, goods_text)
    return content
