"""
main.py — Bot iske túsiriw noqatı hám admin/paydalanıwshı marshrutların (router) ajıratıw.
"""
import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from dotenv import load_dotenv

from handlers import admin as admin_handlers
from handlers import user as user_handlers

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
admin_id_str = os.getenv("ADMIN_ID", "")
ADMIN_IDS: list = [int(id.strip()) for id in admin_id_str.split(",") if id.strip().isdigit()]

if not BOT_TOKEN:
    raise ValueError(".env faylında BOT_TOKEN ornatılmaǵan")
if not ADMIN_IDS:
    raise ValueError(".env faylında ADMIN_ID ornatılmaǵan")


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ── Middleware: admin hám paydalanıwshı marshrutizaciyası ────────────────────

from aiogram import BaseMiddleware
from typing import Any, Awaitable, Callable
from aiogram.types import TelegramObject, Update


class RouterMiddleware(BaseMiddleware):
    """
    'is_admin' bayraǵın handler maǵlıwmatlarına qosadı.
    Admin router is_admin filtri arqalı bólek dizimnen ótkeriledi.
    """
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        # in ADMIN_IDS dep ózgertildi:
        data["is_admin"] = bool(user and user.id in ADMIN_IDS)
        return await handler(event, data)


# ── Admin filtri ─────────────────────────────────────────────────────────────

from aiogram.filters import Filter

class IsAdmin(Filter):
    async def __call__(self, message: Message, is_admin: bool = False) -> bool:
        return is_admin


# ── Dispatcher jaratıw ───────────────────────────────────────────────────────

def build_dispatcher() -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())
    dp.update.middleware(RouterMiddleware())

    # Admin router — tek ADMIN_ID den kelgen xabarlardı qayta isleydi
    admin_router = admin_handlers.router
    admin_router.message.filter(IsAdmin())
    admin_router.callback_query.filter(IsAdmin())

    # User router — basqa barlıq paydalanıwshılar ushın (admin emesler)
    user_router = user_handlers.router

    dp.include_router(admin_router)
    dp.include_router(user_router)

    return dp


# ── Tiykarǵı bólim ───────────────────────────────────────────────────────────

async def main() -> None:
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = build_dispatcher()

    logger.info("Bot iske túsirildi...")
    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    asyncio.run(main())