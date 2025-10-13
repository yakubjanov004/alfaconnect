from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputMediaDocument
from aiogram.fsm.context import FSMContext
from datetime import datetime
import html
from database.admin.orders import (
    get_connection_orders,
    get_technician_orders,
    get_staff_orders
)
from database.basic.user import get_user_by_telegram_id
from filters.role_filter import RoleFilter
from keyboards.admin_buttons import get_applications_main_menu, get_admin_main_menu
from database.basic.language import get_user_language

router = Router()

router.message.filter(RoleFilter("admin")) 

def fmt_dt(dt: datetime) -> str:
    return dt.strftime("%d.%m.%Y %H:%M")

def esc(v) -> str:
    if v is None:
        return "-"
    return html.escape(str(v), quote=False)

def connection_status_names(lang: str) -> dict:
    if lang == "ru":
        return {
            "new": "🆕 Новая",
            "in_manager": "👨‍💼 У менеджера",
            "in_junior_manager": "👨‍💼 У джуниор-менеджера",
            "in_controller": "🎛️ У контроллера",
            "in_technician": "🔧 У техника",
            "in_diagnostics": "🔍 На диагностике",
            "in_repairs": "🛠️ В ремонте",
            "in_warehouse": "📦 На складе",
            "in_technician_work": "⚙️ В работе у техника",
            "completed": "✅ Завершена",
        }
    return {
        "new": "🆕 Yangi",
        "in_manager": "👨‍💼 Menejerda",
        "in_junior_manager": "👨‍💼 Junior menejerda",
        "in_controller": "🎛️ Controllerda",
        "in_technician": "🔧 Texnikda",
        "in_diagnostics": "🔍 Diagnostikada",
        "in_repairs": "🛠️ Ta'mirda",
        "in_warehouse": "📦 Omborда",
        "in_technician_work": "⚙️ Texnik ishda",
        "completed": "✅ Tugallangan",
    }


def technician_status_names(lang: str) -> dict:
    if lang == "ru":
        return {
            "new": "🆕 Новая",
            "in_controller": "🎛️ У контроллера",
            "in_technician": "🔧 У техника",
            "in_diagnostics": "🔍 На диагностике",
            "in_repairs": "🛠️ В ремонте",
            "in_warehouse": "📦 На складе",
            "in_technician_work": "⚙️ В работе у техника",
            "completed": "✅ Завершена",
        }
    return {
        "new": "🆕 Yangi",
        "in_controller": "🎛️ Controllerda",
        "in_technician": "🔧 Texnikda",
        "in_diagnostics": "🔍 Diagnostikada",
        "in_repairs": "🛠️ Ta'mirda",
        "in_warehouse": "📦 Omborда",
        "in_technician_work": "⚙️ Texnik ishda",
        "completed": "✅ Tugallangan",
    }

