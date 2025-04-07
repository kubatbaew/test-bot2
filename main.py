import logging
import sys
import asyncio

from os import getenv
from aiogram.types import FSInputFile
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
import ssl

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext


from configs import BOT_TOKEN, ADMIN_USER_ID
from components import templates
from keyboards.main_keyboard import main_keyboard
from handlers import menu_handlers, state_handlers
from admin.state import AdminLoginState

from admin.keyboard import admin_keyboard
from admin.handlers import admin_router

from filters.filters import MainFilter
from db import query



# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="bot.log",  # Логи будут записываться в этот файл
    filemode="a"  # Открытие файла в режиме добавления
)

logger = logging.getLogger(__name__)

SELF_SSL = True

# Path to webhook route, on which Telegram will send requests
WEBHOOK_PATH = "/" + getenv("PROJECT_NAME")

DOMAIN = getenv("DOMAIN_IP") if SELF_SSL else getenv("DOMAIN_NAME")
EXTERNAL_PORT = 8443

# Base URL for webhook will be used to generate webhook URL for Telegram,
# in this example it is used public DNS with HTTPS support
# BASE_WEBHOOK_URL = "https://aiogram.dev/"
BASE_WEBHOOK_URL = "https://" + DOMAIN + ":" + str(EXTERNAL_PORT)

if SELF_SSL:
    WEB_SERVER_HOST = DOMAIN
    WEB_SERVER_PORT = EXTERNAL_PORT
else:
    # Webserver settings
    # bind localhost only to prevent any external access
    WEB_SERVER_HOST = "127.0.0.1"
    # Port for incoming request from reverse proxy. Should be any available port
    WEB_SERVER_PORT = 8080

# Secret key to validate requests from Telegram (optional)
WEBHOOK_SECRET = "my-secret"

# ========= For self-signed certificate =======
# Path to SSL certificate and private key for self-signed certificate.
# WEBHOOK_SSL_CERT = "/path/to/cert.pem"
# WEBHOOK_SSL_PRIV = "/path/to/private.key"
if SELF_SSL:
    WEBHOOK_SSL_CERT = "../SSL/" + DOMAIN + ".self.crt"
    WEBHOOK_SSL_PRIV = "../SSL/" + DOMAIN + ".self.key"




dp = Dispatcher()
bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    if message.from_user.id in query.get_admin_id():
        return await message.answer(
            "Вас приветствует Global Trade Bot! 👋🤖\n\nДобро пожаловать админ!", reply_markup=admin_keyboard
        )

    await message.answer(templates.START_MESSAGE, reply_markup=main_keyboard)


@dp.message(Command("admin"))
async def admin(message: types.Message, state: FSMContext):
    await state.set_state(AdminLoginState.login)
    await message.answer("Введите логин: ")


@dp.message(Command("get_image_id_mozgi_ne_ebi"))
async def get_file_id(message: types.Message):
    file_id = message.video.file_id
    await message.answer(file_id)

async def on_startup(bot: Bot) -> None:
    if SELF_SSL:
        # In case when you have a self-signed SSL certificate, you need to send the certificate
        # itself to Telegram servers for validation purposes
        # (see https://core.telegram.org/bots/self-signed)
        # But if you have a valid SSL certificate, you SHOULD NOT send it to Telegram servers.
        await bot.set_webhook(
            f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}",
            certificate=FSInputFile(WEBHOOK_SSL_CERT),
            secret_token=WEBHOOK_SECRET,
        )
    else:
        await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}", secret_token=WEBHOOK_SECRET)


# === (Added) Register shutdown hook to initialize webhook ===
async def on_shutdown(bot: Bot) -> None:
    """
    Graceful shutdown. This method is recommended by aiohttp docs.
    """
    # Remove webhook.
    await bot.delete_webhook()


def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.include_routers(
        admin_router, menu_handlers.menu_router, state_handlers.state_router
    )

    app = web.Application()

    # Create an instance of request handler,
    # aiogram has few implementations for different cases of usage
    # In this example we use SimpleRequestHandler which is designed to handle simple cases
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    )
    # Register webhook handler on application
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    # Mount dispatcher startup and shutdown hooks to aiohttp application
    setup_application(app, dp, bot=bot)

    if SELF_SSL:  # ==== For self-signed certificate ====
        # Generate SSL context
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)

        # And finally start webserver
        web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT, ssl_context=context)
    else:
        # And finally start webserver
        web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)
    

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
