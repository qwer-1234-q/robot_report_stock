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
from user_handle_message import send_long_text, cancel, build_date_keyboard, build_menu
from helper import check_shipping_date

# Telegram Bot Token
TOKEN = '6487583852:AAGH3YlPRpfuOtLt-GlWvyI4Ss-B1lxOdtA'

# 实例化管理对象
sales_manager = Sales()
warehousing_manager = Warehousing_read()
inventory_manager = Inventories()
customers_manager = Customers()

RECORD_OUT_CUSTOMER, RECORD_OUT_PRODUCT, RECORD_OUT_SHIPPING_DATE, RECORD_OUT_STOCK_OUT, RECORD_OUT_UNIT_PRICE, RECORD_OUT_STAFF, RECORD_OUT_PAYMENT, RECORD_OUT_CONFIRMATION = range(8)
MANUAL_INPUT_CUSTOMER, MANUAL_SOLD_PRODUCT, MANUAL_SOLD_SHIPPING_DATE, MANUAL_SOLD_STAFF = range(4)

def start_record_out(update: Update, context: CallbackContext) -> int:
    customer_list = customers_manager.get_customer_name_list()  
    for name in sales_manager.get_customer_name_list():
        if name not in customer_list:
            customer_list.append(name)
    customer_list.sort()
    logging.info(f"customer list is {customer_list}")
    buttons = [InlineKeyboardButton(name, callback_data=name) for name in customer_list]
    # buttons.append(InlineKeyboardButton("手动输入", callback_data="mannual_input_customer"))
    reply_markup = InlineKeyboardMarkup(build_menu(buttons, 4))
    # message = '请选择或输入客户名字：\n（在选择了手动输入后，如果出现回复框，则需要你自己自主输入客户名字'
    message = '请选择或输入客户名字'
    update.message.reply_text(message, reply_markup=reply_markup)
    # context.bot.send_message(chat_id=update.message.chat_id, text=message)
    logging.info("start to add a sale record")
    return RECORD_OUT_CUSTOMER

def record_out_customer(update: Update, context: CallbackContext) -> int:
    # context.user_data['out_customer'] = update.message.text
    query = update.callback_query
    query.answer()
    if query.data == "mannual_input_customer":
        message = "请输入客户名："
        context.bot.send_message(chat_id=query.message.chat_id, text=message)
        # query.edit_message_text(message)        
        return MANUAL_INPUT_CUSTOMER
    context.user_data['out_customer'] = query.data    
    product_list = inventory_manager.get_product_list()
    if len(product_list) == 0:
        update.message.reply_text("当前库存中没有产品。")
        return ConversationHandler.END
    product_list.sort()
    keyboard = [InlineKeyboardButton(name, callback_data=name) for name in product_list]
    # keyboard.append(InlineKeyboardButton("手动输入", callback_data="mannual_input_product"))
    reply_markup = InlineKeyboardMarkup(build_menu(keyboard, 4))
    message = f"您选择的客户名是：{query.data}。\n请选择产品名称:"
    # context.bot.send_message(chat_id=query.message.chat_id, text=message)
    query.edit_message_text(message, reply_markup=reply_markup)
    return RECORD_OUT_PRODUCT

def manual_input_customer(update: Update, context: CallbackContext) -> int:
    customer_name = update.message.text
    context.user_data['out_customer'] = customer_name

    product_list = inventory_manager.get_product_list()
    if len(product_list) == 0:
        update.message.reply_text("当前库存中没有产品。")
        return ConversationHandler.END
    product_list.sort()
    keyboard = [InlineKeyboardButton(name, callback_data=name) for name in product_list]
    # keyboard.append(InlineKeyboardButton("手动输入", callback_data="mannual_input_product"))
    reply_markup = InlineKeyboardMarkup(build_menu(keyboard, 4))
    message = f"您输入的客户名是：{customer_name}。请输入产品信息："
    update.message.reply_text(message, reply_markup=reply_markup)
    # context.bot.send_message(chat_id=update.message.chat_id, text=message, reply_markup=reply_markup)
    return RECORD_OUT_PRODUCT

