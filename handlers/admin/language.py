from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.language_queries import update_user_language, get_user_language
from keyboards.admin_buttons import get_admin_main_menu
from filters.role_filter import RoleFilter

router = Router()

@router.message(RoleFilter("admin"), F.text.in_(["🌐 Til", "🌐 Язык"]))
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
        text = "🌐 Til sozlamalari\n\nKerakli tilni tanlang:\n\n👤 Rol: Admin"
    else:
        text = "🌐 Настройки языка\n\nВыберите нужный язык:\n\n👤 Роль: Админ"
    
    await message.answer(text, reply_markup=keyboard)

@router.callback_query(RoleFilter("admin"), F.data.startswith("lang_"))
async def language_callback_handler(callback: CallbackQuery):
    language = callback.data.split("_")[1]  # uz yoki ru
    
    # Tilni yangilash
    success = await update_user_language(callback.from_user.id, language)
    
    if success:
        if language == "uz":
            text = "✅ Til muvaffaqiyatli o'zgartirildi!\n\n🇺🇿 O'zbek tili tanlandi"
        else:
            text = "✅ Язык успешно изменен!\n\n🇷🇺 Выбран русский язык"
        
        # Avvalgi xabarni o'chirish
        await callback.message.delete()
        
        # Yangi tilda admin menyusini ko'rsatish
        keyboard = get_admin_main_menu(language)
        await callback.message.answer(
            text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        if language == "uz":
            text = "❌ Tilni o'zgartirishda xatolik yuz berdi"
        else:
            text = "❌ Произошла ошибка при изменении языка"
        
        # Xatolik holatida ham inline keyboardni o'chirish
        await callback.message.edit_text(text)
    
    await callback.answer()