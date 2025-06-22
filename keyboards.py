from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_start_keyboard():
    """
    יוצר מקלדת עם כפתור התחלת הזמנה.
    
    Returns:
        InlineKeyboardMarkup: מקלדת עם כפתור התחלה
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ התחל הזמנה", callback_data="start_order")]
    ])
    return keyboard

def get_back_keyboard():
    """
    יוצר מקלדת עם כפתור חזרה.
    
    Returns:
        InlineKeyboardMarkup: מקלדת עם כפתור חזרה
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅ חזור", callback_data="back")]
    ])
    return keyboard

def get_add_product_keyboard():
    """
    יוצר מקלדת עם אפשרויות הוספת מוצר, המשך לתשלום וחזרה.
    
    Returns:
        InlineKeyboardMarkup: מקלדת עם אפשרויות מוצר
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ הוסף מוצר נוסף", callback_data="add_product")],
        [InlineKeyboardButton(text="➡️ המשך לתשלום", callback_data="continue_payment")],
        [InlineKeyboardButton(text="⬅ חזור", callback_data="back")]
    ])
    return keyboard

def get_summary_keyboard():
    """
    יוצר מקלדת עם אפשרויות אישור, עריכה וביטול הזמנה.
    
    Returns:
        InlineKeyboardMarkup: מקלדת עם אפשרויות סיכום
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ אישור", callback_data="confirm_order")],
        [InlineKeyboardButton(text="✏️ עריכת הזמנה", callback_data="edit_order")],
        [InlineKeyboardButton(text="❌ ביטול", callback_data="cancel_order")]
    ])
    return keyboard

def get_product_selection_keyboard(products):
    """
    יוצר מקלדת לבחירת מוצר לעריכה.
    
    Args:
        products: רשימת המוצרים
    
    Returns:
        InlineKeyboardMarkup: מקלדת עם רשימת המוצרים
    """
    keyboard = []
    for i, product in enumerate(products):
        keyboard.append([InlineKeyboardButton(
            text=f"{product['type']} - {product['quantity']:,} יח'", 
            callback_data=f"select_product_{i}"
        )])
    keyboard.append([InlineKeyboardButton(text="⬅ חזור לסיכום", callback_data="back_to_summary")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_edit_action_keyboard():
    """
    יוצר מקלדת לבחירת פעולת עריכה.
    
    Returns:
        InlineKeyboardMarkup: מקלדת עם אפשרויות עריכה ומחיקה
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ ערוך מוצר", callback_data="edit_product")],
        [InlineKeyboardButton(text="🗑️ מחק מוצר", callback_data="delete_product")],
        [InlineKeyboardButton(text="⬅ חזור", callback_data="back_to_product_selection")]
    ])
    return keyboard

def get_back_and_continue_keyboard():
    """
    יוצר מקלדת עם אפשרויות המשך וחזרה.
    
    Returns:
        InlineKeyboardMarkup: מקלדת עם אפשרויות המשך וחזרה
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➡️ המשך", callback_data="continue")],
        [InlineKeyboardButton(text="⬅ חזור", callback_data="back")]
    ])
    return keyboard