from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.basic.language import update_user_language, get_user_language
from filters.role_filter import RoleFilter
from keyboards.client_buttons import get_client_main_menu
import logging

router = Router()
logger = logging.getLogger(__name__)

@router.message(RoleFilter("client"), F.text.in_(["🌐 Tilni o'zgartirish", "🌐 Изменить язык"]))
async def language_handler(message: Message):
    try:
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
            text = "🌐 Til sozlamalari\n\nKerakli tilni tanlang:"
        else:
            text = "🌐 Настройки языка\n\nВыберите нужный язык:"
        
        await message.answer(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.exception(f"Language handler error | User: {message.from_user.id}", exc_info=True)
        try:
            await message.answer("❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")
        except:
            pass

@router.callback_query(RoleFilter("client"), F.data.startswith("lang_"))
async def language_callback_handler(callback: CallbackQuery):
    try:
        language = callback.data.split("_")[1]  # uz yoki ru
        
        # Tilni yangilash
        success = await update_user_language(callback.from_user.id, language)
        
        if success:
            if language == "uz":
                text = "✅ Til muvaffaqiyatli o'zgartirildi!\n\n🇺🇿 O'zbek tili tanlandi"
            else:
                text = "✅ Язык успешно изменен!\n\n🇷🇺 Выбран русский язык"
            
            # Avvalgi xabarni o'chirish va yangi tilda menyuni yuborish
            await callback.message.delete()
            keyboard = get_client_main_menu(language)
            await callback.message.answer(text, reply_markup=keyboard)
        else:
            if language == "uz":
                text = "❌ Tilni o'zgartirishda xatolik yuz berdi"
            else:
                text = "❌ Произошла ошибка при изменении языка"
            
            # Xatolik holatida ham inline keyboardni o'chirish
            await callback.message.edit_text(text)
        
        await callback.answer()
        
    except Exception as e:
        logger.exception(f"Language callback handler error | User: {callback.from_user.id}", exc_info=True)
        try:
            await callback.answer("❌ Xatolik yuz berdi", show_alert=True)
        except:
            pass
