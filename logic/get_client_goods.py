import json
import gspread
from google.oauth2.service_account import Credentials

import logging
logging.basicConfig(level=logging.INFO)

scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
client = gspread.authorize(creds)

goods_sheet_id = "1C1oHa-aeRzKasCnEu_swMamEBCQ15AkZPUvrRuzQ9bg"
users_data_sheet_id = "1wHO5MzW9fVUTkwmKy5uulCHxujzF3_X001a0OCSJl3I"
workbook1 = client.open_by_key(goods_sheet_id)
workbook2 = client.open_by_key(users_data_sheet_id)
sheet = workbook1.worksheet("апрель")
sheet2 = workbook2.worksheet("База клиентов")


def get_user_data(client_id):
    data = sheet2.get_all_values()
    header = data[0]
    rows = data[1:]

    data = []
    for row in rows:
        if row[0] == client_id:
            data.append(row)

    
    return data[0] if data else "None"


def get_goods(client_id, client_name, admin = False):
    data = sheet.get_all_values()
    header = data[0]
    rows = data[1:]

    result = []
    temp_group = []
    client_data = {"goods": []}
    client_name = get_user_data(client_id)

    if admin:
        client_name = "ADMIN"

    
    print(client_name[1])
    logging.info(client_name[1])

    for row in rows:
        if any(row):
            temp_group.append(row)
        else:
            if any(r[-4] == "FALSE" for r in temp_group if r):
                result.extend(temp_group)
            temp_group = []

    if any(r[-4] == "FALSE" for r in temp_group if r):
        result.extend(temp_group)

    for row in result:
        if row[1] == client_id:
            client_data["KK"] = row[1]
            client_data["goods"].append(
                {"track_code": row[4], "height": row[5], "price": row[7]}
            )

            if row[2] and row[3] and row[-4]:
                logging.info(row[2])
                if client_name != "ADMIN":
                    if client_name[1].lower() not in row[2].lower():
                        return {"name_valid": False, "goods": True}

                client_data["status"] = row[-4]
                client_data["name"] = row[2]
                client_data["phone_number"] = row[3]
                client_data["full_price"] = row[-6]
                client_data["full_height"] = row[-5]
            else:
                return {"kk_code_not_valid": True, "goods": True}

    # print(json.dumps(client_data, indent=4))
    if not client_data["goods"]:
        return {"goods": False, "name": True}
    return {"client_data": client_data, "goods": True, "name_valid": True}



def update_checked_status(client_id):
    data = sheet.get_all_values()
    rows = data[1:]  # Пропускаем заголовки
    
    batch_updates = []
    
    for i, row in enumerate(rows, start=2):  # Индексируем с 2 (учет заголовка)
        if row[1] == client_id and row[10] == "FALSE":  # Колонка K (индекс 10)
            batch_updates.append({
                'range': f'K{i}',
                'values': [[True]]
            })

    if batch_updates:
        sheet.batch_update(batch_updates)

    return True
