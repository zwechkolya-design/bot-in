"""
handlers/user.py — User flow: browse places, view details.
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InputMediaPhoto

import db
from keyboards import user_places_kb

router = Router()


async def _send_places_menu(target, places: list[dict]):
    """Send or edit the main places inline menu."""
    text = "🏙 <b>Nókis qalasındaǵı jaylar:</b>\nTómendegi jaylardan birin saylań:"
    kb = user_places_kb(places)

    if isinstance(target, CallbackQuery):
        await target.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    else:
        await target.answer(text, reply_markup=kb, parse_mode="HTML")


# ── /start ───────────────────────────────────────────────────────────────────

@router.message(Command("start"))
async def user_start(message: Message):
    places = db.get_all_places()
    if not places:
        await message.answer(
            "🏙 <b>Nókis qalasındaǵı jaylar</b>\n\n"
            "⏳ Házirshe maǵlıwmatlar joq. Tez arada qosıladı!",
            parse_mode="HTML",
        )
        return
    await _send_places_menu(message, places)


# ── View a specific place ────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("view_"))
async def view_place(call: CallbackQuery):
    place_id = int(call.data.split("_")[-1])
    place = next((p for p in db.get_all_places() if p["id"] == place_id), None)

    if not place:
        await call.answer("⚠️ Jay tabılmadı!", show_alert=True)
        return

    # Build caption: NAME in caps + description + phone
    caption = (
        f"<b>{place['name'].upper()}</b>\n\n"
        f"{place['description']}\n\n"
        f"📞 <b>Telefon:</b> {place['phone']}"
    )

    photos = place["photos"]

    if len(photos) == 1:
        # Single photo — send as photo with caption
        await call.message.delete()
        await call.message.answer_photo(
            photo=photos[0],
            caption=caption,
            reply_markup=user_places_kb(db.get_all_places()),
            parse_mode="HTML",
        )
    else:
        # Media group (2-3 photos): caption on last photo
        media_group = []
        for i, file_id in enumerate(photos):
            if i == len(photos) - 1:
                media_group.append(
                    InputMediaPhoto(media=file_id, caption=caption, parse_mode="HTML")
                )
            else:
                media_group.append(InputMediaPhoto(media=file_id))

        await call.message.delete()
        await call.message.answer_media_group(media=media_group)
        # Send back button separately (media groups don't support reply_markup)
        await call.message.answer(
            "⬇Basqa jerdi saylan:",
            reply_markup=user_places_kb(db.get_all_places()),
        )


# ── Back to main list ────────────────────────────────────────────────────────

@router.callback_query(F.data == "user_back")
async def user_back(call: CallbackQuery):
    places = db.get_all_places()
    if not places:
        await call.message.edit_text(
            "⏳ Házirshe maǵlıwmatlar joq.",
        )
        return
    await _send_places_menu(call, places)