def connection_order_text(item: dict, lang: str) -> str:
    order_id = item.get('application_number') or item['id']
    created = item["created_at"]
    created_dt = datetime.fromisoformat(created) if isinstance(created, str) else created
    
    # Escape ALL dynamic fields - use correct field names from database
    full_name = esc(item.get('client_name', '-'))  # Use client_name from JOIN
    phone = esc(item.get('client_phone', '-'))     # Use client_phone from JOIN
    username = esc(item.get('username', ''))
    address = esc(item.get('address', '-'))
    region = esc(item.get('region', '-'))
    tarif_name = esc(item.get('tariff_name', '-'))  # Use correct field name from database
    status_map = connection_status_names(lang)
    status = status_map.get(item.get('status', 'in_manager'), item.get('status', 'in_manager'))
    notes = esc(item.get('notes', '-'))  # This field doesn't exist in connection_orders
    jm_notes = esc(item.get('jm_notes', '-'))
    rating = item.get('rating', 0) or 0  # This field doesn't exist in connection_orders
    
    username_text = f"\n👤 Username: @{username}" if username else ""
    location_text = ""
    if item.get('latitude') and item.get('longitude'):
        lat = item['latitude']
        lon = item['longitude']
        location_text = f"\n📍 GPS: https://maps.google.com/?q={lat},{lon}"
    
    rating_text = "⭐" * rating if rating > 0 else ("Baholanmagan" if lang == "uz" else "Без оценки")
    
    if lang == "ru":
        return (
            "🔌 <b>ЗАЯВКА НА ПОДКЛЮЧЕНИЕ</b>\n\n"
            f"📋 <b>Заказ:</b> #{esc(order_id)}\n"
            f"🏷️ <b>Статус:</b> {status}\n"
            f"👤 <b>Клиент:</b> {full_name}\n"
            f"📞 <b>Телефон:</b> {phone}{username_text}\n"
            f"🌍 <b>Регион:</b> {region}\n"
            f"📍 <b>Адрес:</b> {address}{location_text}\n"
            f"📦 <b>Тариф:</b> {tarif_name}\n"
            f"⭐ <b>Оценка:</b> {rating_text}\n"
            f"📝 <b>Заметки:</b> {notes}\n"
            f"📝 <b>Заметки JM:</b> {jm_notes}\n"
            f"📅 <b>Дата:</b> {fmt_dt(created_dt)}"
        )
    return (
        "🔌 <b>ULANISH ZAYAVKASI</b>\n\n"
        f"📋 <b>Buyurtma:</b> #{esc(order_id)}\n"
        f"🏷️ <b>Status:</b> {status}\n"
        f"👤 <b>Mijoz:</b> {full_name}\n"
        f"📞 <b>Telefon:</b> {phone}{username_text}\n"
        f"🌍 <b>Hudud:</b> {region}\n"
        f"📍 <b>Manzil:</b> {address}{location_text}\n"
        f"📦 <b>Tarif:</b> {tarif_name}\n"
        f"⭐ <b>Baho:</b> {rating_text}\n"
        f"📝 <b>Izohlar:</b> {notes}\n"
        f"📝 <b>JM Izohlar:</b> {jm_notes}\n"
        f"📅 <b>Sana:</b> {fmt_dt(created_dt)}"
    )

def technician_order_text(item: dict, lang: str) -> str:
    order_id = item.get('application_number') or item['id']
    created = item["created_at"]
    created_dt = datetime.fromisoformat(created) if isinstance(created, str) else created
    
    full_name = esc(item.get('client_name', '-'))  # Use client_name from JOIN
    phone = esc(item.get('client_phone', item.get('phone', '-')))  # Try both phone fields
    username = esc(item.get('username', ''))
    address = esc(item.get('address', '-'))
    region = esc(item.get('region', '-'))
    abonent_id = esc(item.get('abonent_id', '-'))
    description = esc(item.get('description', '-'))
    status_map = technician_status_names(lang)
    status = status_map.get(item.get('status', 'in_technician'), item.get('status', 'in_technician'))
    notes = esc(item.get('notes', '-'))
    rating = item.get('rating', 0) or 0
    
    username_text = f"\n👤 Username: @{username}" if username else ""
    location_text = ""
    if item.get('latitude') and item.get('longitude'):
        lat = item['latitude']
        lon = item['longitude']
        location_text = f"\n📍 GPS: https://maps.google.com/?q={lat},{lon}"
    
    rating_text = "⭐" * rating if rating > 0 else ("Baholanmagan" if lang == "uz" else "Без оценки")
    
    if lang == "ru":
        return (
            "🔧 <b>ТЕХНИЧЕСКАЯ ЗАЯВКА</b>\n\n"
            f"📋 <b>Заказ:</b> #{esc(order_id)}\n"
            f"🏷️ <b>Статус:</b> {status}\n"
            f"👤 <b>Клиент:</b> {full_name}\n"
            f"📞 <b>Телефон:</b> {phone}{username_text}\n"
            f"🆔 <b>Абонент ID:</b> {abonent_id}\n"
            f"🌍 <b>Регион:</b> {region}\n"
            f"📍 <b>Адрес:</b> {address}{location_text}\n"
            f"📝 <b>Описание:</b> {description}\n"
            f"⭐ <b>Оценка:</b> {rating_text}\n"
            f"📝 <b>Заметки:</b> {notes}\n"
            f"📅 <b>Дата:</b> {fmt_dt(created_dt)}"
        )
    return (
        "🔧 <b>TEXNIK ZAYAVKA</b>\n\n"
        f"📋 <b>Buyurtma:</b> #{esc(order_id)}\n"
        f"🏷️ <b>Status:</b> {status}\n"
        f"👤 <b>Mijoz:</b> {full_name}\n"
        f"📞 <b>Telefon:</b> {phone}{username_text}\n"
        f"🆔 <b>Abonent ID:</b> {abonent_id}\n"
        f"🌍 <b>Hudud:</b> {region}\n"
        f"📍 <b>Manzil:</b> {address}{location_text}\n"
        f"📝 <b>Tavsif:</b> {description}\n"
        f"⭐ <b>Baho:</b> {rating_text}\n"
        f"📝 <b>Izohlar:</b> {notes}\n"
        f"📅 <b>Sana:</b> {fmt_dt(created_dt)}"
    )

