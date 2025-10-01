from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import html

from database.queries import get_or_create_user, find_user_by_telegram_id, update_user_phone, update_user_full_name
from database.language_queries import get_user_language

from keyboards.admin_buttons import get_admin_main_menu
from keyboards.client_buttons import get_client_main_menu, get_contact_keyboard
from keyboards.manager_buttons import get_manager_main_menu
from keyboards.junior_manager_buttons import get_junior_manager_main_menu
from keyboards.controllers_buttons import get_controller_main_menu
from keyboards.technician_buttons import get_technician_main_menu
from keyboards.warehouse_buttons import get_warehouse_main_menu
from keyboards.call_center_supervisor_buttons import get_call_center_supervisor_main_menu
from keyboards.call_center_buttons import get_call_center_main_keyboard

router = Router()

class UserRegistration(StatesGroup):
    waiting_for_full_name = State()

@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    user = message.from_user
    
    # Check if user exists in database
    db_user = await find_user_by_telegram_id(user.id)
    # Resolve language early for correct replies
    lang = await get_user_language(user.id) or "uz"
    
    # If user doesn't exist, create with minimal info
    if not db_user:
        role = await get_or_create_user(
            telegram_id=user.id,
            username=user.username,
            full_name=None  # Don't save Telegram full_name initially
        )
        db_user = await find_user_by_telegram_id(user.id)
    else:
        # Get existing role
        role = db_user.get("role", "client")

    # If user does not have a phone number yet, request contact share
    user_phone = db_user.get("phone") if db_user else None
    if not user_phone:
        await message.answer(
            "Iltimos, raqamingizni jo'nating (tugma orqali)." if lang == "uz" else "Пожалуйста, поделитесь своим номером (через кнопку).",
            reply_markup=get_contact_keyboard()
        )
        return
    
    # Always check for full_name and ask if not present
    if not db_user.get("full_name"):
        await state.set_state(UserRegistration.waiting_for_full_name)
        await message.answer(
            "Iltimos, to'liq ism-sharifingizni (FISH) kiriting:" if lang == "uz" else "Пожалуйста, введите ваше полное имя:",
            reply_markup=None
        )
        return

    await show_main_menu(message, role)

@router.message(F.contact)
async def handle_contact_share(message: Message, state: FSMContext):
    """Handle user's shared contact and save phone number."""
    if not message.contact:
        return

    # Only accept the sender's own contact
    if message.contact.user_id and message.contact.user_id != message.from_user.id:
        lang = await get_user_language(message.from_user.id) or "uz"
        await message.answer(
            "Iltimos, faqat o'zingizning raqamingizni yuboring." if lang == "uz" else "Пожалуйста, отправьте только свой номер.",
            reply_markup=get_contact_keyboard()
        )
        return

    phone = message.contact.phone_number
    await update_user_phone(message.from_user.id, phone)
    
    # After saving phone, ask for full name
    await state.set_state(UserRegistration.waiting_for_full_name)
    lang = await get_user_language(message.from_user.id) or "uz"
    await message.answer(
        "Raqamingiz saqlandi. Iltimos, to'liq ism-sharifingizni (FISH) kiriting:" if lang == "uz" else "Ваш номер сохранён. Пожалуйста, введите ваше полное имя:",
        reply_markup=None
    )


@router.message(UserRegistration.waiting_for_full_name)
async def process_full_name(message: Message, state: FSMContext):
    """Process user's full name input."""
    full_name = message.text.strip()
    lang = await get_user_language(message.from_user.id) or "uz"
    
    if len(full_name) < 3:  # Basic validation
        await message.answer(
            "Iltimos, to'g'ri ism-sharif kiriting (kamida 3 ta belgi)." if lang == "uz" else "Пожалуйста, введите корректное имя (минимум 3 символа)."
        )
        return
    
    # Save full name to database
    await update_user_full_name(message.from_user.id, full_name)
    await state.clear()
    
    # Get user role and show main menu
    role = await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        full_name=full_name
    )
    await show_main_menu(message, role)


async def show_main_menu(message: Message, role: str):
    """Show appropriate main menu based on user role."""
    user_language = await get_user_language(message.from_user.id) or "uz"
    
    role_keyboards = {
        "admin": get_admin_main_menu(user_language),
        "client": get_client_main_menu(user_language),
        "manager": get_manager_main_menu(user_language),
        "junior_manager": get_junior_manager_main_menu(user_language),
        "controller": get_controller_main_menu(user_language),
        "technician": get_technician_main_menu(user_language),
        "warehouse": get_warehouse_main_menu(user_language),
        "callcenter_supervisor": get_call_center_supervisor_main_menu(user_language),
        "callcenter_operator": get_call_center_main_keyboard(user_language),
    }

    keyboard = role_keyboards.get(role, get_client_main_menu(user_language))
    
    # Database dan full_name olish
    db_user = await find_user_by_telegram_id(message.from_user.id)
    full_name = db_user.get("full_name") if db_user else message.from_user.full_name
    
    if full_name:
        full_name = html.escape(full_name)
        greeting = (
            f"Assalomu alaykum, {full_name}!" if user_language == "uz" else f"Здравствуйте, {full_name}!"
        )
        await message.answer(greeting, reply_markup=keyboard, parse_mode="HTML")
    else:
        await message.answer(
            "Assalomu alaykum!" if user_language == "uz" else "Здравствуйте!",
            reply_markup=keyboard,
            parse_mode="HTML"
        )