def record_out_product(update: Update, context: CallbackContext) -> int:
    # context.user_data['out_product'] = update.message.text
    query = update.callback_query
    query.answer()
    logging.info(f"record out product is {query.data}")
    # if str(query.data) in ["mannual_input_product"]:
    #     message = "请输入产品信息："
    #     # query.edit_message_text(message)
    #     context.bot.send_message(chat_id=query.message.chat_id, text=message)
    #     return MANUAL_SOLD_PRODUCT
    context.user_data['out_product'] = query.data
    today = datetime.now().strftime('%d/%m/%Y')
    context.user_data['out_shipping_date'] = today
    keyboard = [
        [InlineKeyboardButton("确认今日日期", callback_data='confirm_today')],
        [InlineKeyboardButton("输入新日期", callback_data='enter_custom')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = f"你输入的产品是 {context.user_data['out_product']} \n当前出货日期默认为今日：{today}。确认或更改？\nn（在选择了手动输入后，如果出现回复框，则需要你自己自主输入日期）"
    # message = f"你选择的产品是 {context.user_data['out_product']} \n请输入出货日期(格式DD/MM/YYYY):"
    context.bot.send_message(chat_id=query.message.chat_id, text=message)
    query.edit_message_text(text=message, reply_markup=reply_markup)
    return RECORD_OUT_SHIPPING_DATE

def manual_sold_product(update: Update, context: CallbackContext) -> int:
    context.user_data['out_product'] = update.message.text
    today = datetime.now().strftime('%d/%m/%Y')
    context.user_data['out_shipping_date'] = today
    keyboard = [
        [InlineKeyboardButton("确认今日日期", callback_data='confirm_today')],
        [InlineKeyboardButton("输入新日期", callback_data='enter_custom')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = f"你输入的产品是 {context.user_data['out_product']} \n当前出货日期默认为今日：{today}。确认或更改？"
    # context.bot.send_message(chat_id=update.message.chat_id, text=message, reply_markup=reply_markup)
    update.message.reply_text(message, reply_markup=reply_markup)
    return RECORD_OUT_SHIPPING_DATE

def manual_sold_shipping_date(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    logging.info(f"sold manual")
    try:
        # Attempt to convert the text input into a datetime object
        # custom_date = datetime.strptime(text, '%d/%m/%Y')
        flag, custom_date = check_shipping_date(text)
        if flag:
            context.user_data['out_shipping_date'] = custom_date
            message = f"已确认出货日期：{context.user_data['out_shipping_date']}\n请输入出库数量:"
            update.message.reply_text(message)
            context.bot.send_message(chat_id=update.message.chat_id, text=message)
            return RECORD_OUT_STOCK_OUT
        else: 
            raise ValueError 
    except ValueError:
        # If the date format is incorrect, prompt the user to try again
        update.message.reply_text("日期格式不正确，请使用DD/MM/YYYY格式重新输入：")
        return MANUAL_SOLD_SHIPPING_DATE

def record_out_shipping_date(update: Update, context: CallbackContext) -> int:
    # context.user_data['out_shipping_date'] = update.message.text
    query = update.callback_query
    query.answer()

    logging.info(f"sold confirm or change date")
    if query.data == 'enter_custom':
        message = f"请输入出货日期(格式DD/MM/YYYY):"
        query.edit_message_text(text=message)
        context.bot.send_message(chat_id=query.message.chat_id, text=message)
        return MANUAL_SOLD_SHIPPING_DATE
    # else:
    # update.message.reply_text('请输入出库数量:')
    message = f"已确认出货日期：{context.user_data['out_shipping_date']}\n请输入出库数量："
    query.edit_message_text(text=message)
    context.bot.send_message(chat_id=query.message.chat_id, text=message)
    return RECORD_OUT_STOCK_OUT

def record_out_stock_out(update: Update, context: CallbackContext) -> int:
    try:
        number = int(update.message.text)
        if number < 0:
            raise ValueError 
        context.user_data['out_stock_out'] = int(update.message.text)
        update.message.reply_text('请输入单价:')
        return RECORD_OUT_UNIT_PRICE
    except ValueError:
        update.message.reply_text("请输入有效的正数作为出库数量:")
        return RECORD_OUT_STOCK_OUT
    

def record_out_unit_price(update: Update, context: CallbackContext) -> int:
    try: 
        number = float(update.message.text)
        if number < 0:
            raise ValueError
        context.user_data['out_unit_price'] = float(update.message.text)
        message = '请输入销售员:'
        staff_list = sales_manager.get_staff_name_list() 
        buttons = [InlineKeyboardButton(staff, callback_data=staff) for staff in staff_list]
        # buttons.append(InlineKeyboardButton("手动输入销售员名字", callback_data="manual_staff"))
        reply_markup = InlineKeyboardMarkup(build_menu(buttons, 2))
        update.message.reply_text(message, reply_markup=reply_markup)
        return RECORD_OUT_STAFF
    except ValueError:
        update.message.reply_text("请输入有效的正数作为单价:")
        return RECORD_OUT_UNIT_PRICE

def record_out_staff(update: Update, context: CallbackContext) -> int:
    # context.user_data['out_staff'] = update.message.text
    # update.message.reply_text('请输入款项:')
    query = update.callback_query
    query.answer()
    context.user_data['out_staff'] = query.data 
    # if context.user_data['out_staff'] == "manual_staff":
    #     message = "请输入销售员名字"
    #     context.bot.send_message(chat_id=query.message.chat_id, text=message)
    #     return MANUAL_SOLD_STAFF
    message = f"{context.user_data['out_staff']} 销售员 \n请输入款项:"
    context.bot.send_message(chat_id=query.message.chat_id, text=message)
    return RECORD_OUT_PAYMENT

def manual_input_staff(update: Update, context: CallbackContext) -> int:
    selected_staff = update.message.text
    logging.info(f"manual input staff {selected_staff}")
    context.user_data['sale_staff'] = selected_staff
    update.message.reply_text(text=f"已输入销售员：{selected_staff}\n请输入款项：")
    return RECORD_OUT_PAYMENT

def record_out_payment(update: Update, context: CallbackContext) -> int:
    try:
        number = float(update.message.text)
        if number < 0:
            raise ValueError
        context.user_data['out_payment'] = float(update.message.text)
        update.message.reply_text('感谢您的输入，正在处理...')
        response = sales_manager.add_sale(
            customer=context.user_data['out_customer'], 
            product=context.user_data['out_product'], 
            shipping_date=context.user_data['out_shipping_date'], 
            stock_out=context.user_data['out_stock_out'], 
            unit_price=context.user_data['out_unit_price'], 
            staff=context.user_data['out_staff'], 
            payment=context.user_data['out_payment']
        )
        context.bot.send_message(chat_id=update.message.chat_id, text=response)
        update.message.reply_text(response) 
        return ConversationHandler.END
    except ValueError:
        update.message.reply_text("请输入有效的正数作为单价:")
        return RECORD_OUT_PAYMENT
    
# 生成确认信息的辅助函数
def generate_new_sale_confirmation_message(user_data):
    message = "请确认以下信息：\n"
    sale_customer = user_data.get('sale_customer', '未提供')  # 使用get方法，如果键不存在，返回'未提供'
    sale_product = user_data.get('sale_product', '未提供')
    sale_shipping_date = user_data.get('sale_shipping_date', '未提供')
    sale_stock_out = user_data.get('sale_stock_out', '未提供')
    sale_unit_price = user_data.get('sale_unit_price', '未提供')
    sale_staff = user_data.get('sale_staff', '未提供')
    sale_payment = user_data.get('sale_payment', '未提供')

    message += f"客户名：{sale_customer}\n产品名称：{sale_product}\n"
    message += f"出货日期：{sale_shipping_date}\n出库数量：{sale_stock_out}\n"
    message += f"单价：{sale_unit_price}\n销售员：{sale_staff}\n款项：{sale_payment}\n"
    message += "\n请回复 'yes' 确认，回复 'no' 重新输入。"
    return message