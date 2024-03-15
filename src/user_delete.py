import telegram
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, CallbackQueryHandler
import logging

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

"""
###################################################################################
                            Sales records 销售记录表
###################################################################################
"""

SALE_DELETE = range(2)

# Function to start deleting a sale record by ID
def start_delete_sale(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('请输入要删除的销售记录ID:')
    return SALE_DELETE

def delete_sale(update: Update, context: CallbackContext) -> int:
    data = update.message.text  
    deletion_message = sales_manager.delete_sale(data) 
    update.message.reply_text(deletion_message)
    logging.info(f"{data} deleted")
    return ConversationHandler.END

"""
###################################################################################
                                Customer 客户记录表
###################################################################################
"""
CUSTOMER_DELETE_NAME, CUSTOMER_DELETE_CONFIRMATION = range(2)

def customer_delete_start(update: Update, context: CallbackContext) -> int:
    # 假设有一个方法返回所有客户名列表
    customer_list = customers_manager.get_customer_name_list()
    if len(customer_list) == 0:
        update.message.reply_text('没有可以删除的客户名')
        return ConversationHandler.END
    
    keyboard = [[InlineKeyboardButton(customer, callback_data=customer)] for customer in customer_list]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('请选择要删除的客户名：', reply_markup=reply_markup)
    return CUSTOMER_DELETE_NAME

def customer_delete_name(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    context.user_data['customer_delete_name'] = query.data
    # 确认信息
    keyboard = [
        [InlineKeyboardButton("确认删除", callback_data='confirm_delete')],
        [InlineKeyboardButton("取消", callback_data='cancel_delete')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=f"您确定要删除客户 '{context.user_data['customer_delete_name']}' 吗？", reply_markup=reply_markup)
    return CUSTOMER_DELETE_CONFIRMATION

def delete_customer_confirmation(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    if query.data == 'confirm_delete':
        customer_name = context.user_data['customer_delete_name']
        success, response = customers_manager.delete_customer(customer_name)
        query.edit_message_text(text=response)
    elif query.data == 'cancel_delete':
        query.edit_message_text(text='已取消删除操作。')
    return ConversationHandler.END

"""
###################################################################################
                                Inventory 库存登记
###################################################################################
"""
DELETE_PRODUCT = range(1)

def start_delete_product(update: Update, context: CallbackContext) -> int:
    product_list = inventory_manager.get_product_list()
    keyboard = [[InlineKeyboardButton(product, callback_data=product)] for product in product_list]
    reply_markup = InlineKeyboardMarkup(build_menu(keyboard, 2))
    update.message.reply_text('请选择您要删除的产品名称：', reply_markup=reply_markup)
    return DELETE_PRODUCT

def delete_product(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    selected_product = query.data
    response = inventory_manager.delete_product_by_name(selected_product)
    response = f"已删除产品：{selected_product}"
    query.edit_message_text(text=response)
    return ConversationHandler.END

"""
###################################################################################
                                Warehousing 入货记录
###################################################################################
"""
(DELETE_ARRIVAL_DATE, DELETE_SUPPLIER, DELETE_PRODUCT, DELETE_SUPPLIER_CONFIRMATION) = range(4)
MANUAL_DELETE_WAREHOUSING_DATE = range(1)
def build_selection_keyboard(options):
    # 根据选项列表生成选择键盘
    keyboard = [InlineKeyboardButton(name, callback_data=name) for name in options]
    keyboard.append(InlineKeyboardButton("取消", callback_data='cancel'))
    return InlineKeyboardMarkup(build_menu(keyboard, 2))

def start_delete_warehousing(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("请选择要删除的仓储记录的到货日期：", reply_markup=build_date_keyboard())
    return DELETE_ARRIVAL_DATE

def delete_warehousing_arrival_date(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    if query.data == 'choose_today':
        selected_date = datetime.now().strftime('%d/%m/%Y')
        context.user_data['delete_arrival_date'] = selected_date
        # supplier
        flag, suppliers = warehousing_manager.get_supplier_list()  
        if flag:
            query.edit_message_text("请选择供应商名称：", reply_markup=build_selection_keyboard(suppliers))
            return DELETE_SUPPLIER
        else: 
            query.edit_message_text("库存表中没有供应商名称，且库存表中无数据。\n无法删除库存数据。")
            return ConversationHandler.END
    else: 
        query.edit_message_text(text="请输入日期：请使用DD/MM/YYYY格式输入")
        return MANUAL_DELETE_WAREHOUSING_DATE

def manual_delete_warehousing_date(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    try:
        # Attempt to convert the text input into a datetime object
        # custom_date = datetime.strptime(text, '%d/%m/%Y')
        flag, custom_date = check_shipping_date(text)
        if flag:
            context.user_data['delete_arrival_date'] = custom_date
            # supplier
            flag, suppliers = warehousing_manager.get_supplier_list()  
            if flag:
                update.message.reply_text("请选择供应商名称：", reply_markup=build_selection_keyboard(suppliers))
                return DELETE_SUPPLIER
            else: 
                update.message.reply_text("库存表中没有供应商名称，且库存表中无数据。\n无法删除库存数据。")
                return ConversationHandler.END
        else:
            update.message.reply_text("日期格式不正确，请使用DD/MM/YYYY格式重新输入：")
        return MANUAL_DELETE_WAREHOUSING_DATE
    except ValueError:
        # If the date format is incorrect, prompt the user to try again
        update.message.reply_text("日期格式不正确，请使用DD/MM/YYYY格式重新输入：")
        return MANUAL_DELETE_WAREHOUSING_DATE

def delete_warehousing_supplier(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    if query.data == 'cancel':
        query.edit_message_text("操作已取消。")
        return ConversationHandler.END
    context.user_data['delete_supplier'] = query.data
    flag, products = warehousing_manager.get_product_list() 
    
    if flag:
        query.edit_message_text("请选择产品名称：", reply_markup=build_selection_keyboard(products))
        return DELETE_PRODUCT
    else: 
        update.message.reply_text("库存表中没有产品名称，且库存表中无数据。\n无法删除库存数据。")
        return ConversationHandler.END
    
def delete_warehousing_product(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    if query.data == 'cancel':
        query.edit_message_text("操作已取消。")
        return ConversationHandler.END
    context.user_data['delete_product'] = query.data
    confirmation_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("确认", callback_data='confirm_delete'), InlineKeyboardButton("取消", callback_data='cancel')]])
    query.edit_message_text(f"您要删除的记录信息如下：\n到货日期：{context.user_data['delete_arrival_date']}\n供应商：{context.user_data['delete_supplier']}\n产品名称：{context.user_data['delete_product']}\n请确认是否删除：", reply_markup=confirmation_keyboard)
    return DELETE_SUPPLIER_CONFIRMATION
   
def delete_warehousing_confirmation(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    if query.data == 'confirm_delete':
        # 执行删除操作
        response = warehousing_manager.delete_warehousing_record(context.user_data['delete_arrival_date'], context.user_data['delete_supplier'], context.user_data['delete_product'])
        query.edit_message_text(response)
    else:
        query.edit_message_text("操作已取消。")
    return ConversationHandler.END