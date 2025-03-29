import json


def update_admin_id(file_path="db/data.json", new_id=""):
    """Обновляет ADMIN_USER_ID в JSON-файле."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    data["ADMIN_USER_ID"] = new_id

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def clear_admin_id(file_path="db/data.json"):
    """Очищает ADMIN_USER_ID в JSON-файле."""
    update_admin_id(file_path, "")


def get_admin_id(file_path="db/data.json"):
    """Получает ADMIN_USER_ID из JSON-файла."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data.get("ADMIN_USER_ID", "")
    except (FileNotFoundError, json.JSONDecodeError):
        return ""
