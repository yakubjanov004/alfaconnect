from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext
from filters.role_filter import RoleFilter
from keyboards.admin_buttons import (
    get_admin_export_types_keyboard,
    get_admin_export_formats_keyboard,
)
from utils.export_utils import ExportUtils
from database.admin_export import (
    get_admin_users_for_export,
    get_admin_connection_orders_for_export,
    get_admin_technician_orders_for_export,
    get_admin_saff_orders_for_export,
    get_admin_statistics_for_export,
)
from database.warehouse_queries import (
    get_warehouse_inventory_for_export,
    get_warehouse_statistics_for_export,
)
from datetime import datetime
import logging
from database.language_queries import get_user_language

router = Router()
router.message.filter(RoleFilter(role="admin"))
logger = logging.getLogger(__name__)

@router.message(F.text.in_(["📤 Export", "📤 Экспорт"]))
async def export_handler(message: Message, state: FSMContext):
    await state.clear()
    lang = await get_user_language(message.from_user.id) or "uz"
    await message.answer(
        ("📤 <b>Admin eksportlari</b>\n\nKerakli bo'limni tanlang:" if lang == "uz" else "📤 <b>Экспорт администратора</b>\n\nВыберите нужный раздел:"),
        reply_markup=get_admin_export_types_keyboard(lang),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("admin_export_users_"))
async def admin_export_users(cb: CallbackQuery, state: FSMContext):
    user_type = cb.data.split("_")[-1]  # clients | staff
    await state.update_data(export_type=f"users:{user_type}")
    lang = await get_user_language(cb.from_user.id) or "uz"
    await cb.message.edit_text(
        ("👤 <b>Foydalanuvchilar</b>\n\nFormatni tanlang:" if lang == "uz" else "👤 <b>Пользователи</b>\n\nВыберите формат:"),
        reply_markup=get_admin_export_formats_keyboard(lang),
        parse_mode="HTML",
    )
    await cb.answer()


@router.callback_query(F.data == "admin_export_connection")
async def admin_export_connection(cb: CallbackQuery, state: FSMContext):
    await state.update_data(export_type="connection")
    lang = await get_user_language(cb.from_user.id) or "uz"
    await cb.message.edit_text(
        ("🔌 <b>Ulanish arizalari</b>\n\nFormatni tanlang:" if lang == "uz" else "🔌 <b>Заявки на подключение</b>\n\nВыберите формат:"),
        reply_markup=get_admin_export_formats_keyboard(lang),
        parse_mode="HTML",
    )
    await cb.answer()


@router.callback_query(F.data == "admin_export_technician")
async def admin_export_technician(cb: CallbackQuery, state: FSMContext):
    await state.update_data(export_type="technician")
    lang = await get_user_language(cb.from_user.id) or "uz"
    await cb.message.edit_text(
        ("🔧 <b>Texnik arizalar</b>\n\nFormatni tanlang:" if lang == "uz" else "🔧 <b>Технические заявки</b>\n\nВыберите формат:"),
        reply_markup=get_admin_export_formats_keyboard(lang),
        parse_mode="HTML",
    )
    await cb.answer()


@router.callback_query(F.data == "admin_export_saff")
async def admin_export_saff(cb: CallbackQuery, state: FSMContext):
    await state.update_data(export_type="saff")
    lang = await get_user_language(cb.from_user.id) or "uz"
    await cb.message.edit_text(
        ("👤 <b>Xodim arizalari</b>\n\nFormatni tanlang:" if lang == "uz" else "👤 <b>Заявки сотрудников</b>\n\nВыберите формат:"),
        reply_markup=get_admin_export_formats_keyboard(lang),
        parse_mode="HTML",
    )
    await cb.answer()


@router.callback_query(F.data == "admin_export_statistics")
async def admin_export_statistics(cb: CallbackQuery, state: FSMContext):
    await state.update_data(export_type="statistics")
    lang = await get_user_language(cb.from_user.id) or "uz"
    await cb.message.edit_text(
        ("📊 <b>Statistika</b>\n\nFormatni tanlang:" if lang == "uz" else "📊 <b>Статистика</b>\n\nВыберите формат:"),
        reply_markup=get_admin_export_formats_keyboard(lang),
        parse_mode="HTML",
    )
    await cb.answer()


@router.callback_query(F.data == "admin_export_back_types")
async def admin_export_back_types(cb: CallbackQuery, state: FSMContext):
    await state.update_data(export_type=None)
    lang = await get_user_language(cb.from_user.id) or "uz"
    await cb.message.edit_text(
        ("📤 <b>Admin eksportlari</b>\n\nKerakli bo'limni tanlang:" if lang == "uz" else "📤 <b>Экспорт администратора</b>\n\nВыберите нужный раздел:"),
        reply_markup=get_admin_export_types_keyboard(lang),
        parse_mode="HTML",
    )
    await cb.answer()


