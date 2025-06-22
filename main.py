from dotenv import load_dotenv

# טען את קובץ ה-.env
load_dotenv()

import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ChatType
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery, ChatMemberUpdated
from keyboards import (
    get_start_keyboard, get_back_keyboard, get_add_product_keyboard,
    get_summary_keyboard, get_product_selection_keyboard, get_edit_action_keyboard
)
from states import OrderStates

from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ChatType

from states import OrderStates
from keyboards import (
    get_start_keyboard, get_back_keyboard, get_add_product_keyboard,
    get_summary_keyboard
)

import os

# הגדרת משתנה גלובלי למספר קבוצות מקסימלי
MAX_ACTIVE_GROUPS = 1  # שנה ערך זה כדי לאפשר יותר קבוצות בו זמנית

# הכנס כאן את הטוקן של הבוט שלך
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN or BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
    raise ValueError("❌ לא הוגדר טוקן בוט! אנא הגדירו את משתנה הסביבה BOT_TOKEN")

# הגדרת לוגים מפורטים יותר לניטור פעילות הבוט בשרת:
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# מונה הזמנות גלובלי
order_counter = 1
# רשימת קבוצות פעילות
active_groups = set()

@dp.my_chat_member()
async def on_chat_member_updated(update: ChatMemberUpdated) -> None:
    """מטפל בעדכוני חברות בצ'אט, כולל הסרת הבוט מקבוצה"""
    chat_id = update.chat.id
    # בדיקה אם הבוט הוסר מהקבוצה
    if update.new_chat_member.status in ["left", "kicked"]:
        if chat_id in active_groups:
            active_groups.discard(chat_id)
            logging.info(f"הבוט הוסר מקבוצה {chat_id}. הקבוצה הוסרה מרשימת הקבוצות הפעילות.")

# פונקציה לבדיקת הגבלת קבוצה
async def check_group_limit(message_or_callback) -> bool:
    """
    בודק אם הקבוצה עומדת במגבלת הקבוצות הפעילות.
    Args:
        message_or_callback: הודעה או קולבק מהמשתמש
    Returns:
        bool: האם הקבוצה עומדת במגבלה
    """
    # קבלת מזהה הצ'אט
    if hasattr(message_or_callback, 'message'):
        chat_id = message_or_callback.message.chat.id
        chat_type = message_or_callback.message.chat.type
    else:
        chat_id = message_or_callback.chat.id
        chat_type = message_or_callback.chat.type
    # אם זה צ'אט פרטי, אפשר תמיד
    if chat_type == ChatType.PRIVATE:
        return True
    # בדיקת מגבלת קבוצות (מקסימום קבוצות פעילות)
    if chat_id not in active_groups:
        if len(active_groups) >= MAX_ACTIVE_GROUPS:
            if hasattr(message_or_callback, 'message'):
                await message_or_callback.answer("❌ הבוט כבר פעיל במספר קבוצות מירבי. אנא נסו מאוחר יותר.")
            else:
                await message_or_callback.answer(
                    "❌ הבוט כבר פעיל במספר קבוצות מירבי. אנא נסו מאוחר יותר.",
                    reply_markup=get_start_keyboard()
                )
            return False
        active_groups.add(chat_id)
    return True


@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    if not await check_group_limit(message):
        return
        
    await state.clear()
    await message.answer(
        "🛒 ברוכים הבאים לבוט הזמנות!\n\n"
        "לחצו על הכפתור למטה כדי להתחיל הזמנה חדשה:",
        reply_markup=get_start_keyboard()
    )

@dp.callback_query(F.data == "start_order")
async def start_order(callback: CallbackQuery, state: FSMContext):
    if not await check_group_limit(callback):
        return
        
    await callback.answer()
    await state.set_state(OrderStates.waiting_for_nickname)
    await callback.message.edit_text(
        "📝 שלב 1/8: הכנסת כינוי\n\n"
        "אנא הכניסו את הכינוי שלכם:",
        reply_markup=get_back_keyboard()
    )

