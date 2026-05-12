"""
keyboards.py — Barlıq inline klaviaturalar (tuymeler) jıynaǵı.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


# ──────────────────────────────────────────────
# Admin keyboards
# ──────────────────────────────────────────────

def admin_main_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="➕ Jay qosıw", callback_data="admin_add"),
        InlineKeyboardButton(text="📋 Jaylardı kóriw", callback_data="admin_list"),
    )
    builder.row(
        InlineKeyboardButton(text="✏️ Jaylardı ózgertiw", callback_data="admin_edit_list"),
        InlineKeyboardButton(text="🗑 Jaylardı óshiriw", callback_data="admin_delete_list"),
    )
    return builder.as_markup()


def admin_cancel_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔙 Arqaǵa", callback_data="admin_cancel")
    )
    return builder.as_markup()


def photos_done_kb() -> InlineKeyboardMarkup:
    """Súwretler jıynalip atırǵanda kórsetiledi: tawsıw yamasa biykar etiw."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Tayın", callback_data="photos_done"),
        InlineKeyboardButton(text="🔙 Arqaǵa", callback_data="admin_cancel"),
    )
    return builder.as_markup()


def edit_photos_done_kb() -> InlineKeyboardMarkup:
    """Ózgertiw processindegi photos_done_kb dıń aynan ózi."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Tayın", callback_data="edit_photos_done"),
        InlineKeyboardButton(text="🔙 Arqaǵa", callback_data="admin_cancel"),
    )
    return builder.as_markup()


def admin_list_kb(places: list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for place in places:
        builder.row(
            InlineKeyboardButton(
                text=f"🗑 {place['name']} (Óshiriw)",
                callback_data=f"admin_delete_{place['id']}",
            )
        )
    builder.row(
        InlineKeyboardButton(text="🔙 Arqaǵa", callback_data="admin_back_main")
    )
    return builder.as_markup()


def admin_repeat_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="➕ Taǵı jay qosıw", callback_data="admin_add"),
        InlineKeyboardButton(text="🔙 Arqaǵa", callback_data="admin_back_main"),
    )
    return builder.as_markup()


def admin_edit_list_kb(places: list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for place in places:
        builder.row(
            InlineKeyboardButton(
                text=f"✏️ {place['name']}",
                callback_data=f"admin_edit_select_{place['id']}",
            )
        )
    builder.row(
        InlineKeyboardButton(text="🔙 Arqaǵa", callback_data="admin_back_main")
    )
    return builder.as_markup()


def admin_edit_fields_kb(place_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📸 Súwretler", callback_data=f"admin_editfield_photos_{place_id}"),
        InlineKeyboardButton(text="📝 Atı",     callback_data=f"admin_editfield_name_{place_id}"),
    )
    builder.row(
        InlineKeyboardButton(text="📞 Telefon",  callback_data=f"admin_editfield_phone_{place_id}"),
        InlineKeyboardButton(text="📄 Maǵlıwmat", callback_data=f"admin_editfield_description_{place_id}"),
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Arqaǵa", callback_data="admin_edit_list")
    )
    return builder.as_markup()


def admin_delete_list_kb(places: list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for place in places:
        builder.row(
            InlineKeyboardButton(
                text=f"🗑 {place['name']}",
                callback_data=f"admin_delete_{place['id']}",
            )
        )
    builder.row(
        InlineKeyboardButton(text="🔙 Arqaǵa", callback_data="admin_back_main")
    )
    return builder.as_markup()


# ──────────────────────────────────────────────
# User keyboards
# ──────────────────────────────────────────────

def user_places_kb(places: list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for place in places:
        builder.row(
            InlineKeyboardButton(
                text=place["name"],
                callback_data=f"view_{place['id']}",
            )
        )
    return builder.as_markup()

def user_back_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔙 Arqaǵa", callback_data="user_back")
    )
    return builder.as_markup()