from components.templates import KEYBOARD_MESSAGES


def is_valid_message(text):
    return any(command in text for command in KEYBOARD_MESSAGES)