@dp.message(StateFilter(OrderStates.waiting_for_nickname))
async def process_nickname(message: Message, state: FSMContext):
    await state.update_data(nickname=message.text)
    await state.set_state(OrderStates.waiting_for_username)
    await message.answer(
        "📝 שלב 2/8: שם משתמש טלגרם\n\n"
        "אנא הכניסו את שם המשתמש שלכם בטלגרם (לדוגמה: @example):",
        reply_markup=get_back_keyboard()
    )

@dp.message(StateFilter(OrderStates.waiting_for_username))
async def process_username(message: Message, state: FSMContext):
    username = message.text
    if not username.startswith('@'):
        username = '@' + username
    await state.update_data(username=username)
    await state.set_state(OrderStates.waiting_for_address)
    await message.answer(
        "📝 שלב 3/8: כתובת\n\n"
        "אנא הכניסו את הכתובת שלכם:",
        reply_markup=get_back_keyboard()
    )

@dp.message(StateFilter(OrderStates.waiting_for_address))
async def process_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text, products=[])
    await state.set_state(OrderStates.waiting_for_product_type)
    await message.answer(
        "📝 שלב 4/8: הוספת מוצרים\n\n"
        "אנא הכניסו את סוג המוצר הראשון:",
        reply_markup=get_back_keyboard()
    )

@dp.message(StateFilter(OrderStates.waiting_for_product_type))
async def process_product_type(message: Message, state: FSMContext):
    await state.update_data(current_product_type=message.text)
    await state.set_state(OrderStates.waiting_for_quantity)
    await message.answer(
        f"📦 מוצר: {message.text}\n\n"
        "🧮 הכנס את הכמות (מספר):",
        reply_markup=get_back_keyboard()
    )

@dp.message(StateFilter(OrderStates.waiting_for_quantity))
async def process_quantity(message: Message, state: FSMContext):
    try:
        quantity = int(message.text)
        await state.update_data(current_quantity=quantity)
        await state.set_state(OrderStates.waiting_for_price)
        data = await state.get_data()
        product_type = data.get('current_product_type')
        await message.answer(
            f"📦 מוצר: {product_type}\n"
            f"🧮 כמות: {quantity:,}\n\n"
            "💲 הכנס את המחיר ליחידה (מספר):",
            reply_markup=get_back_keyboard()
        )
    except ValueError:
        await message.answer(
            "❌ אנא הכניסו מספר תקין עבור הכמות:",
            reply_markup=get_back_keyboard()
        )

@dp.message(StateFilter(OrderStates.waiting_for_price))
async def process_price(message: Message, state: FSMContext):
    try:
        price = float(message.text)
        data = await state.get_data()
        
        product_type = data.get('current_product_type')
        quantity = data.get('current_quantity')
        total_price = quantity * price
        
        # הוספת המוצר לרשימה
        products = data.get('products', [])
        products.append({
            'type': product_type,
            'quantity': quantity,
            'price': price,
            'total': total_price
        })
        
        await state.update_data(products=products)
            
        # חישוב סה\"כ כולל כולל
        grand_total = sum(product['total'] for product in products)
        
        products_text = "\n".join([
            f"• {p['type']}: {p['quantity']:,} × {p['price']:,} = {p['total']:,} ₪"
            for p in products
        ])
        
        await message.answer(
            f"✅ המוצר נוסף בהצלחה!\n\n"
            f"📋 רשימת מוצרים עד כה:\n{products_text}\n\n"
            f"💰 סה\"כ כולל: {grand_total:,} ₪\n\n"
            "האם אתם מאשרים את הזמנה?",
            reply_markup=get_add_product_keyboard()
        )
        
    except ValueError:
        await message.answer(
            "❌ אנא הכניסו מספר תקין עבור המחיר:",
            reply_markup=get_back_keyboard()
        )

