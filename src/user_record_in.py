import telegram
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, CallbackQueryHandler
import logging

# 导入之前定义的类
from read_sales import Sales
from read_warehousing import Warehousing_read
from read_inventory import Inventories
from read_customer import Customers

from datetime import datetime 

### the message handle features from other files
from user_handle_message import cancel, reply_message
from helper import check_shipping_date

from user_get_button_menu import get_product_buttons, get_supplier_buttons, build_date_keyboard

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 实例化管理对象
sales_manager = Sales()
warehousing_manager = Warehousing_read()
inventory_manager = Inventories()
customers_manager = Customers()

RECORD_IN_ARRIVAL_DATE, RECORD_IN_SUPPLIER, RECORD_IN_PRODUCT, RECORD_IN_STOCK_IN, RECORD_IN_UNIT_PRICE = range(5)
MANUAL_RECORD_IN_ARRIVAL_DATE = range(1)

def arrival_date_message(date):
    return f"入货日期为：{date} \n请选择供应商名称:\n（如果没有显示，证明系统没有搜索到供应商，需要到 /add_supplier 添加）"

def start_add_warehousing(update: Update, context: CallbackContext) -> int:
    today = datetime.now().strftime('%d/%m/%Y')
    context.user_data['record_in_arrival_date'] = today
    reply_markup = build_date_keyboard()
    message = f"当前出货日期默认为今日：{today}。确认或更改？"
    # context.bot.send_message(chat_id=update.message.chat_id, text=message, reply_markup=reply_markup)
    # update.message.reply_text(message, reply_markup=reply_markup)
    reply_message(update, context, message, reply_markup)
    logging.info(f"{today} is today")
    return RECORD_IN_ARRIVAL_DATE

def record_in_arrival_date(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_input = query.data
    logging.info(f"[{user_input}] in the record in arrival date {str(user_input).startswith('enter')}")
    if str(user_input).startswith('enter'):
        logging.info("here we input the date")
        message = f"请输入出货日期(格式DD/MM/YYYY):"
        context.bot.send_message(chat_id=query.message.chat_id, text=message)
        return MANUAL_RECORD_IN_ARRIVAL_DATE

    logging.info("here we input the supplier")
    today = datetime.now().strftime('%d/%m/%Y')
    # context.bot.send_message(chat_id=query.message.chat_id, text=message)
    # query.edit_message_text(text=arrival_date_message(today), reply_markup=get_supplier_buttons(update, context, manual_input=False, cancel=False))
    flag, suppliers = get_supplier_buttons(update, context, manual_input=False, cancel=False)
    reply_message(update, context, arrival_date_message(today), suppliers)
    return RECORD_IN_SUPPLIER

def manual_record_in_shipping_date(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    logging.info(f"record in date manual")
    flag, suppliers = get_supplier_buttons(update, context, manual_input=False, cancel=False)
    if text.startswith('confirm'):
        update.message.reply_text(arrival_date_message(context.user_data['record_in_arrival_date']), reply_markup=suppliers)
        # reply_message(update, context, arrival_date_message(today), get_supplier_buttons(update, context, manual_input=False, cancel=False))
        return RECORD_IN_SUPPLIER
    try:
        # Attempt to convert the text input into a datetime object
        flag, custom_date = check_shipping_date(text)
        logging.info(f"we input the date is {custom_date}")
        if flag:
            context.user_data['record_in_arrival_date'] = custom_date
            message = f"已确认入货日期：{context.user_data['record_in_arrival_date']}\n请选择供应商名称:\n（如果没有显示，证明系统没有搜索到供应商，需要到/add_supplier添加）"
            context.bot.send_message(chat_id=update.message.chat_id, text=message)
            update.message.reply_text(message, reply_markup=suppliers)
            return RECORD_IN_SUPPLIER
        else: 
            raise ValueError 
    except ValueError:
        # If the date format is incorrect, prompt the user to try again
        update.message.reply_text("日期格式不正确，请使用DD/MM/YYYY格式重新输入：")
        return MANUAL_RECORD_IN_ARRIVAL_DATE

def record_in_supplier(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    user_input = query.data
    context.user_data['record_in_supplier'] = ''
    logging.info(f"[{user_input}] in the record in supplier {str(user_input).startswith('manual_input_')}")
    context.user_data['record_in_supplier'] = user_input
    message = f"供应商名称: {user_input}\n请选择产品:"
    context.bot.send_message(chat_id=query.message.chat_id, text=message)
    flag, reply_markup = get_product_buttons(update, context, False, False) 
    if flag is False:
        return cancel(update, context)
    query.edit_message_text(text=message, reply_markup=reply_markup)    
    return RECORD_IN_PRODUCT

def record_in_product(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    user_input = query.data
    logging.info(f"[{user_input}] in the record in product {str(user_input).startswith('manual_input_')}")
    context.user_data['record_in_product'] = user_input
    message = f"产品名称: {user_input}\n请输入入库数量:"
    context.bot.send_message(chat_id=query.message.chat_id, text=message)
    query.edit_message_text(text=message)    
    return RECORD_IN_STOCK_IN

def record_in_stock_in(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text
    context.user_data['record_in_stock_in'] = user_input
    update.message.reply_text('请输入单价:')
    return RECORD_IN_UNIT_PRICE

def record_in_unit_price(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text
    context.user_data['record_in_unit_price'] = user_input
    result = warehousing_manager.add_warehousing_record(
        arrival_date=context.user_data['record_in_arrival_date'] , 
        supplier=context.user_data['record_in_supplier'], 
        product=context.user_data['record_in_product'], 
        stock_in=context.user_data['record_in_stock_in'], 
        unit_price=context.user_data['record_in_unit_price'] )
    update.message.reply_text(f"{result}", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

ADD_SUPPLIER = range(1)

def start_add_supplier(update: Update, context: CallbackContext) -> int:
    # update.message.reply_text("请输入供应商名称:")
    reply_message(update, context, "请输入供应商名称:", None)
    return ADD_SUPPLIER

def add_supplier(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    logging.info(f"add supplier {text}")
    result = warehousing_manager.add_supplier(text)
    if result:
        message = f"{text} 供应商已经成功加入"
    else: 
        message = f"{text} 供应商已在系统中"
    context.bot.send_message(chat_id=update.message.chat_id, text=message)
    return ConversationHandler.END