def staff_order_text(item: dict, lang: str) -> str:
    order_id = item.get('application_number') or item['id']
    created = item["created_at"]
    created_dt = datetime.fromisoformat(created) if isinstance(created, str) else created
    
    # Escape ALL dynamic fields - use correct field names from database
    full_name = esc(item.get('client_name', '-'))  # Use client_name from JOIN
    phone = esc(item.get('client_phone', item.get('phone', '-')))  # Try both phone fields
    username = esc(item.get('username', ''))
    address = esc(item.get('address', '-'))
    region = esc(item.get('region', '-'))
    abonent_id = esc(item.get('abonent_id', '-'))
    description = esc(item.get('description', '-'))
    status_map = connection_status_names(lang)
    status = status_map.get(item.get('status', 'in_call_center_supervisor'), item.get('status', 'in_call_center_supervisor'))
    tarif_name = esc(item.get('tariff_name', '-'))  # Use correct field name from database
    type_of_zayavka = esc(item.get('type_of_zayavka', '-'))
    problem_description = esc(item.get('problem_description', '-'))
    
    username_text = f"\n👤 Username: @{username}" if username else ""
    
    # Determine what to show based on order type
    if type_of_zayavka.lower() == 'connection':
        # For connection orders, show tariff
        tariff_or_problem_label = "📦 <b>Tarif:</b>" if lang == "uz" else "📦 <b>Тариф:</b>"
        tariff_or_problem_value = tarif_name
    else:
        # For technician orders, show problem description
        tariff_or_problem_label = "🔧 <b>Muammo:</b>" if lang == "uz" else "🔧 <b>Проблема:</b>"
        tariff_or_problem_value = problem_description if problem_description != '-' else description
    
    if lang == "ru":
        return (
            "👥 <b>ЗАЯВКА СОТРУДНИКА</b>\n\n"
            f"📋 <b>Заказ:</b> #{esc(order_id)}\n"
            f"🏷️ <b>Статус:</b> {status}\n"
            f"🔧 <b>Тип:</b> {type_of_zayavka}\n"
            f"👤 <b>Клиент:</b> {full_name}\n"
            f"📞 <b>Телефон:</b> {phone}{username_text}\n"
            f"🆔 <b>Абонент ID:</b> {abonent_id}\n"
            f"🌍 <b>Регион:</b> {region}\n"
            f"📍 <b>Адрес:</b> {address}\n"
            f"{tariff_or_problem_label} {tariff_or_problem_value}\n"
            f"📝 <b>Описание:</b> {description}\n"
            f"📅 <b>Дата:</b> {fmt_dt(created_dt)}"
        )
    return (
        "👥 <b>XODIM ZAYAVKASI</b>\n\n"
        f"📋 <b>Buyurtma:</b> #{esc(order_id)}\n"
        f"🏷️ <b>Status:</b> {status}\n"
        f"🔧 <b>Tur:</b> {type_of_zayavka}\n"
        f"👤 <b>Mijoz:</b> {full_name}\n"
        f"📞 <b>Telefon:</b> {phone}{username_text}\n"
        f"🆔 <b>Abonent ID:</b> {abonent_id}\n"
        f"🌍 <b>Hudud:</b> {region}\n"
        f"📍 <b>Manzil:</b> {address}\n"
        f"{tariff_or_problem_label} {tariff_or_problem_value}\n"
        f"📝 <b>Tavsif:</b> {description}\n"
        f"📅 <b>Sana:</b> {fmt_dt(created_dt)}"
    )

