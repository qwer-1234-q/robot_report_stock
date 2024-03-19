import telegram
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, CallbackQueryHandler
import logging

# 导入之前定义的类
from read_sales import Sales
from read_warehousing import Warehousing_read
from read_inventory import Inventories
from read_customer import Customers
from helper import check_shipping_date

from datetime import datetime 
from user_handle_message import send_long_text, cancel, build_menu, reply_message
from user_handle_message import reply_long_message

# 实例化管理对象
sales_manager = Sales()
warehousing_manager = Warehousing_read()
inventory_manager = Inventories()
customers_manager = Customers()

def build_date_keyboard():
    keyboard = [
        # Button for selecting today's date directly
        [InlineKeyboardButton(text="选择今日日期", callback_data='choose_today')],
        # Button for prompting the user to enter a custom date
        [InlineKeyboardButton(text="输入自定义日期", callback_data='enter_custom_date')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_product_buttons(update, context, manual_input=True, cancel=True):
    product_list = inventory_manager.get_product_list()
    if len(product_list) == 0:        
        message="当前库存中没有产品。"
        reply_message(update, context, message, reply_markup)
        return False, []
    product_list.sort()
    keyboard = [InlineKeyboardButton(name, callback_data=name) for name in product_list]
    if manual_input:
        keyboard.append(InlineKeyboardButton("手动输入", callback_data="mannual_input_product"))
    if cancel:
        keyboard.append(InlineKeyboardButton("取消", callback_data="cancel_input_product"))
    reply_markup = InlineKeyboardMarkup(build_menu(keyboard, 4))
    return True, reply_markup

def get_customer_buttons(update, context, manual_input=True, cancel=True):
    customer_list = customers_manager.get_customer_name_list()  
    for name in sales_manager.get_customer_name_list():
        if name not in customer_list:
            customer_list.append(name)
    if len(customer_list) == 0:
        reply_message(update, context, '销售记录中没有记录任何客户名', None)
        return False, []
    customer_list.sort()
    logging.info(f"customer list is {customer_list}")
    buttons = [InlineKeyboardButton(name, callback_data=name) for name in customer_list]
    if manual_input:
        buttons.append(InlineKeyboardButton("手动输入", callback_data="mannual_input_customer"))
    if cancel:
        buttons.append(InlineKeyboardButton("取消", callback_data="cancel_input_customer"))
    reply_markup = InlineKeyboardMarkup(build_menu(buttons, 4))
    return True, reply_markup

def get_supplier_buttons(update, context, manual_input=True, cancel=True):
    flag, suppliers = warehousing_manager.get_supplier_list() 
    buttons = []
    if flag:
        buttons = [InlineKeyboardButton(supplier, callback_data=supplier) for supplier in suppliers]        
    else: 
        message = "库存表中没有供应商名称，且库存表中无数据。"
        reply_message(update, context, message, None)
    if manual_input:
        buttons.append(InlineKeyboardButton("手动输入", callback_data="manual_input_supplier"))
    if cancel:
        buttons.append(InlineKeyboardButton("取消", callback_data="cancel_input_supplier"))
    keyboard = InlineKeyboardMarkup(build_menu(buttons, n_cols=4)) 
    return flag, keyboard