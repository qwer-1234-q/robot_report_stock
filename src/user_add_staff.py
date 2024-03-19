import logging
import telegram
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, CallbackQueryHandler
from telebot import types

# 导入之前定义的类
from read_sales import Sales

from datetime import datetime 

from user_handle_message import send_long_text, cancel, reply_message

# Telegram Bot Token
TOKEN = '6487583852:AAGH3YlPRpfuOtLt-GlWvyI4Ss-B1lxOdtA'

# 实例化管理对象
sales_manager = Sales()

ADD_STAFF = range(1)

def add_staff_start(update: Update, context: CallbackContext) -> None:
    message = '请输入销售员名字'
    reply_message(update, context, message, None)
    return ADD_STAFF

def add_staff_command(update: Update, context: CallbackContext) -> None:
    staff_name = update.message.text 
    if sales_manager.add_staff(staff_name):
        update.message.reply_text(f'员工 "{staff_name}" 已成功添加。')
    else:
        update.message.reply_text(f'员工 "{staff_name}" 已存在或无效。')
    return ConversationHandler.END