def nav_keyboard(index: int, total: int, order_type: str, lang: str) -> InlineKeyboardMarkup:
    rows = []
    nav_row = []
    
    if index > 0:
        nav_row.append(InlineKeyboardButton(text=("⬅️ Oldingi" if lang == "uz" else "⬅️ Предыдущая"), callback_data=f"{order_type}_prev_{index}"))
    
    if index < total - 1:
        nav_row.append(InlineKeyboardButton(text=("Keyingi ➡️" if lang == "uz" else "Следующая ➡️"), callback_data=f"{order_type}_next_{index}"))
    
    if nav_row:
        rows.append(nav_row)
    
    # Yopish tugmasi
    rows.append([InlineKeyboardButton(text=("❌ Yopish" if lang == "uz" else "❌ Закрыть"), callback_data="orders_back")])
    
    return InlineKeyboardMarkup(inline_keyboard=rows)

# Asosiy zayavkalar menyusi
@router.message(F.text.in_(["📝 Zayavkalar", "📝 Заявки"]))
async def open_orders_menu(message: Message, state: FSMContext):
    user = await get_user_by_telegram_id(message.from_user.id)
    if not user or user.get("role") != "admin":
        return
    lang = await get_user_language(message.from_user.id) or "uz"
    
    await message.answer(
        ("📝 <b>Zayavkalar bo'limi</b>\n\nQuyidagi tugmalardan birini tanlang:" if lang == "uz" else "📝 <b>Раздел заявок</b>\n\nВыберите одну из кнопок:"),
        parse_mode='HTML',
        reply_markup=get_applications_main_menu(lang)
    )

# Ulanish zayavkalari
@router.message(F.text.in_(["🔌 Ulanish zayavkalari", "🔌 Заявки на подключение"]))
async def open_connection_orders(message: Message, state: FSMContext):
    user = await get_user_by_telegram_id(message.from_user.id)
    if not user or user.get("role") != "admin":
        return
    lang = await get_user_language(message.from_user.id) or "uz"
    
    items = await get_connection_orders(limit=50, offset=0)
    if not items:
        await message.answer(
            ("🔌 <b>Ulanish Zayavkalari</b>\n\nHozircha zayavkalar yo'q." if lang == "uz" else "🔌 <b>Заявки на подключение</b>\n\nПока нет заявок."),
            parse_mode='HTML',
            reply_markup=get_applications_main_menu(lang)
        )
        return
    
    await state.update_data(connection_orders=items, idx=0)
    text = connection_order_text(items[0], lang)
    kb = nav_keyboard(0, len(items), "connection", lang)
    await send_connection_order_with_media(message, items[0], lang, kb)

# Texnik zayavkalar
@router.message(F.text.in_(["🔧 Texnik zayavkalar", "🔧 Технические заявки"]))
async def open_technician_orders(message: Message, state: FSMContext):
    user = await get_user_by_telegram_id(message.from_user.id)
    if not user or user.get("role") != "admin":
        return
    lang = await get_user_language(message.from_user.id) or "uz"
    
    items = await get_technician_orders(limit=50, offset=0)
    if not items:
        await message.answer(
            ("🔧 <b>Texnik Zayavkalar</b>\n\nHozircha zayavkalar yo'q." if lang == "uz" else "🔧 <b>Технические заявки</b>\n\nПока нет заявок."),
            parse_mode='HTML',
            reply_markup=get_applications_main_menu(lang)
        )
        return
    
    await state.update_data(technician_orders=items, idx=0)
    kb = nav_keyboard(0, len(items), "technician", lang)
    await send_technician_order_with_media(message, items[0], lang, kb)