@router.callback_query(F.data == "admin_export_end")
async def admin_export_end(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await cb.message.delete()
    except Exception:
        pass
    lang = await get_user_language(cb.from_user.id) or "uz"
    await cb.answer("Yopildi" if lang == "uz" else "Закрыто")


@router.callback_query(F.data.startswith("admin_format_"))
async def admin_export_format(cb: CallbackQuery, state: FSMContext):
    format_type = cb.data.split("_")[-1]  # csv | xlsx | docx | pdf
    data = await state.get_data()
    export_type = data.get("export_type", "connection")

    lang = await get_user_language(cb.from_user.id) or "uz"
    await cb.message.edit_text(("⏳ <b>Eksport tayyorlanmoqda...</b>" if lang == "uz" else "⏳ <b>Экспорт подготавливается...</b>"), parse_mode="HTML")

    try:
        title = ""
        filename_base = "export"
        headers = []

        if export_type.startswith("users:"):
            user_type = export_type.split(":")[1]
            raw_data = await get_admin_users_for_export("clients" if user_type == "clients" else "staff")
            title = ("Foydalanuvchilar (mijozlar)" if user_type == "clients" else "Xodimlar") if lang == "uz" else ("Пользователи (клиенты)" if user_type == "clients" else "Сотрудники")
            filename_base = f"users_{user_type}"
            headers = ["ID", "Telegram ID", "Username", "Ism", "Telefon", "Rol", "Yaratilgan", "Yangilangan", "Bloklangan"]
        elif export_type == "connection":
            raw_data = await get_admin_connection_orders_for_export()
            title = "Ulanish arizalari" if lang == "uz" else "Заявки на подключение"
            filename_base = "connection_orders"
        elif export_type == "technician":
            raw_data = await get_admin_technician_orders_for_export()
            title = "Texnik arizalar" if lang == "uz" else "Технические заявки"
            filename_base = "technician_orders"
        elif export_type == "saff":
            raw_data = await get_admin_saff_orders_for_export()
            title = "Xodim arizalari" if lang == "uz" else "Заявки сотрудников"
            filename_base = "saff_orders"
        elif export_type == "warehouse_inventory":
            raw_data = await get_warehouse_inventory_for_export()
            title = "Ombor inventarizatsiyasi" if lang == "uz" else "Инвентаризация склада"
            filename_base = "warehouse_inventory"
            headers = [
                ("ID" if lang == "uz" else "ID"),
                ("Nomi" if lang == "uz" else "Название"),
                ("Seriya raqami" if lang == "uz" else "Серийный №"),
                ("Miqdor" if lang == "uz" else "Количество"),
                ("Narx" if lang == "uz" else "Цена"),
                ("Yaratilgan" if lang == "uz" else "Создано"),
            ]
        elif export_type == "warehouse_stats":
            raw_data = await get_warehouse_statistics_for_export('all')
            title = "Ombor statistikasi" if lang == "uz" else "Статистика склада"
            filename_base = "warehouse_statistics"
        elif export_type == "statistics":
            stats = await get_admin_statistics_for_export()
            # Flatten to rows
            raw_rows = []
            label_key = "Ko'rsatkich" if lang == "uz" else "Показатель"
            value_key = "Qiymat" if lang == "uz" else "Значение"
            raw_rows.append({label_key: ("Jami foydalanuvchilar" if lang == "uz" else "Всего пользователей"), value_key: stats["users"]["total"]})
            raw_rows.append({label_key: ("Mijozlar" if lang == "uz" else "Клиенты"), value_key: stats["users"]["clients"]})
            raw_rows.append({label_key: ("Xodimlar" if lang == "uz" else "Сотрудники"), value_key: stats["users"]["staff"]})
            for r in stats["users"]["by_role"]:
                raw_rows.append({label_key: (f"Rol: {r['role']}" if lang == "uz" else f"Роль: {r['role']}"), value_key: r['cnt']})
            raw_rows.append({label_key: ("Ulanish arizalari" if lang == "uz" else "Заявки на подключение"), value_key: stats["orders"]["connection_total"]})
            raw_rows.append({label_key: ("Texnik arizalar" if lang == "uz" else "Технические заявки"), value_key: stats["orders"]["technician_total"]})
            raw_rows.append({label_key: ("Xodim arizalari" if lang == "uz" else "Заявки сотрудников"), value_key: stats["orders"]["saff_total"]})
            for r in stats["orders"]["connection_by_status"]:
                raw_rows.append({label_key: (f"Ulanish: {r['status']}" if lang == "uz" else f"Подключение: {r['status']}"), value_key: r['cnt']})
            for r in stats["orders"]["technician_by_status"]:
                raw_rows.append({label_key: (f"Texnik: {r['status']}" if lang == "uz" else f"Тех: {r['status']}"), value_key: r['cnt']})
            raw_data = raw_rows
            title = "Statistika" if lang == "uz" else "Статистика"
            filename_base = "statistics"
            headers = (["Ko'rsatkich", "Qiymat"] if lang == "uz" else ["Показатель", "Значение"])
        else:
            raw_data = []

        export_utils = ExportUtils()

        if format_type == "csv":
            file_data = export_utils.to_csv(raw_data, headers=headers if headers else None)
            file_to_send = BufferedInputFile(file_data.getvalue(), filename=f"{filename_base}_{int(datetime.now().timestamp())}.csv")
        elif format_type == "xlsx":
            file_data = export_utils.generate_excel(raw_data, sheet_name="export", title=title)
            file_to_send = BufferedInputFile(file_data.getvalue(), filename=f"{filename_base}_{int(datetime.now().timestamp())}.xlsx")
        elif format_type == "docx":
            file_data = export_utils.generate_word(raw_data, title=title)
            file_to_send = BufferedInputFile(file_data.getvalue(), filename=f"{filename_base}_{int(datetime.now().timestamp())}.docx")
        elif format_type == "pdf":
            file_data = export_utils.generate_pdf(raw_data, title=title)
            file_to_send = BufferedInputFile(file_data.getvalue(), filename=f"{filename_base}_{int(datetime.now().timestamp())}.pdf")
        else:
            await cb.answer("Format noto'g'ri", show_alert=True)
            return

        await cb.message.answer_document(
            document=file_to_send,
            caption=f"📤 {title} — {format_type.upper()}",
        )

        await cb.message.answer(
            ("Yana qaysi bo'limni eksport qilamiz?" if lang == "uz" else "Что экспортируем дальше?"),
            reply_markup=get_admin_export_types_keyboard(lang),
        )

    except Exception as e:
        logger.error(f"Admin export error: {e}", exc_info=True)
        await cb.message.answer("❌ Eksportda xatolik yuz berdi")
    finally:
        await cb.answer()


# Warehouse specific selections -> format selection
@router.callback_query(F.data == "admin_export_warehouse_inventory")
async def admin_export_wh_inventory(cb: CallbackQuery, state: FSMContext):
    await state.update_data(export_type="warehouse_inventory")
    lang = await get_user_language(cb.from_user.id) or "uz"
    await cb.message.edit_text(
        ("📦 <b>Ombor inventarizatsiyasi</b>\n\nFormatni tanlang:" if lang == "uz" else "📦 <b>Инвентаризация склада</b>\n\nВыберите формат:"),
        reply_markup=get_admin_export_formats_keyboard(lang),
        parse_mode="HTML",
    )
    await cb.answer()

@router.callback_query(F.data == "admin_export_warehouse_stats")
async def admin_export_wh_stats(cb: CallbackQuery, state: FSMContext):
    await state.update_data(export_type="warehouse_stats")
    lang = await get_user_language(cb.from_user.id) or "uz"
    await cb.message.edit_text(
        ("📊 <b>Ombor statistikasi</b>\n\nFormatni tanlang:" if lang == "uz" else "📊 <b>Статистика склада</b>\n\nВыберите формат:"),
        reply_markup=get_admin_export_formats_keyboard(lang),
        parse_mode="HTML",
    )
    await cb.answer()

@router.callback_query(F.data == "admin_export_warehouse_low_stock")
async def admin_export_wh_low(cb: CallbackQuery, state: FSMContext):
    await state.update_data(export_type="warehouse_low_stock")
    lang = await get_user_language(cb.from_user.id) or "uz"
    await cb.message.edit_text(
        ("⚠️ <b>Kam zaxira</b>\n\nFormatni tanlang:" if lang == "uz" else "⚠️ <b>Низкий остаток</b>\n\nВыберите формат:"),
        reply_markup=get_admin_export_formats_keyboard(lang),
        parse_mode="HTML",
    )
    await cb.answer()

@router.callback_query(F.data == "admin_export_warehouse_out_of_stock")
async def admin_export_wh_oos(cb: CallbackQuery, state: FSMContext):
    await state.update_data(export_type="warehouse_out_of_stock")
    lang = await get_user_language(cb.from_user.id) or "uz"
    await cb.message.edit_text(
        ("⛔ <b>Zaxira tugagan</b>\n\nFormatni tanlang:" if lang == "uz" else "⛔ <b>Нет в наличии</b>\n\nВыберите формат:"),
        reply_markup=get_admin_export_formats_keyboard(lang),
        parse_mode="HTML",
    )
    await cb.answer()
