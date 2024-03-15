import telegram
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, CallbackQueryHandler
import json
import os 
import telebot
import requests
import logging 
import warnings

# 导入之前定义的类
from read_sales import Sales
from read_warehousing import Warehousing_read
from read_inventory import Inventories
from read_customer import Customers

from datetime import datetime 

### the message handle features from other files
from user_handle_message import start, send_long_text, cancel, build_date_keyboard, build_menu, help

# Telegram Bot Token
TOKEN = '6487583852:AAGH3YlPRpfuOtLt-GlWvyI4Ss-B1lxOdtA'

# Telegram 
website = 'https://web.telegram.org/a/#6487583852'

# 实例化管理对象
sales_manager = Sales()
warehousing_manager = Warehousing_read()
inventory_manager = Inventories()
customers_manager = Customers()

logging.basicConfig(
    filename='bot.log',  # 日志文件名
    filemode='a',  # 追加模式
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 日志格式
    level=logging.INFO  # 记录所有级别大于等于INFO的日志
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

warnings.filterwarnings("ignore", message="If 'per_message=False'")
"""
###################################################################################
                            Sales records 销售记录表
###################################################################################
"""
# record out functions 
from user_record_out import sale_start, manual_input_customer, sale_customer, sale_product
from user_record_out import sale_confirm_or_change_date, sale_enter_custom_date, sale_seller
from user_record_out import sale_stock_out, sale_unit_price, sale_payment, sale_confirmation

from user_record_out import (SALE_CUSTOMER, MANUAL_INPUT_CUSTOMER, SALE_CONFIRM_DATE, 
                             SALE_ENTER_CUSTOM_DATE, SALE_PRODUCT, SALE_STOCK_OUT, 
                             SALE_UNIT_PRICE, SALE_SELLER, SALE_PAYMENT, SALE_CONFIRMATION,
                             )

# all sales records
from user_all_records import (sale_get_all, find_sale_by_id, start_find_sale, 
                            start_find_sale_by_customer_name, handle_customer_selection, handle_manual_find_customer_input)
from user_all_records import (SALE_FIND, SALE_FIND_CUSTOMER, HANDLE_MANUAL_FIND_CUSTOMER_INPUT)

# Delete a record
from user_delete import (start_delete_sale, delete_sale)
from user_delete import (SALE_DELETE)

"""
###################################################################################
                            Customer 客户记录表
###################################################################################
"""
# Get the excess payment and debt
from user_all_records import get_customers_with_excess_payment_handler, get_customers_with_debt

# Get all customers' details
from user_all_records import get_all_customers

# Delete the customer and his/her payment details 
from user_delete import (CUSTOMER_DELETE_NAME, CUSTOMER_DELETE_CONFIRMATION)
from user_delete import (customer_delete_start, customer_delete_name, delete_customer_confirmation)

CUSTOMER_NAME, CUSTOMER_PAYABLE, CUSTOMER_PAYMENT, CUSTOMER_COMFIRMATION = range(4)

def customer_add(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('请输入客户名:')
    return CUSTOMER_NAME

def customer_name(update: Update, context: CallbackContext) -> int:
    context.user_data['customer_name'] = update.message.text
    update.message.reply_text('请输入应付金额:')
    return CUSTOMER_PAYABLE

def customer_payable(update: Update, context: CallbackContext) -> int:
    payable = update.message.text
    if not payable.replace('.', '', 1).isdigit():
        update.message.reply_text('应付金额必须为数字，请重新输入:')
        return CUSTOMER_PAYABLE
    context.user_data['customer_payable'] = payable
    update.message.reply_text('请输入实付金额:')
    return CUSTOMER_PAYMENT

def customer_payment(update: Update, context: CallbackContext) -> int:
    payment = update.message.text
    if not payment.replace('.', '', 1).isdigit():
        update.message.reply_text('实付金额必须为数字，请重新输入:')
        return CUSTOMER_PAYMENT
    context.user_data['customer_payment'] = payment
    confirm_new_customer_information(update, context)
    return CUSTOMER_COMFIRMATION

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
        customer_msg = customers_manager.add_customer(
            customer_name=context.user_data['customer_name'], 
            payable=context.user_data['customer_payable'],
            payment=context.user_data['customer_payment']
        )
        query.edit_message_text(text=customer_msg)
    elif query.data == 'reenter':
        query.edit_message_text(text='请输入客户名:')
        return CUSTOMER_NAME

# Define states for the conversation
UPDATE_CUSTOMER_NAME, UPDATE_PAYABLE, UPDATE_PAYMENT, UPDATE_CONFIRMATION = range(4)

def update_payment_start(update: Update, context: CallbackContext) -> int:
    customer_list = customers_manager.get_customer_name_list()  # 假设有这个方法返回客户名列表
    keyboard = [[InlineKeyboardButton(customer, callback_data=customer)] for customer in customer_list]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('请选择客户名：', reply_markup=reply_markup)
    return UPDATE_CUSTOMER_NAME

def update_payment_customer_name(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    context.user_data['update_customer_name'] = query.data
    query.edit_message_text(text='请输入现在需要再支付应付金额（必须为数字）：')
    return UPDATE_PAYABLE

def update_payment_payable(update: Update, context: CallbackContext) -> int:
    payable = update.message.text
    if not payable.replace('.', '', 1).isdigit():
        update.message.reply_text('应付金额必须为数字，请重新输入：')
        return UPDATE_PAYABLE
    context.user_data['update_payable'] = payable
    update.message.reply_text('请输入现在客户已支付金额（必须为数字）：')
    return UPDATE_PAYMENT

def update_payment(update: Update, context: CallbackContext) -> int:
    payment = update.message.text
    if not payment.replace('.', '', 1).isdigit():
        update.message.reply_text('支付金额必须为数字，请重新输入：')
        return UPDATE_PAYMENT
    context.user_data['update_payment'] = payment
    confirm_update_customer_information(update, context)
    return UPDATE_CONFIRMATION

def confirm_update_customer_information(update, context):
    keyboard = [
        [InlineKeyboardButton("确认", callback_data='confirm')],
        [InlineKeyboardButton("重新输入", callback_data='reenter')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    confirmation_message = generate_update_customer_confirmation_message(context.user_data)
    update.message.reply_text(confirmation_message, reply_markup=reply_markup)

def generate_update_customer_confirmation_message(user_data):
    return (
        f"请确认以下信息：\n"
        f"客户名：{user_data['update_customer_name']}\n"
        f"应付金额：{user_data['update_payable']}\n"
        f"新的支付金额：{user_data['update_payment']}\n"
        f"请通过点击按钮确认或重新输入。"
    )

def update_payment_confirmation(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    if query.data == 'confirm':
        response = customers_manager.update_customer_payment(
            context.user_data['update_customer_name'], 
            context.user_data['update_payable'], 
            context.user_data['update_payment']
        )
        query.edit_message_text(text=response)
        return ConversationHandler.END
    elif query.data == 'reenter':
        update_payment_start(update, context)
    


"""
###################################################################################
                                Inventory 库存登记
###################################################################################
"""
# List all product information
from user_all_records import list_all_products

# List the product
from user_all_records import PRODUCT_QUERY
from user_all_records import start_get_product_data, product_query

# delete the product  
from user_delete import DELETE_PRODUCT, start_delete_product, delete_product

ENTER_PRODUCT_NAME = range(1)

def add_product_name(update: Update, context: CallbackContext) -> str:
    """开始添加或更新产品的对话"""
    update.message.reply_text('请输入产品名称：')
    return ENTER_PRODUCT_NAME

def enter_product_name(update: Update, context: CallbackContext) -> str:
    """接收产品名称并处理"""
    product_name = update.message.text
    response_message = inventory_manager.add_or_update_product(product=product_name)
    update.message.reply_text(response_message)
    return ConversationHandler.END

# 定义状态常量
(PRODUCT_NAME, OPENING_INVENTORY, STOCK_IN, STOCK_OUT, SCHEDULE_INVENTORY, TOTAL_INVENTORY, IN_STOCK, PRODUCT_CONFIRMATION) = range(8)

def start_add_or_update_product(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("本次需要输入多个数据，如果只想添加产品名称，可以通过/add_product_name")
    update.message.reply_text("请输入产品名称，或者发送 /cancel 取消操作。")
    return PRODUCT_NAME

def product_name(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    context.user_data['product'] = text
    update.message.reply_text("请输入初始库存数量，如果不想修改请回复 NONE 或留空。")
    return OPENING_INVENTORY

def opening_inventory(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    context.user_data['opening_inventory'] = text if text.strip().lower() != "none" and text.strip() != "" else None
    update.message.reply_text("请输入入库总数量，如果不想修改请回复 NONE 或留空。")
    return STOCK_IN

def stock_in(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    context.user_data['stock_in'] = text if text.strip().lower() != "none" and text.strip() != "" else None
    update.message.reply_text("请输入出库总数量，如果不想修改请回复 NONE 或留空。")
    return STOCK_OUT

def stock_out(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    context.user_data['stock_out'] = text if text.strip().lower() != "none" and text.strip() != "" else None
    update.message.reply_text("请输入预定总数量，如果不想修改请回复 NONE 或留空。")
    return SCHEDULE_INVENTORY

def schedule_inventory(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    context.user_data['schedule_inventory'] = text if text.strip().lower() != "none" and text.strip() != "" else None
    update.message.reply_text("请输入库存总数量，如果不想修改请回复 NONE 或留空。")
    return TOTAL_INVENTORY

def total_inventory(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    context.user_data['total_inventory'] = text if text.strip().lower() != "none" and text.strip() != "" else None
    update.message.reply_text("请输入可用库存，如果不想修改请回复 NONE 或留空。")
    return IN_STOCK

def in_stock(update, context):
    text = update.message.text
    context.user_data['in_stock'] = text if text.strip().lower() != "none" and text.strip() != "" else None
    confirmation_text = "请确认您提供的信息：\n"
    for key, value in context.user_data.items():
        confirmation_text += f"{key}: {value}\n"
    update.message.reply_text(confirmation_text + "确认请回复 'yes'，重新输入请回复 'no'。")
    return PRODUCT_CONFIRMATION

def perform_add_or_update(update, context):
    user_data = context.user_data
    product = user_data.get('product')
    opening_inventory = user_data.get('opening_inventory')
    stock_in = user_data.get('stock_in')
    stock_out = user_data.get('stock_out')
    schedule_inventory = user_data.get('schedule_inventory')
    total_inventory = user_data.get('total_inventory')
    in_stock = user_data.get('in_stock')
    message = inventory_manager.add_or_update_product(product=product, opening_inventory=opening_inventory, 
                                                      stock_in=stock_in, stock_out=stock_out, schedule_inventory=schedule_inventory, 
                                                      total_inventory=total_inventory, in_stock=in_stock)
    update.message.reply_text(message)  
    user_data.clear()
    return ConversationHandler.END

"""
###################################################################################
                                Warehousing 入货记录
###################################################################################
"""
# record in functions
from user_record_in import (confirm_warehousing, start_add_warehousing, arrival_date,
                            manual_input_supplier,  warehousing_stock_in,
                            warehousing_unit_price, choose_supplier_method, 
                            manual_input_product, manual_input_arrival_date)
from user_record_in import (WAREHOUSING_ARRIVAL_DATE, WAREHOUSING_SUPPLIER, SUPPLIER_PRODUCT, 
                            WAREHOUSING_STOCK_IN, WAREHOUSING_UNIT_PRICE, WAREHOUSING_TOTAL_PRICE, 
                            SUPPLIER_CONFIRMATION, CHOOSE_SUPPLIER_METHOD, MANUAL_INPUT_SUPPLIER, 
                            SUPPLIER_PRODUCT, CHOOSE_PRODUCT_METHOD, MANUAL_INPUT_PRODUCT, 
                            WAREHOUSING_STOCK_IN, MANUAL_INPUT_ARRIVAL_DATE)

# get the warehousing data 
from user_all_records import FIND_BY_DATE, MANUAL_FIND_WAREHOUSING_DATE 
from user_all_records import start_find_by_date, find_by_date, manual_find_warehousing_date, get_all_warehousing

# delete a warehousing data
from user_delete import (DELETE_ARRIVAL_DATE, DELETE_SUPPLIER, DELETE_PRODUCT, MANUAL_DELETE_WAREHOUSING_DATE, DELETE_SUPPLIER_CONFIRMATION)
from user_delete import (start_delete_warehousing, delete_warehousing_arrival_date, manual_delete_warehousing_date,
                         delete_warehousing_supplier, delete_warehousing_product, delete_warehousing_confirmation)

UPDATE_ARRIVAL_DATE, UPDATE_SUPPLIER, UPDATE_PRODUCT, UPDATE_NEW_QUANTITY, UPDATE_NEW_UNIT_PRICE, UPDATE_SUPPLIER_CONFIRMATION = range(6)

# 开始更新记录的处理函数
def start_update_warehousing(update, context):
    update.message.reply_text("请选择到货日期:", reply_markup=build_date_keyboard())
    return UPDATE_ARRIVAL_DATE

# 处理到货日期的函数
def update_arrival_date(update, context):
    query = update.callback_query
    query.answer()
    selected_date = query.data
    context.user_data['update_arrival_date'] = selected_date
    query.edit_message_text(text=f"已选择到货日期：{selected_date}\n请选择供应商:")
    
    # 生成供应商选择按钮
    suppliers = warehousing_manager.get_supplier_list()  # 获取供应商列表
    buttons = [InlineKeyboardButton(supplier, callback_data=supplier) for supplier in suppliers]
    buttons.append(InlineKeyboardButton("手动输入", callback_data="manual_input_supplier"))
    query.edit_message_text(text="请选择或输入供应商名称:", reply_markup=InlineKeyboardMarkup([buttons]))
    
    return UPDATE_SUPPLIER

# 处理供应商名的函数
def warehousing_update_supplier(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    if query.data == "manual_input_supplier":
        query.edit_message_text(text="请输入供应商名称:")
        return MANUAL_INPUT_SUPPLIER
    else:
        context.user_data['update_supplier'] = query.data
        query.edit_message_text(text=f"已选择供应商：{query.data}\n请选择或输入产品名称:")
        
        # 生成产品选择按钮
        products = warehousing_manager.get_product_list()  # 获取产品列表
        buttons = [InlineKeyboardButton(product, callback_data=product) for product in products]
        buttons.append(InlineKeyboardButton("手动输入", callback_data="manual_input_product"))
        query.edit_message_text(text="请选择或输入产品名称:", reply_markup=InlineKeyboardMarkup([buttons]))
        
    return UPDATE_PRODUCT

# 处理产品名称的函数
def warehousing_update_product(update: Update, context: CallbackContext) -> int:
    context.user_data['update_product'] = update.message.text
    update.message.reply_text("请输入新的入库数量（如果不修改请回复 NONE）：")
    return UPDATE_NEW_QUANTITY

def supplier_product(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    logging.info("supplier product")
    if query.data == "manual_input_product":
        # 提示用户手动输入产品名称
        context.user_data['manual_input_for_product'] = True
        query.edit_message_text(text="请输入产品名称:")
        return MANUAL_INPUT_PRODUCT
    else:
        # 用户从列表中选择了一个产品
        context.user_data['supplier_product'] = query.data
        context.user_data['manual_input_for_product'] = False
        query.edit_message_text(text="请输入入库数量:")
        return WAREHOUSING_STOCK_IN

# 处理新的入库数量的函数
def warehousing_update_new_quantity(update: Update, context: CallbackContext) -> int:
    quantity = update.message.text
    context.user_data['update_new_quantity'] = None if quantity.lower() == 'none' else quantity
    update.message.reply_text("请输入新的单价（如果不修改请回复 NONE）：")
    return UPDATE_NEW_UNIT_PRICE

# 处理新的单价的函数
def warehousing_new_unit_price(update: Update, context: CallbackContext) -> int:
    price = update.message.text
    context.user_data['update_unit_price'] = None if price.lower() == 'none' else price
    # 确认信息
    query = update.callback_query
    query.answer()
    confirmation_text = "请确认更新信息：\n"
    confirmation_text += f"到货日期: {context.user_data['update_arrival_date']}\n供应商: {context.user_data['update_supplier']}\n产品: {context.user_data['update_product']}\n新的入库数量: {context.user_data.get('update_new_quantity', '未更改')}\n新的单价: {context.user_data.get('update_unit_price', '未更改')}"
    keyboard = [
        [InlineKeyboardButton("确认", callback_data='confirm')],
        [InlineKeyboardButton("取消", callback_data='cancel')]
    ]
    query.edit_message_text(text=confirmation_text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    return UPDATE_SUPPLIER_CONFIRMATION

# 确认并执行更新的函数
def perform_update_warehousing(update: Update, context: CallbackContext) -> int:
    if update.message.text.lower() == 'yes':
        # 调用更新函数
        message = warehousing_manager.update_stock_out_or_unit_price(
            arrival_date=context.user_data['update_arrival_date'],
            supplier=context.user_data['update_supplier'],
            product=context.user_data['update_product'],
            new_quantity=context.user_data['update_new_quantity'],
            unit_price=context.user_data['update_unit_price']
        )
        update.message.reply_text(message)
    else:
        update.message.reply_text("更新已取消，请重新开始。")
    return ConversationHandler.END

"""
###################################################################################
                                MAIN
###################################################################################
"""
def main() -> None:
    """运行bot"""
    # 创建Updater并传入你的bot的token。
    updater = Updater(TOKEN)

    # 获取dispatcher来注册handlers
    dispatcher = updater.dispatcher
    dp = updater.dispatcher

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    # try:
        
    dispatcher.add_handler(CommandHandler("start", start))

    dispatcher.add_handler(CommandHandler("help", help))

    ########################################### SALES ############################################################
    dispatcher.add_handler(CommandHandler("sale_get_all", sale_get_all))
    
    conv_handler_sale_start = ConversationHandler(
        entry_points=[CommandHandler('record_out', sale_start)],
        states={
            SALE_CUSTOMER: [CallbackQueryHandler(sale_customer)],
            MANUAL_INPUT_CUSTOMER: [MessageHandler(Filters.text & ~Filters.command, manual_input_customer)],  
            SALE_PRODUCT: [CallbackQueryHandler(sale_product)],
            # SALE_SHIPPING_DATE: [CallbackQueryHandler(sale_shipping_date)],
            SALE_CONFIRM_DATE: [CallbackQueryHandler(sale_confirm_or_change_date, pattern='^(confirm_today|enter_custom)$')],
            SALE_ENTER_CUSTOM_DATE: [MessageHandler(Filters.text & ~Filters.command, sale_enter_custom_date)],
            SALE_STOCK_OUT: [MessageHandler(Filters.text, sale_stock_out)],
            SALE_UNIT_PRICE: [MessageHandler(Filters.text, sale_unit_price)],
            SALE_SELLER: [CallbackQueryHandler(sale_seller)],
            SALE_PAYMENT: [MessageHandler(Filters.text, sale_payment)],
            SALE_CONFIRMATION: [CallbackQueryHandler(sale_confirmation, pattern='^(confirm|reenter)$')]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler_sale_start)
    
    conv_handler_sale_delete = ConversationHandler(
        entry_points=[CommandHandler('sale_delete_by_id', start_delete_sale)],
        states={
            SALE_DELETE: [MessageHandler(Filters.text & ~Filters.command, delete_sale)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler_sale_delete)

    # This is find sale records for a customer
    conv_handler_sales_find_by_customer = ConversationHandler(
        entry_points=[CommandHandler('sale_by_customer', start_find_sale_by_customer_name)],
        states={
            SALE_FIND_CUSTOMER: [CallbackQueryHandler(handle_customer_selection)],
            HANDLE_MANUAL_FIND_CUSTOMER_INPUT: [MessageHandler(Filters.text & ~Filters.command, handle_manual_find_customer_input)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler_sales_find_by_customer)
    
    conv_handler_sales_get_by_id = ConversationHandler(
        entry_points=[CommandHandler('sale_get_by_id', start_find_sale)],
        states={
            SALE_FIND: [MessageHandler(Filters.text & ~Filters.command, find_sale_by_id)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler_sales_get_by_id)
    
    ################################################# Customer ######################################################
    conv_handler_customer_add = ConversationHandler(
        entry_points=[CommandHandler('customer_add', customer_add)],
        states={
            CUSTOMER_NAME: [MessageHandler(Filters.text, customer_name)],
            CUSTOMER_PAYABLE: [MessageHandler(Filters.text, customer_payable)],
            CUSTOMER_PAYMENT: [MessageHandler(Filters.text, customer_payment)],         
            CUSTOMER_COMFIRMATION: [MessageHandler(Filters.regex('^(yes|no)$'), customer_confirmation)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler_customer_add)

    dispatcher.add_handler(CallbackQueryHandler(customer_confirmation, pattern='^(confirm|reenter)$'))

    debt_handler = CommandHandler('get_customers_with_debt', get_customers_with_debt)
    dispatcher.add_handler(debt_handler)

    conv_handler_update_payment = ConversationHandler(
    entry_points=[CommandHandler('update_payment', update_payment_start)],
        states={
            UPDATE_CUSTOMER_NAME: [MessageHandler(Filters.text & ~Filters.command, update_payment_customer_name)],
            UPDATE_PAYABLE: [MessageHandler(Filters.text & ~Filters.command, update_payment_payable)],
            UPDATE_PAYMENT: [MessageHandler(Filters.text & ~Filters.command, update_payment)],
            UPDATE_CONFIRMATION: [MessageHandler(Filters.regex('^(yes|no)$'), update_payment_confirmation)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler_update_payment)

    dispatcher.add_handler(CallbackQueryHandler(update_payment_confirmation, pattern='^(confirm|reenter)$'))

    dispatcher.add_handler(CommandHandler('customer_excess_payment', get_customers_with_excess_payment_handler))

    conv_handler_delete_customer = ConversationHandler(
        entry_points=[CommandHandler('delete_customer', customer_delete_start)],
        states={
            CUSTOMER_DELETE_NAME: [CallbackQueryHandler( customer_delete_name)],
            CUSTOMER_DELETE_CONFIRMATION: [CallbackQueryHandler(delete_customer_confirmation, pattern=('^(confirm_delete|cancel_delete)$'))],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler_delete_customer)

    dispatcher.add_handler(CommandHandler("get_all_customers", get_all_customers))

    ########################################### Inventory ###########################################
    conv_handler_get_product_data = ConversationHandler(
        entry_points=[CommandHandler('get_product_data', start_get_product_data)],
        states={
            PRODUCT_QUERY: [CallbackQueryHandler(product_query)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler_get_product_data)

    # 添加处理函数
    dp.add_handler(CommandHandler("start_get_product_data", start_get_product_data))
    
    # 添加查询回调处理
    dp.add_handler(CallbackQueryHandler(product_query, pattern='^' + str(PRODUCT_QUERY) + '$'))

    conv_handler_inventory_delete = ConversationHandler(
        entry_points=[CommandHandler('delete_product', start_delete_product)],
        states={DELETE_PRODUCT: [CallbackQueryHandler(delete_product)],},
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler_inventory_delete)

    dispatcher.add_handler(CommandHandler('list_all_products', list_all_products))

    conv_handler_add_or_update_product = ConversationHandler(
        entry_points=[CommandHandler('add_or_update_product', start_add_or_update_product)],
            states={
                PRODUCT_NAME: [MessageHandler(Filters.text & ~Filters.command, product_name)],
                OPENING_INVENTORY: [MessageHandler(Filters.text & ~Filters.command, opening_inventory)],
                STOCK_IN: [MessageHandler(Filters.text & ~Filters.command, stock_in)],
                STOCK_OUT: [MessageHandler(Filters.text & ~Filters.command, stock_out)],
                SCHEDULE_INVENTORY: [MessageHandler(Filters.text & ~Filters.command, schedule_inventory)],
                TOTAL_INVENTORY: [MessageHandler(Filters.text & ~Filters.command, total_inventory)],
                IN_STOCK: [MessageHandler(Filters.text & ~Filters.command, in_stock)],
                PRODUCT_CONFIRMATION: [MessageHandler(Filters.regex('^(yes|no)$'), perform_add_or_update)]
            },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    dispatcher.add_handler(conv_handler_add_or_update_product)

    conv_handler_add_product_name = ConversationHandler(
        entry_points=[CommandHandler('add_product_name', add_product_name)],
        states={
            ENTER_PRODUCT_NAME: [MessageHandler(Filters.text & ~Filters.command, enter_product_name)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler_add_product_name)

    ######################################### Warehousing #########################################
    conv_handler_add_warehousing = ConversationHandler(
        entry_points=[CommandHandler('record_in', start_add_warehousing)],
            states={
                WAREHOUSING_ARRIVAL_DATE: [CallbackQueryHandler(arrival_date)],
                MANUAL_INPUT_ARRIVAL_DATE: [MessageHandler(Filters.text & ~Filters.command, manual_input_arrival_date)],
                CHOOSE_SUPPLIER_METHOD: [CallbackQueryHandler(choose_supplier_method)],
                MANUAL_INPUT_SUPPLIER: [MessageHandler(Filters.text & ~Filters.command, manual_input_supplier)],
                SUPPLIER_PRODUCT: [CallbackQueryHandler(supplier_product), MessageHandler(Filters.text & ~Filters.command, choose_supplier_method)],
                WAREHOUSING_STOCK_IN: [MessageHandler(Filters.text & ~Filters.command, warehousing_stock_in)],
                WAREHOUSING_UNIT_PRICE: [MessageHandler(Filters.text & ~Filters.command, warehousing_unit_price)],
                SUPPLIER_CONFIRMATION: [CallbackQueryHandler(confirm_warehousing)]
            },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dispatcher.add_handler(conv_handler_add_warehousing)

    delete_warehousing_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('delete_warehousing', start_delete_warehousing)],
        states={
            DELETE_ARRIVAL_DATE: [CallbackQueryHandler(delete_warehousing_arrival_date)],
            MANUAL_DELETE_WAREHOUSING_DATE: [MessageHandler(Filters.text & ~Filters.command, manual_delete_warehousing_date)],
            DELETE_SUPPLIER: [CallbackQueryHandler(delete_warehousing_supplier)],
            DELETE_PRODUCT: [CallbackQueryHandler(delete_warehousing_product)],
            DELETE_SUPPLIER_CONFIRMATION: [CallbackQueryHandler(delete_warehousing_confirmation, pattern=('^(confirm_delete|cancel)$'))]
        },
        fallbacks=[CommandHandler('cancel', cancel)],  # 假设你有一个取消函数
    )

    # 添加处理器到 dispatcher
    dispatcher.add_handler(delete_warehousing_conv_handler)

    update_warehousing_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('update_warehousing', start_update_warehousing)],
        states={
            UPDATE_ARRIVAL_DATE: [CallbackQueryHandler(update_arrival_date, pattern='^\d{2}/\d{2}/\d{4}$')],
            UPDATE_SUPPLIER: [
                CallbackQueryHandler(manual_input_supplier, pattern='^manual_input_supplier$'),
                CallbackQueryHandler(warehousing_update_supplier, pattern='^\w+$')  # 假设供应商名称为字母和数字
            ],
            MANUAL_INPUT_SUPPLIER: [MessageHandler(Filters.text & ~Filters.command, manual_input_supplier)],
            UPDATE_PRODUCT: [
                CallbackQueryHandler(manual_input_product, pattern='^manual_input_product$'),
                CallbackQueryHandler(supplier_product, pattern='^\w+$')  # 假设产品名称为字母和数字
            ],
            MANUAL_INPUT_PRODUCT: [MessageHandler(Filters.text & ~Filters.command, manual_input_product)],
            UPDATE_NEW_QUANTITY: [MessageHandler(Filters.text & ~Filters.command, warehousing_update_new_quantity)],
            UPDATE_NEW_UNIT_PRICE: [MessageHandler(Filters.text & ~Filters.command, warehousing_new_unit_price)],
            UPDATE_CONFIRMATION: [CallbackQueryHandler(perform_update_warehousing, pattern='^(confirm|cancel)$')]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(update_warehousing_conv_handler)

    conv_handler_find_by_date = ConversationHandler(
        entry_points=[CommandHandler('get_warehoursing_by_date', start_find_by_date)],
        states={
            FIND_BY_DATE: [CallbackQueryHandler(find_by_date)],
            MANUAL_FIND_WAREHOUSING_DATE: [MessageHandler(Filters.text & ~Filters.command, manual_find_warehousing_date)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler_find_by_date)

    get_all_warehousing_handler = CommandHandler('get_all_warehousing', get_all_warehousing)
    dispatcher.add_handler(get_all_warehousing_handler)
    
    #######################################################################################################
    # 开始Bot
    updater.start_polling()

    # 一直运行直到按Ctrl-C或进程收到SIGINT, SIGTERM或SIGABRT。这应该在大多数情况下用于非异步应用程序。
    updater.idle()
    # except Exception or TypeError or AttributeError as e:
    #     error_message = f"发生错误：{e}"
    #     updater.message.reply_text(error_message)
    #     updater.message.reply_text('尽管发生了错误，但我们可以继续进行其他操作。请输入下一步命令。')
        

if __name__ == '__main__':
    # try:
    #     main()
    # except Exception as e:
    #     logger.error("ERROR: ", exc_info=True)
    main()
