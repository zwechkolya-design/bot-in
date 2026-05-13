"""
handlers/admin.py — Admin flow: add/edit/delete places (FSM).
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InputMediaPhoto

import db
from keyboards import (
    admin_main_kb, admin_cancel_kb, admin_list_kb, admin_repeat_kb,
    admin_edit_list_kb, admin_edit_fields_kb, admin_back_to_list_kb,
    admin_delete_list_kb, admin_confirm_delete_kb, photos_done_kb, edit_photos_done_kb
)

router = Router()

# ── FSM States ───────────────────────────────────────────────────────────────

class AddPlace(StatesGroup):
    photos      = State()
    name        = State()
    phone       = State()
    description = State()

class EditPlace(StatesGroup):
    photos      = State()
    name        = State()
    phone       = State()
    description = State()

# ── /start ───────────────────────────────────────────────────────────────────

@router.message(Command("start"))
async def admin_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 Sálem, Admin!\nTómendegi menyudan saylań:",
        reply_markup=admin_main_kb(),
    )

# ── Main menu navigation ─────────────────────────────────────────────────────

@router.callback_query(F.data == "admin_back_main")
async def back_to_main(call: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await call.message.delete()
        await call.message.answer(
            "👋 Sálem, Admin!\nTómendegi menyudan saylań:",
            reply_markup=admin_main_kb(),
        )
    except:
        await call.message.edit_text(
            "👋 Sálem, Admin!\nTómendegi menyudan saylań:",
            reply_markup=admin_main_kb(),
        )

@router.callback_query(F.data == "admin_cancel")
async def cancel_step(call: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await call.message.edit_text(
            "❌ Biykar etildi.\nTómendegi menyudan saylań:",
            reply_markup=admin_main_kb(),
        )
    except:
        await call.message.delete()
        await call.message.answer(
            "❌ Biykar etildi.\nTómendegi menyudan saylań:",
            reply_markup=admin_main_kb(),
        )

# ── ADD PLACE ────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "admin_add")
async def start_add(call: CallbackQuery, state: FSMContext):
    await state.set_state(AddPlace.photos)
    await state.update_data(photos=[])
    await call.message.edit_text(
        "📸 Súwret(ler) jiberiń — keminde 1 dana, kóbi menen 10 dana.\n"
        "Hámmesi tayın bolsa ✅ Tayın tuymesin basıń:",
        reply_markup=photos_done_kb(),
    )

@router.message(AddPlace.photos, F.photo)
async def collect_photos(message: Message, state: FSMContext):
    data = await state.get_data()
    photos: list = data.get("photos", [])
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)

    if len(photos) >= 10:
        await state.set_state(AddPlace.name)
        await message.answer(
            "✅ 10 súwret qabıllandı (maksimum)!\n\n📝 Jay atın jiberiń:",
            reply_markup=admin_cancel_kb(),
        )
    else:
        await message.answer(
            f"✅ {len(photos)} dana súwret qabıllandı.\n"
            f"Taǵı súwret jiberiń yamasa ✅ Tayın tuymesin basıń:",
            reply_markup=photos_done_kb(),
        )

@router.callback_query(F.data == "photos_done", AddPlace.photos)
async def photos_done(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data.get("photos"):
        await call.answer("⚠️ Keminde 1 súwret jiberiń!", show_alert=True)
        return
    await state.set_state(AddPlace.name)
    await call.message.edit_text(
        f"✅ {len(data['photos'])} súwret qabıllandı!\n\n📝 Jay atın jiberiń:",
        reply_markup=admin_cancel_kb(),
    )

@router.message(AddPlace.photos)
async def photos_wrong_type(message: Message):
    await message.answer("⚠️ Tek súwret jiberiń.", reply_markup=photos_done_kb())

@router.message(AddPlace.name, F.text)
async def collect_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(AddPlace.phone)
    await message.answer("📞 Telefon nomer(ler)in jiberiń:", reply_markup=admin_cancel_kb())

@router.message(AddPlace.name)
async def name_wrong_type(message: Message):
    await message.answer("⚠️ Tekst jiberiń.", reply_markup=admin_cancel_kb())

@router.message(AddPlace.phone, F.text)
async def collect_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text.strip())
    await state.set_state(AddPlace.description)
    await message.answer("📄 Bul jay haqqında maǵlıwmat kirgiziń:", reply_markup=admin_cancel_kb())

@router.message(AddPlace.phone)
async def phone_wrong_type(message: Message):
    await message.answer("⚠️ Tekst jiberiń.", reply_markup=admin_cancel_kb())

@router.message(AddPlace.description, F.text)
async def collect_description(message: Message, state: FSMContext):
    data = await state.get_data()
    place = db.add_place(
        name=data["name"],
        photos=data["photos"],
        phone=data["phone"],
        description=message.text.strip(),
    )
    await state.clear()
    await message.answer(
        f"✅ <b>{place['name']}</b> tabıslı qosıldı!\n\nTaǵı jay kirgizesiz be?",
        reply_markup=admin_repeat_kb(),
        parse_mode="HTML",
    )

@router.message(AddPlace.description)
async def description_wrong_type(message: Message):
    await message.answer("⚠️ Tekst jiberiń.", reply_markup=admin_cancel_kb())

# ── LIST & VIEW (JAYLARDI KÓRIW) ──────────────────────────────────────────────

@router.callback_query(F.data == "admin_list")
async def list_places(call: CallbackQuery):
    places = db.get_all_places()
    
    try:
        await call.message.delete()
    except:
        pass

    if not places:
        await call.message.answer("📭 Házirshe hesh qanday jay joq.", reply_markup=admin_main_kb())
        return

    text = "📋 <b>Barlıq jaylar:</b>\n\nQaysı jaydı kórmekshisiz?"
    await call.message.answer(text, reply_markup=admin_list_kb(places), parse_mode="HTML")

@router.callback_query(F.data.startswith("admin_view_"))
async def admin_view_place(call: CallbackQuery):
    place_id = int(call.data.split("_")[-1])
    place = db.get_place_by_id(place_id)

    if not place:
        await call.answer("⚠️ Jay tabılmadı!", show_alert=True)
        return

    caption = (
        f"<b>{place['name'].upper()}</b>\n\n"
        f"{place['description']}\n\n"
        f"📞 <b>Telefon:</b> {place['phone']}"
    )
    photos = place["photos"]

    try:
        await call.message.delete()
    except:
        pass

    try:
        if len(photos) == 1:
            await call.message.answer_photo(
                photo=photos[0],
                caption=caption,
                reply_markup=admin_back_to_list_kb(),
                parse_mode="HTML",
            )
        else:
            media_group = []
            for i, file_id in enumerate(photos):
                if i == len(photos) - 1:
                    media_group.append(InputMediaPhoto(media=file_id, caption=caption, parse_mode="HTML"))
                else:
                    media_group.append(InputMediaPhoto(media=file_id))

            await call.message.answer_media_group(media=media_group)
            await call.message.answer(
                "⬇️ Arqaǵa qaytıw ushın tuymeni basıń:",
                reply_markup=admin_back_to_list_kb(),
            )
    except Exception as e:
        await call.message.answer(
            f"⚠️ Súwretlerdi shıǵarıwda qátelik júz berdi.\nIltimas, bul jaydı ózgertiw arqalı jańa súwret jiberiń.",
            reply_markup=admin_back_to_list_kb()
        )

# ── DELETE (JAYLARDI TASTIYQLAP ÓSHIRIW) ─────────────────────────────────────

@router.callback_query(F.data == "admin_delete_list")
async def delete_list(call: CallbackQuery, state: FSMContext):
    await state.clear()
    places = db.get_all_places()
    
    try:
        await call.message.delete()
    except:
        pass

    if not places:
        await call.message.answer("📭 Óshiriw ushın jay joq.", reply_markup=admin_main_kb())
        return
    await call.message.answer(
        "🗑 <b>Qaysı jaydı óshirmekshisiz?</b>\nTómendegi dizimnen saylań:",
        reply_markup=admin_delete_list_kb(places),
        parse_mode="HTML",
    )

@router.callback_query(F.data.startswith("del_req_"))
async def ask_delete_confirmation(call: CallbackQuery):
    place_id = int(call.data.split("_")[-1])
    place = db.get_place_by_id(place_id)
    if not place:
        await call.answer("⚠️ Jay tabılmadı!", show_alert=True)
        return
    
    text = f"❗️ <b>{place['name']}</b> jayın haqıyqattan da óshirmekshisiz be?\n<i>Bul háreketti arqaǵa qaytarıp bolmaydı!</i>"
    try:
        await call.message.edit_text(text, reply_markup=admin_confirm_delete_kb(place_id), parse_mode="HTML")
    except:
        await call.message.delete()
        await call.message.answer(text, reply_markup=admin_confirm_delete_kb(place_id), parse_mode="HTML")

@router.callback_query(F.data.startswith("del_confirm_"))
async def confirm_delete_place(call: CallbackQuery):
    place_id = int(call.data.split("_")[-1])
    success = db.delete_place(place_id)
    await call.answer("✅ Tabıslı óshirildi!" if success else "⚠️ Jay tabılmadı yamasa aldın óshirilgen.", show_alert=True)

    places = db.get_all_places()
    if not places:
        try:
            await call.message.edit_text("📭 Barsha jaylar óshirildi.", reply_markup=admin_main_kb())
        except:
            await call.message.answer("📭 Barsha jaylar óshirildi.", reply_markup=admin_main_kb())
    else:
        try:
            await call.message.edit_text(
                "🗑 <b>Taǵı qaysı jaydı óshirmekshisiz?</b>",
                reply_markup=admin_delete_list_kb(places),
                parse_mode="HTML",
            )
        except:
            await call.message.answer(
                "🗑 <b>Taǵı qaysı jaydı óshirmekshisiz?</b>",
                reply_markup=admin_delete_list_kb(places),
                parse_mode="HTML",
            )

# ── EDIT — select place & field ──────────────────────────────────────────────

@router.callback_query(F.data == "admin_edit_list")
async def edit_list(call: CallbackQuery, state: FSMContext):
    await state.clear()
    places = db.get_all_places()
    
    try:
        await call.message.delete()
    except:
        pass

    if not places:
        await call.message.answer("📭 Ózgertiw ushın jay joq.", reply_markup=admin_main_kb())
        return
    await call.message.answer(
        "✏️ <b>Qaysı jaydı ózgertpekshisiz?</b>",
        reply_markup=admin_edit_list_kb(places),
        parse_mode="HTML",
    )

@router.callback_query(F.data.startswith("admin_edit_select_"))
async def edit_select_place(call: CallbackQuery):
    place_id = int(call.data.split("_")[-1])
    place = db.get_place_by_id(place_id)
    if not place:
        await call.answer("⚠️ Jay tabılmadı!", show_alert=True)
        return
    await call.message.edit_text(
        f"✏️ <b>{place['name']}</b> — qaysı bólimin ózgertpekshisiz?",
        reply_markup=admin_edit_fields_kb(place_id),
        parse_mode="HTML",
    )

# ── EDIT — photos (1–10) ─────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin_editfield_photos_"))
async def edit_photos_start(call: CallbackQuery, state: FSMContext):
    place_id = int(call.data.split("_")[-1])
    await state.set_state(EditPlace.photos)
    await state.update_data(edit_id=place_id, photos=[])
    await call.message.edit_text(
        "📸 Jańa súwret(ler) jiberiń — keminde 1 dana, kóbi menen 10 dana.\n"
        "Tayın bolǵan soń ✅ Tayın tuymesin basıń:",
        reply_markup=edit_photos_done_kb(),
    )

@router.message(EditPlace.photos, F.photo)
async def edit_collect_photos(message: Message, state: FSMContext):
    data = await state.get_data()
    photos: list = data.get("photos", [])
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)

    if len(photos) >= 10:
        place = db.update_place(data["edit_id"], photos=photos)
        await state.clear()
        await message.answer(
            f"✅ <b>{place['name']}</b> súwretleri jańalandı! (10 dana maksimum)",
            reply_markup=admin_main_kb(),
            parse_mode="HTML",
        )
    else:
        await message.answer(
            f"✅ {len(photos)} dana súwret qabıllandı.\n"
            f"Taǵı súwret jiberiń yamasa ✅ Tayın tuymesin basıń:",
            reply_markup=edit_photos_done_kb(),
        )

@router.callback_query(F.data == "edit_photos_done", EditPlace.photos)
async def edit_photos_done(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data.get("photos"):
        await call.answer("⚠️ Keminde 1 súwret jiberiń!", show_alert=True)
        return
    place = db.update_place(data["edit_id"], photos=data["photos"])
    await state.clear()
    await call.message.edit_text(
        f"✅ <b>{place['name']}</b> súwretleri jańalandı!",
        reply_markup=admin_main_kb(),
        parse_mode="HTML",
    )

@router.message(EditPlace.photos)
async def edit_photos_wrong(message: Message):
    await message.answer("⚠️ Tek súwret jiberiń.", reply_markup=edit_photos_done_kb())

# ── EDIT — name ──────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin_editfield_name_"))
async def edit_name_start(call: CallbackQuery, state: FSMContext):
    place_id = int(call.data.split("_")[-1])
    await state.set_state(EditPlace.name)
    await state.update_data(edit_id=place_id)
    await call.message.edit_text("📝 Jańa jay atın jiberiń:", reply_markup=admin_cancel_kb())

@router.message(EditPlace.name, F.text)
async def edit_collect_name(message: Message, state: FSMContext):
    data = await state.get_data()
    place = db.update_place(data["edit_id"], name=message.text.strip())
    await state.clear()
    await message.answer(
        f"✅ Jay atı <b>{place['name']}</b> etip jańalandı!",
        reply_markup=admin_main_kb(),
        parse_mode="HTML",
    )

@router.message(EditPlace.name)
async def edit_name_wrong(message: Message):
    await message.answer("⚠️ Tekst jiberiń.", reply_markup=admin_cancel_kb())

# ── EDIT — phone ─────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin_editfield_phone_"))
async def edit_phone_start(call: CallbackQuery, state: FSMContext):
    place_id = int(call.data.split("_")[-1])
    await state.set_state(EditPlace.phone)
    await state.update_data(edit_id=place_id)
    await call.message.edit_text("📞 Jańa telefon nomerin jiberiń:", reply_markup=admin_cancel_kb())

@router.message(EditPlace.phone, F.text)
async def edit_collect_phone(message: Message, state: FSMContext):
    data = await state.get_data()
    place = db.update_place(data["edit_id"], phone=message.text.strip())
    await state.clear()
    await message.answer(
        f"✅ <b>{place['name']}</b> telefon nomeri jańalandı!",
        reply_markup=admin_main_kb(),
        parse_mode="HTML",
    )

@router.message(EditPlace.phone)
async def edit_phone_wrong(message: Message):
    await message.answer("⚠️ Tekst jiberiń.", reply_markup=admin_cancel_kb())

# ── EDIT — description ───────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("admin_editfield_description_"))
async def edit_desc_start(call: CallbackQuery, state: FSMContext):
    place_id = int(call.data.split("_")[-1])
    await state.set_state(EditPlace.description)
    await state.update_data(edit_id=place_id)
    await call.message.edit_text("📄 Jańa maǵlıwmat jiberiń:", reply_markup=admin_cancel_kb())

@router.message(EditPlace.description, F.text)
async def edit_collect_desc(message: Message, state: FSMContext):
    data = await state.get_data()
    place = db.update_place(data["edit_id"], description=message.text.strip())
    await state.clear()
    await message.answer(
        f"✅ <b>{place['name']}</b> maǵlıwmatı jańalandı!",
        reply_markup=admin_main_kb(),
        parse_mode="HTML",
    )

@router.message(EditPlace.description)
async def edit_desc_wrong(message: Message):
    await message.answer("⚠️ Tekst jiberiń.", reply_markup=admin_cancel_kb())