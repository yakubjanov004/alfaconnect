from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.language_queries import update_user_language, get_user_language
from filters.role_filter import RoleFilter
from keyboards.manager_buttons import get_manager_main_menu

router = Router()

@router.message(RoleFilter("manager"), F.text.in_(["🌐 Tilni o'zgartirish", "🌐 Изменить язык"]))
async def language_handler(message: Message):
    # Foydalanuvchi tilini olish
    current_language = await get_user_language(message.from_user.id)
    
    # Inline tugmalar yaratish
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🇺🇿 O'zbek tili" + (" ✅" if current_language == "uz" else ""),
                callback_data="lang_uz"
            )
        ],
        [
            InlineKeyboardButton(
                text="🇷🇺 Русский язык" + (" ✅" if current_language == "ru" else ""),
                callback_data="lang_ru"
            )
        ]
    ])
    
    if current_language == "uz":
        text = "🌐 Til sozlamalari\n\nKerakli tilni tanlang:\n\n👤 Rol: Menejer"
    else:
        text = "🌐 Настройки языка\n\nВыберите нужный язык:\n\n👤 Роль: Менеджер"
    
    await message.answer(text, reply_markup=keyboard)

@router.callback_query(RoleFilter("manager"), F.data.startswith("lang_"))
async def language_callback_handler(callback: CallbackQuery):
    language = callback.data.split("_")[1]  # uz yoki ru
    
    # Tilni yangilash
    success = await update_user_language(callback.from_user.id, language)
    
    if success:
        if language == "uz":
            text = "✅ Til muvaffaqiyatli o'zgartirildi!\n\n🇺🇿 O'zbek tili tanlandi\n\n👤 Rol: Menejer"
        else:
            text = "✅ Язык успешно изменен!\n\n🇷🇺 Выбран русский язык\n\n👤 Роль: Менеджер"
        
        # Avvalgi xabarni o'chirish va yangi tilda menyuni yuborish
        await callback.message.delete()
        keyboard = get_manager_main_menu(language)
        await callback.message.answer(text, reply_markup=keyboard)
    else:
        if language == "uz":
            text = "❌ Tilni o'zgartirishda xatolik yuz berdi"
        else:
            text = "❌ Произошла ошибка при изменении языка"
        
        # Xatolik holatida ham inline keyboardni o'chirish
        await callback.message.edit_text(text)
    
    await callback.answer()
