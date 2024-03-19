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
from user_handle_message import send_long_text, cancel, handle_input
from user_handle_message import reply_message

from user_get_button_menu import get_customer_buttons

# Telegram Bot Token
TOKEN = '6487583852:AAGH3YlPRpfuOtLt-GlWvyI4Ss-B1lxOdtA'

# 实例化管理对象
sales_manager = Sales()
warehousing_manager = Warehousing_read()
inventory_manager = Inventories()
customers_manager = Customers()

CUSTOMER_NAME, CUSTOMER_PAYABLE, CUSTOMER_PAYMENT, CUSTOMER_COMFIRMATION = range(4)
HANDLE_MANUAL_NEW_CUSTOMER_INPUT = range(1)

def customer_add(update: Update, context: CallbackContext) -> int:
    flag, reply_markup = get_customer_buttons(update, context, manual_input=True, cancel=True)
    # update.message.reply_text('请选择或输入客户名字：', reply_markup=reply_markup)
    reply_message(update, context, '请选择或输入客户名字：', reply_markup)
    return CUSTOMER_NAME

def customer_name(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    
    selected_customer = query.data
    if selected_customer in ["mannual_input_customer"]:
        query.edit_message_text(text="请输入客户名字：")
        return HANDLE_MANUAL_NEW_CUSTOMER_INPUT
    elif selected_customer in ["cancel_input_customer"]:
        return cancel(update, context)
    context.user_data['customer_name'] = selected_customer
    message = '请输入应付金额:'
    query.edit_message_text(text=message)
    context.bot.send_message(chat_id=query.message.chat_id, text=message)
    return CUSTOMER_PAYABLE

def handle_manual_new_customer_input(update: Update, context: CallbackContext) -> int:
    context.user_data['customer_name'] = update.message.text
    update.message.reply_text('请输入应付金额:')
    return CUSTOMER_PAYABLE

def customer_payable(update: Update, context: CallbackContext) -> int:
    payable = update.message.text
    try:
        price = float(payable)
        if price >= 0:
            context.user_data['customer_payable'] = payable
            update.message.reply_text('请输入实付金额:')
            return CUSTOMER_PAYMENT
        else: 
            raise ValueError
    except ValueError:
        update.message.reply_text("请输入有效的正数作为单价:")
        update.message.reply_text('应付金额必须为数字，请重新输入:')
        return CUSTOMER_PAYABLE

def customer_payment(update: Update, context: CallbackContext) -> int:
    payment = update.message.text
    try:
        price = float(payment)
        if price >= 0:
            context.user_data['customer_payment'] = payment
            confirm_new_customer_information(update, context)
            return CUSTOMER_COMFIRMATION
        else: 
            raise ValueError
    except ValueError:
        update.message.reply_text("请输入有效的正数作为单价:")
        update.message.reply_text('实付金额必须为数字，请重新输入:')
        return CUSTOMER_PAYMENT

def confirm_new_customer_information(update, context):
    keyboard = [
        [InlineKeyboardButton("确认", callback_data='confirm')],
        [InlineKeyboardButton("重新输入", callback_data='reenter')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    confirmation_message = generate_customer_confirmation_message(context.user_data)
    update.message.reply_text(confirmation_message, reply_markup=reply_markup)

def generate_customer_confirmation_message(user_data):
    return (
        f"请确认以下信息：\n"
        f"客户名：{user_data['customer_name']}\n"
        f"应付金额：{user_data['customer_payable']}\n"
        f"实付金额：{user_data['customer_payment']}\n"
        f"\n请选择确认或重新输入。"
    )

# 确认信息处理
def customer_confirmation(update: Update, context: CallbackContext) -> str:
    query = update.callback_query
    query.answer()
    if query.data == 'confirm':
        name = handle_input(context.user_data['customer_name'])
        payable = handle_input(context.user_data['customer_payable'])
        payment = handle_input(context.user_data['customer_payment'])
        customer_msg = customers_manager.add_or_update_customer(
            customer_name=name, payable=payable, payment=payment
        )
        query.edit_message_text(text=customer_msg)
    elif query.data == 'reenter':
        query.edit_message_text(text='请输入客户名:')
        return CUSTOMER_NAME
    return ConversationHandler.END