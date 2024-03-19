import logging
import telegram
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, CallbackQueryHandler
from telebot import types

# 导入之前定义的类
from read_sales import Sales
from read_warehousing import Warehousing_read
from read_inventory import Inventories
from read_customer import Customers

from datetime import datetime 
from user_handle_message import send_long_text, cancel, handle_input, reply_message
from helper import check_shipping_date
from user_get_button_menu import get_product_buttons

# Telegram Bot Token
TOKEN = '6487583852:AAGH3YlPRpfuOtLt-GlWvyI4Ss-B1lxOdtA'

# 实例化管理对象
sales_manager = Sales()
warehousing_manager = Warehousing_read()
inventory_manager = Inventories()
customers_manager = Customers()

ENTER_PRODUCT_NAME = range(1)

def add_product_name(update: Update, context: CallbackContext) -> str:
    message = '请输入产品名称：'
    reply_message(update, context, message, None)
    return ENTER_PRODUCT_NAME

def enter_product_name(update: Update, context: CallbackContext) -> str:
    product_name = update.message.text
    response_message = inventory_manager.add_or_update_product(product=product_name)
    update.message.reply_text(response_message)
    return ConversationHandler.END

# input all data 
(PRODUCT_NAME, MANUAL_PRODUCT_NAME, STOCK_IN, STOCK_OUT, SCHEDULE_INVENTORY, PRODUCT_CONFIRMATION) = range(6)

def start_add_or_update_product(update: Update, context: CallbackContext) -> None:
    reply_message(update, context, "本次需要输入多个数据，如果只想添加产品名称，可以通过/add_product_name", None)
    flag, reply_markup = get_product_buttons(update, context) 
    message = "请选择或输入产品名称，也可以发送 /cancel 或按取消，申请取消操作。"
    message += f"\n如果该产品已在库存，输入的数字为增加库存是‘10’则为在原有基础上增加10，输入增加库存为‘-10’则为在原有基础上减少10个。"
    message += f"\n\n如果该产品没有加入，则新添加到里面。"
    message += f"\n\n如果您想输入从供货商入货，可以先输入 /cancel ，再输入 /record_in ，表示添加入货记录。"
    message += f"\n\n如果只想添加产品名称，不想修改别的内容，可以输入或点击 /cancel , 再点击或输入 /add_product_name 。"
    message += f"\n\n可以直接点击蓝色字体跳转"
    # update.message.reply_text("请选择或输入产品名称，也可以发送 /cancel 或按取消，申请取消操作。", reply_markup=reply_markup)
    reply_message(update, context, message, reply_markup)
    return PRODUCT_NAME

def product_name(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    if query.data == 'cancel_input_product':
        return  cancel(update, context)
    elif query.data == "mannual_input_product":
        query.edit_message_text("请输入产品名称:")
        return MANUAL_PRODUCT_NAME 
    context.user_data['product'] = query.data
    message = "请输入入库总数量，如果不想修改请回复 NONE或none。"
    query.edit_message_text(message, reply_markup=None)
    context.bot.send_message(chat_id=query.message.chat_id, text=message)
    return STOCK_IN

def manual_input_product(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    context.user_data['product'] = text
    update.message.reply_text("请输入入库总数量，如果不想修改请回复 NONE或none。")
    return STOCK_IN

def stock_in(update: Update, context: CallbackContext) -> None:
    # update.message.reply_text("请输入入库总数量，如果不想修改请回复 NONE或none。")
    text = update.message.text
    context.user_data['stock_in'] = text if text.strip().lower() != "none" and text.strip() != "" else None
    if context.user_data['stock_in'] is not None: 
        try: 
            number = int(text) 
            if number < 0:
                raise ValueError 
        except ValueError:
            update.message.reply_text("请输入有效的正数作为单价:")
            return STOCK_IN

    update.message.reply_text("请输入出库总数量，如果不想修改请回复 NONE或none。")
    return STOCK_OUT

def stock_out(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    context.user_data['stock_out'] = text if text.strip().lower() != "none" and text.strip() != "" else None
    if context.user_data['stock_out'] is not None: 
        try: 
            number = int(text) 
            if number < 0:
                raise ValueError 
        except ValueError:
            update.message.reply_text("请输入有效的正数作为单价:")
            return STOCK_OUT
    update.message.reply_text("请输入预定总数量，如果不想修改请回复 NONE或none。")
    return SCHEDULE_INVENTORY

def schedule_inventory(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    context.user_data['schedule_inventory'] = text if text.strip().lower() != "none" and text.strip() != "" else None
    if context.user_data['schedule_inventory'] is not None: 
        try: 
            number = int(text) 
            if number < 0:
                raise ValueError 
        except ValueError:
            update.message.reply_text("请输入有效的正数作为单价:")
            return SCHEDULE_INVENTORY
    confirmation_text = "请确认您提供的信息：\n"
    confirmation_text += f"产品名称 : {context.user_data['product']}\n"
    confirmation_text += f"入库总数量 : {context.user_data['stock_in']}\n"
    confirmation_text += f"出库总数量 : {context.user_data['stock_out']}\n"
    confirmation_text += f"预定总数量 : {context.user_data['schedule_inventory']}\n"
    confirmation_text += f"确认请按 'yes'，重新输入请按 'no'。"
    # update.message.reply_text(confirmation_text + "确认请回复 'yes'，重新输入请回复 'no'。")
    # 确认信息
    keyboard = [
        [InlineKeyboardButton("确认", callback_data='confirm')],
        [InlineKeyboardButton("取消", callback_data='cancel')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(confirmation_text, reply_markup=reply_markup)
    return PRODUCT_CONFIRMATION

def perform_add_or_update(update, context):
    query = update.callback_query
    query.answer()
    message = ''
    if query.data == 'confirm':
        user_data = context.user_data
        product = handle_input(user_data.get('product'))
        stock_in = handle_input(user_data.get('stock_in'))
        stock_out = handle_input(user_data.get('stock_out'))
        schedule_inventory = handle_input(user_data.get('schedule_inventory'))
        message = inventory_manager.add_or_update_product(product=product, 
                                                        stock_in=stock_in, 
                                                        stock_out=stock_out, 
                                                        schedule_inventory=schedule_inventory, 
                                                        )
    elif query.data == 'cancel':
        message = '已取消删除操作。'
        
    user_data.clear()
    context.bot.send_message(chat_id=query.message.chat_id, text=message)
    return ConversationHandler.END