# Xodim zayavkalari
@router.message(F.text.in_(["👥 Xodim zayavkalari", "👥 Заявки сотрудников"]))
async def open_staff_orders(message: Message, state: FSMContext):
    user = await get_user_by_telegram_id(message.from_user.id)
    if not user or user.get("role") != "admin":
        return
    lang = await get_user_language(message.from_user.id) or "uz"
    
    items = await get_staff_orders(limit=50, offset=0)
    if not items:
        await message.answer(
            ("👥 <b>Xodim Zayavkalari</b>\n\nHozircha zayavkalar yo'q." if lang == "uz" else "👥 <b>Заявки сотрудников</b>\n\nПока нет заявок."),
            parse_mode='HTML',
            reply_markup=get_applications_main_menu(lang)
        )
        return
    
    await state.update_data(staff_orders=items, idx=0)
    text = staff_order_text(items[0], lang)
    kb = nav_keyboard(0, len(items), "staff", lang)
    await message.answer(text, reply_markup=kb, parse_mode="HTML")

# Navigation callbacks
@router.callback_query(F.data.startswith("connection_prev_"))
async def prev_connection_order(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    lang = await get_user_language(cb.from_user.id) or "uz"
    data = await state.get_data()
    items = data.get("connection_orders", [])
    idx = int(cb.data.replace("connection_prev_", "")) - 1
    if idx < 0 or idx >= len(items):
        return
    await state.update_data(idx=idx)
    text = connection_order_text(items[idx], lang)
    kb = nav_keyboard(idx, len(items), "connection", lang)
    await send_connection_order_with_media_edit(cb, items[idx], lang, kb)

@router.callback_query(F.data.startswith("connection_next_"))
async def next_connection_order(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    lang = await get_user_language(cb.from_user.id) or "uz"
    data = await state.get_data()
    items = data.get("connection_orders", [])
    idx = int(cb.data.replace("connection_next_", "")) + 1
    if idx < 0 or idx >= len(items):
        return
    await state.update_data(idx=idx)
    text = connection_order_text(items[idx], lang)
    kb = nav_keyboard(idx, len(items), "connection", lang)
    await send_connection_order_with_media_edit(cb, items[idx], lang, kb)

@router.callback_query(F.data.startswith("technician_prev_"))
async def prev_technician_order(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    lang = await get_user_language(cb.from_user.id) or "uz"
    data = await state.get_data()
    items = data.get("technician_orders", [])
    idx = int(cb.data.replace("technician_prev_", "")) - 1
    if idx < 0 or idx >= len(items):
        return
    await state.update_data(idx=idx)
    kb = nav_keyboard(idx, len(items), "technician", lang)
    await send_technician_order_with_media_edit(cb, items[idx], lang, kb)

@router.callback_query(F.data.startswith("technician_next_"))
async def next_technician_order(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    lang = await get_user_language(cb.from_user.id) or "uz"
    data = await state.get_data()
    items = data.get("technician_orders", [])
    idx = int(cb.data.replace("technician_next_", "")) + 1
    if idx < 0 or idx >= len(items):
        return
    await state.update_data(idx=idx)
    kb = nav_keyboard(idx, len(items), "technician", lang)
    await send_technician_order_with_media_edit(cb, items[idx], lang, kb)

@router.callback_query(F.data.startswith("staff_prev_"))
async def prev_staff_order(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    lang = await get_user_language(cb.from_user.id) or "uz"
    data = await state.get_data()
    items = data.get("staff_orders", [])
    idx = int(cb.data.replace("staff_prev_", "")) - 1
    if idx < 0 or idx >= len(items):
        return
    await state.update_data(idx=idx)
    text = staff_order_text(items[idx], lang)
    kb = nav_keyboard(idx, len(items), "staff", lang)
    await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

@router.callback_query(F.data.startswith("staff_next_"))
async def next_staff_order(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    lang = await get_user_language(cb.from_user.id) or "uz"
    data = await state.get_data()
    items = data.get("staff_orders", [])
    idx = int(cb.data.replace("staff_next_", "")) + 1
    if idx < 0 or idx >= len(items):
        return
    await state.update_data(idx=idx)
    text = staff_order_text(items[idx], lang)
    kb = nav_keyboard(idx, len(items), "staff", lang)
    await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")

# Orqaga qaytish
@router.callback_query(F.data == "orders_back")
async def back_to_orders_menu(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    await state.clear()
    try:
        await cb.message.delete()
    except Exception:
        pass


# Orqaga (asosiy menyuga)
@router.message(F.text.in_(["◀️ Orqaga", "◀️ Назад"]))
async def back_to_main_menu(message: Message, state: FSMContext):
    user = await get_user_by_telegram_id(message.from_user.id)
    if not user or user.get("role") != "admin":
        return
    
    await state.clear()
    lang = await get_user_language(message.from_user.id) or "uz"
    await message.answer(
        ("🏠 <b>Admin Panel</b>\n\nAsosiy menyuga qaytdingiz." if lang == "uz" else "🏠 <b>Панель администратора</b>\n\nВы вернулись в главное меню."),
        parse_mode='HTML',
        reply_markup=get_admin_main_menu(lang)
    )

async def send_technician_order_with_media(message: Message, item: dict, lang: str, keyboard):
    """Send technician order with media if available"""
    text = technician_order_text(item, lang)
    media_file = item.get('media')
    
    if media_file and media_file.strip():
        try:
            # Try to send as photo first
            await message.answer_photo(
                photo=media_file,
                caption=text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        except Exception:
            try:
                # Try to send as document if photo fails
                await message.answer_document(
                    document=media_file,
                    caption=text,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
            except Exception:
                # If both fail, send as text only
                await message.answer(text, reply_markup=keyboard, parse_mode="HTML")
    else:
        # No media, send as text only
        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

async def send_technician_order_with_media_edit(callback: CallbackQuery, item: dict, lang: str, keyboard):
    """Edit technician order message with media if available"""
    text = technician_order_text(item, lang)
    media_file = item.get('media')
    
    if media_file and media_file.strip():
        try:
            # Try to edit as photo first
            await callback.message.edit_media(
                media=InputMediaPhoto(
                    media=media_file,
                    caption=text,
                    parse_mode="HTML"
                ),
                reply_markup=keyboard
            )
        except Exception:
            try:
                # Try to edit as document if photo fails
                await callback.message.edit_media(
                    media=InputMediaDocument(
                        media=media_file,
                        caption=text,
                        parse_mode="HTML"
                    ),
                    reply_markup=keyboard
                )
            except Exception:
                # If both fail, edit as text only
                await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    else:
        # No media, edit as text only
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")

async def send_connection_order_with_media(message: Message, item: dict, lang: str, keyboard: InlineKeyboardMarkup):
    """Send connection order with media if available"""
    text = connection_order_text(item, lang)
    media_path = item.get('media')
    
    if media_path and os.path.exists(media_path):
        try:
            # Try to send as photo first
            with open(media_path, 'rb') as photo:
                await message.answer_photo(
                    photo=photo,
                    caption=text,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
            return
        except Exception:
            try:
                # If photo fails, try as document
                with open(media_path, 'rb') as doc:
                    await message.answer_document(
                        document=doc,
                        caption=text,
                        reply_markup=keyboard,
                        parse_mode='HTML'
                    )
                return
            except Exception:
                pass  # Fall through to text message
    
    # Send as text message if media handling fails or no media
    await message.answer(text, reply_markup=keyboard, parse_mode='HTML')

async def send_connection_order_with_media_edit(cb: CallbackQuery, item: dict, lang: str, keyboard: InlineKeyboardMarkup):
    """Edit message with connection order and media if available"""
    text = connection_order_text(item, lang)
    media_path = item.get('media')
    
    if media_path and os.path.exists(media_path):
        try:
            # Try to edit with photo
            with open(media_path, 'rb') as photo:
                media = InputMediaPhoto(media=photo, caption=text, parse_mode='HTML')
                await cb.message.edit_media(media=media, reply_markup=keyboard)
            return
        except Exception:
            try:
                # If photo fails, try as document
                with open(media_path, 'rb') as doc:
                    media = InputMediaDocument(media=doc, caption=text, parse_mode='HTML')
                    await cb.message.edit_media(media=media, reply_markup=keyboard)
                return
            except Exception:
                pass  # Fall through to text edit
    
    # Edit as text message if media handling fails or no media
    await cb.message.edit_text(text, reply_markup=keyboard, parse_mode='HTML')