@dp.callback_query(F.data == "add_product")
async def add_another_product(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(OrderStates.waiting_for_product_type)
    await callback.message.edit_text(
        "📝 הוספת מוצר נוסף\n\n"
        "אנא הכניסו את סוג המוצר:",
        reply_markup=get_back_keyboard()
    )

@dp.callback_query(F.data == "continue_payment")
async def continue_to_payment(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    products = data.get('products', [])
    grand_total = sum(product['total'] for product in products)
    
    await state.update_data(grand_total=grand_total)
    await state.set_state(OrderStates.waiting_for_cash_amount)
    
    await callback.message.edit_text(
        f"📝 שלב 6/8: חלוקה לתשלום\n\n"
        f"💰 סה\"כ לתשלום: {grand_total:,} ₪\n\n"
        "💵 אנא הכניסו את הסכום במזומן:",
        reply_markup=get_back_keyboard()
    )

@dp.message(StateFilter(OrderStates.waiting_for_cash_amount))
async def process_cash_amount(message: Message, state: FSMContext):
    try:
        cash_amount = float(message.text)
        data = await state.get_data()
        grand_total = data.get('grand_total')
        credit_amount = grand_total - cash_amount
        await state.update_data(cash_amount=cash_amount)
        await state.set_state(OrderStates.waiting_for_credit_amount)
        await message.answer(
            f"💵 מזומן: {cash_amount:,} ₪\n"
            f"💳 נותר לאשראי: {credit_amount:,} ₪\n\n"
            "💳 אנא הכניסו את הסכום באשראי לאישור:",
            reply_markup=get_back_keyboard()
        )
    except ValueError:
        await message.answer(
            "❌ אנא הכניסו מספר תקין עבור הסכום במזומן:",
            reply_markup=get_back_keyboard()
        )

@dp.message(StateFilter(OrderStates.waiting_for_credit_amount))
async def process_credit_amount(message: Message, state: FSMContext):
    try:
        credit_amount = float(message.text)
        data = await state.get_data()
        cash_amount = data.get('cash_amount')
        grand_total = data.get('grand_total')
        
        total_payment = cash_amount + credit_amount
        
        if abs(total_payment - grand_total) > 0.01:  # טולרנס לשגיאות עיגול
            await message.answer(
                f"❌ שגיאה בחישוב!\n\n"
                f"💰 סה\"כ להזמנה: {grand_total:,} ₪\n"
                f"💵 מזומן: {cash_amount:,} ₪\n"
                f"💳 אשראי: {credit_amount:,} ₪\n"
                f"🧮 סה\"כ תשלום: {total_payment:,} ₪\n\n"
                f"הפרש: {total_payment - grand_total:,} ₪\n\n"
                "אנא הכניסו סכום אשראי שיתאים לסה\"כ:",
                reply_markup=get_back_keyboard()
            )
            return
        
        await state.update_data(credit_amount=credit_amount)
        await state.set_state(OrderStates.waiting_for_notes)
        
        await message.answer(
            "📝 שלב 7/8: הערות\n\n"
            "אנא הכניסו הערות נוספות (או שלחו 'ללא' אם אין הערות):",
            reply_markup=get_back_keyboard()
        )
        
    except ValueError:
        await message.answer(
            "❌ אנא הכניסו מספר תקין עבור הסכום באשראי:",
            reply_markup=get_back_keyboard()
        )

@dp.message(StateFilter(OrderStates.waiting_for_notes))
async def process_notes(message: Message, state: FSMContext):
    notes = message.text.strip()
    await state.update_data(notes=notes)
    await show_updated_summary(message, state)

@dp.message(Command("stop"))
async def cmd_stop(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ ההזמנה בוטלה.\n\nתוכלו להתחיל הזמנה חדשה בכל עת עם /start"
    )

@dp.message(Command("help"))
async def cmd_help(message: Message, state: FSMContext):
    await message.answer(
        "🤖 עזרה לבוט הזמנות:\n\n"
        "/start - התחלת הזמנה חדשה\n"
        "/stop - ביטול הזמנה נוכחית\n"
        "/help - הצגת הודעה זו\n\n"
        "לשאלות נוספות, אנא פנו למנהל המערכת."
    )

@dp.callback_query(F.data == "edit_order")
async def edit_order(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    products = data.get('products', [])
    
    if not products:
        await callback.message.edit_text(
            "❌ אין מוצרים להצגה.",
            reply_markup=get_summary_keyboard()
        )
        return
    
    await state.set_state(OrderStates.selecting_product_to_edit)
    await callback.message.edit_text(
        "📝 בחר מוצר לעריכה:",
        reply_markup=get_product_selection_keyboard(products)
    )

@dp.callback_query(F.data.startswith("select_product_"))
async def select_product_to_edit(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    product_index = int(callback.data.split("_")[-1])
    await state.update_data(editing_product_index=product_index)
    
    data = await state.get_data()
    products = data.get('products', [])
    selected_product = products[product_index]
    
    await state.set_state(OrderStates.choosing_edit_action)
    await callback.message.edit_text(
        f"📦 מוצר נבחר: {selected_product['type']}\n"
        f"כמות: {selected_product['quantity']:,}\n"
        f"מחיר ליחידה: {selected_product['price']:,} ₪\n\n"
        "מה תרצה לעשות?",
        reply_markup=get_edit_action_keyboard()
    )

@dp.callback_query(F.data == "delete_product")
async def delete_product(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    products = data.get('products', [])
    product_index = data.get('editing_product_index')
    
    # מחיקת המוצר
    deleted_product = products.pop(product_index)
    
    # עדכון הסכום הכולל
    grand_total = data.get('grand_total', 0)
    new_grand_total = grand_total - deleted_product['total']
    
    await state.update_data(products=products, grand_total=new_grand_total)
    
    # בדיקה אם נותרו מוצרים
    if not products:
        await callback.message.edit_text(
            "❌ ההזמנה בוטלה - לא נותרו מוצרים.\n\n"
            "תוכל להתחיל הזמנה חדשה עם /start"
        )
        await state.clear()
        return
    
    # חזרה לסיכום עם המוצרים המעודכנים
    await show_updated_summary(callback, state)

@dp.callback_query(F.data == "edit_product")
async def edit_product(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(OrderStates.editing_product_type)
    await callback.message.edit_text(
        "📝 הכנס את שם המוצר החדש:",
        reply_markup=get_back_keyboard()
    )

@dp.message(StateFilter(OrderStates.editing_product_type))
async def process_edited_product_type(message: Message, state: FSMContext):
    product_type = message.text.strip()
    await state.update_data(editing_product_type=product_type)
    await state.set_state(OrderStates.editing_quantity)
    await message.answer(
        f"📦 מוצר: {product_type}\n\n"
        "💯 הכנס את הכמות החדשה:",
        reply_markup=get_back_keyboard()
    )

@dp.message(StateFilter(OrderStates.editing_quantity))
async def process_edited_quantity(message: Message, state: FSMContext):
    try:
        quantity = int(message.text.replace(',', ''))
        if quantity <= 0:
            raise ValueError
        
        await state.update_data(editing_quantity=quantity)
        await state.set_state(OrderStates.editing_price)
        
        data = await state.get_data()
        product_type = data.get('editing_product_type')
        
        await message.answer(
            f"📦 מוצר: {product_type}\n"
            f"💯 כמות: {quantity:,}\n\n"
            "💰 הכנס את המחיר החדש ליחידה:",
            reply_markup=get_back_keyboard()
        )
    except ValueError:
        await message.answer(
            "❌ אנא הכנס מספר תקין וחיובי לכמות.",
            reply_markup=get_back_keyboard()
        )

@dp.message(StateFilter(OrderStates.editing_price))
async def process_edited_price(message: Message, state: FSMContext):
    try:
        price = float(message.text.replace(',', ''))
        if price <= 0:
            raise ValueError
        
        data = await state.get_data()
        products = data.get('products', [])
        product_index = data.get('editing_product_index')
        quantity = data.get('editing_quantity')
        product_type = data.get('editing_product_type')
        
        # חישוב הסכום החדש
        total = quantity * price
        
        # עדכון המוצר
        old_total = products[product_index]['total']
        products[product_index] = {
            'type': product_type,
            'quantity': quantity,
            'price': price,
            'total': total
        }
        
        # עדכון הסכום הכולל
        grand_total = data.get('grand_total', 0)
        new_grand_total = grand_total - old_total + total
        
        await state.update_data(products=products, grand_total=new_grand_total)
        
        # חזרה לסיכום
        await show_updated_summary(message, state)
        
    except ValueError:
        await message.answer(
            "❌ אנא הכנס מספר תקין וחיובי למחיר.",
            reply_markup=get_back_keyboard()
        )

async def show_updated_summary(message_or_callback, state: FSMContext):
    """מציג את הסיכום המעודכן אחרי עריכה"""
    data = await state.get_data()
    global order_counter
    products = data.get('products', [])
    products_text = "\n".join([
        f"מוצר:: {p['type']}\n"
        f"כמות:: {p['quantity']:,}\n"
        f"מחיר ליחידה:: {p['price']:,}\n"
        f"סה\"כ:: {p['total']:,}\n"
        for p in products
    ])
    summary = (
        f"🧾 בון מספר #{order_counter}\n"
        f"כינוי:: {data.get('nickname')}\n"
        f"יוזר:: {data.get('username')}\n"
        f"כתובת:: {data.get('address')}\n\n"
        f"{products_text}\n"
        f"💰 סה\"כ כולל:: {data.get('grand_total'):,} ₪\n"
        f"תשלום:: {data.get('cash_amount'):,} מזומן 🟩, {data.get('credit_amount'):,} אשראי 🟥\n"
    )
    notes = data.get('notes')
    if notes:
        summary += f"הערה:: {notes}\n"
    await state.update_data(final_summary=summary)
    await state.set_state(OrderStates.showing_summary)
    text = f"📝 שלב 8/8: סיכום הזמנה (מעודכן)\n\n{summary}\nהאם אתם מאשרים את הזמנה?"
    reply_markup = get_summary_keyboard()
    try:
        if hasattr(message_or_callback, 'edit_text') and callable(getattr(message_or_callback, 'edit_text', None)):
            await message_or_callback.edit_text(text, reply_markup=reply_markup)
        elif hasattr(message_or_callback, 'answer') and callable(getattr(message_or_callback, 'answer', None)):
            await message_or_callback.answer(text, reply_markup=reply_markup)
        else:
            chat_id = None
            if hasattr(message_or_callback, 'chat'):
                chat_id = message_or_callback.chat.id
            elif hasattr(message_or_callback, 'message') and hasattr(message_or_callback.message, 'chat'):
                chat_id = message_or_callback.message.chat.id
            if chat_id:
                await bot.send_message(chat_id, text, reply_markup=reply_markup)
    except Exception as e:
        # fallback: שלח הודעה חדשה
        chat_id = None
        if hasattr(message_or_callback, 'chat'):
            chat_id = message_or_callback.chat.id
        elif hasattr(message_or_callback, 'message') and hasattr(message_or_callback.message, 'chat'):
            chat_id = message_or_callback.message.chat.id
        if chat_id:
            await bot.send_message(chat_id, text, reply_markup=reply_markup)

@dp.callback_query(F.data == "back_to_summary")
async def back_to_summary(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await show_updated_summary(callback, state)

@dp.callback_query(F.data == "back_to_product_selection")
async def back_to_product_selection(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    products = data.get('products', [])
    
    await state.set_state(OrderStates.selecting_product_to_edit)
    await callback.message.edit_text(
        "📝 בחר מוצר לעריכה:",
        reply_markup=get_product_selection_keyboard(products)
    )

@dp.callback_query(F.data == "confirm_order")
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    global order_counter
    summary = data.get('final_summary')
    if not summary:
        await callback.message.answer("❌ לא נמצא סיכום הזמנה. אנא נסה שוב.")
        return
    # שלח את הבון כהודעה חדשה
    await callback.message.answer(f"✅ ההזמנה אושרה!\n\n{summary}")
    order_counter += 1
    await state.clear()
    await callback.message.answer("תודה על ההזמנה! ניתן להתחיל הזמנה חדשה עם /start")

async def main():
    logging.info("🤖 הבוט מתחיל לפעול...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

