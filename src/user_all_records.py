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
from user_handle_message import send_long_text, cancel, reply_message
from user_handle_message import reply_long_message

from user_get_button_menu import get_customer_buttons, build_date_keyboard, get_product_buttons

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
def show_sales_records(update: Update, context: CallbackContext, sale_info: str) -> int:
    response_message = f"找到的销售记录：\n"
    i = 0
    for sale in sale_info: 
        response_message += f"销售ID : {sale.get_sale_id()}\n"
        response_message += f"出货日期 : {sale.get_shipping_date()}\n"
        response_message += f"客户 : {sale.get_customer()}\n"
        response_message += f"产品名称 : {sale.get_product()}\n"
        response_message += f"出库数量 : {sale.get_stock_out()}\n"
        response_message += f"单价 : {sale.get_unit_price()}\n"
        response_message += f"总价 : {sale.get_total_price()}\n"
        response_message += f"销售员 : {sale.get_staff()}\n"
        response_message += f"款项 : {sale.get_payment()}\n"
        send_long_text(update.effective_chat.id, response_message, context.bot)
        response_message = ''
        i += 1
    return i
    
# Get all sales records 获取所有销售记录
def sale_get_all(update: Update, context: CallbackContext) -> None:
    sales = sales_manager.get_all()
    if not sales:
        # update.message.reply_text("当前没有销售记录。")
        message = "当前没有销售记录。"
        reply_message(update, context, message, None)
        return ConversationHandler.END
    i = show_sales_records(update, context, sales)
    response = f"一共有{i}记录销售。"
    send_long_text(update.effective_chat.id, response, context.bot)
    return ConversationHandler.END

SALE_FIND = range(1)
# Function to start finding a sale record by ID
def start_find_sale(update: Update, context: CallbackContext) -> int:
    # update.message.reply_text('请输入要查找的销售记录ID:')
    message='请输入要查找的销售记录ID:'
    reply_message(update, context, message, None)
    return SALE_FIND

# Function to find a sale record by ID
def find_sale_by_id(update: Update, context: CallbackContext) -> int:
    args = update.message.text  # Assuming args are passed as: /find_sale sale_id
    
    if ' ' in args:
        args = args.repalce(' ')

    sale_id = args
    got_it, sale_info = sales_manager.find_sale_by_id(sale_id)  # Assuming this method returns sale information or a message
    # Check if sale_info is a single Sale object
    if got_it:  # Check if sale_info is a list of Sale objects
        i = show_sales_records(update, context, sale_info)
        response_message = f"该销售ID为 '{sale_id}' 的一共有{i}记录。"

    else:  # If sale_info is None or not found
        response_message = f"未找到销售ID为 '{sale_id}' 的记录。"
    
    send_long_text(update.effective_chat.id, response_message, context.bot)
    return ConversationHandler.END

# Function to start finding sale records by customer name
SALE_FIND_CUSTOMER, HANDLE_MANUAL_FIND_CUSTOMER_INPUT = range(2)

def start_find_sale_by_customer_name(update: Update, context: CallbackContext) -> int:
    flag, reply_markup = get_customer_buttons(update, context, manual_input=True, cancel=False)
    message='请选择或输入客户名字：'
    reply_message(update, context, message, reply_markup)
    return SALE_FIND_CUSTOMER

def handle_customer_selection(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    selected_customer = query.data
    logging.info(f"handdle_customer_selection: {selected_customer}")
    if selected_customer in ["mannual_input_customer"]:
        query.edit_message_text(text="请输入客户名字：")
        return HANDLE_MANUAL_FIND_CUSTOMER_INPUT
    else:
        return find_sale_by_customer_name_with_data(update, context, selected_customer)

def handle_manual_find_customer_input(update: Update, context: CallbackContext) -> int:
    customer_name = update.message.text
    return find_sale_by_customer_name_with_data(update, context, customer_name)

# Function to find a sale record by customer name
def find_sale_by_customer_name_with_data(update: Update, context: CallbackContext, customer: str) -> int:
    got_it, sale_info = sales_manager.find_sales_by_customer(customer) 
    logging.info(f"got the customer sale info {sale_info}")
    if got_it:
        i = show_sales_records(update, context, sale_info)
        response_message = f"该客户名为 '{customer}'的一共有{i}记录。"
    else:
        response_message = f"未找到客户名为 '{customer}' 的记录。"
    reply_long_message(update, context, response_message)
    return ConversationHandler.END

"""
###################################################################################
                                Customer 客户记录表
###################################################################################
"""
def get_customers_with_excess_payment_handler(update: Update, context: CallbackContext) -> None:
    flag, customers_with_excess_payment = customers_manager.get_customers_with_excess_payment()
    
    if not flag:
        # update.message.reply_text("没有找到超额支付的客户。")
        message="没有找到超额支付的客户。"
        reply_message(update, context, message, None)
        return ConversationHandler.END
    i = 0
    response = "超额支付的客户列表:\n"
    for customer in customers_with_excess_payment:
        excess_payment = float(customer.get_payment()) - float(customer.get_payable())
        response += f"- 客户 {customer.get_customer()}: \n\t支付了 {customer.get_payment()}，\n\t但应付金额仅为 {customer.get_payable()}。\n\t超额: {excess_payment}\n"
        reply_long_message(update, context, response)
        i += 1
        response = ''
    response = f'一共有{i}位客户超额支付。'
    return ConversationHandler.END

def get_customers_with_debt(update: Update, context: CallbackContext) -> None:
    # Call the method to get customers with debt
    flag, customers_with_debt = customers_manager.get_customers_with_debt()
    
    # Check if there are any customers with debt
    if flag:
        i = 0
        response = "有欠款的客户\n"
        for customer in customers_with_debt:
            customer_info = f"- {customer.get_customer()} -- 欠款金额: {customer.get_debt()}\n"
            response += customer_info
            send_long_text(update.effective_chat.id, response, context.bot)
            response = ''
            i += 1
        response = f'一共有{i}位客户欠款。'
    else:
        response = "目前没有客户欠款"
    
    send_long_text(update.effective_chat.id, response, context.bot)
    return ConversationHandler.END

# Get all customers
def get_all_customers(update: Update, context: CallbackContext) -> None:
    all_customers = customers_manager.get_all()
    
    if not all_customers:
        reply_message(update, context, "没有找到客户。", None)
        return ConversationHandler.END
    
    i = 0
    message = "所有客户列表：\n"
    for customer in all_customers:
        customer_info = customer.to_dict()  # 假设每个客户都有一个 to_dict 方法以便格式化
        message += f"客户名：{customer_info['Customer']}, 、\n应付金额：{customer_info['Payable']}元, \n实付金额：{customer_info['Payment']}元, \n欠款金额：{customer_info['Debt']}元\n"
        reply_long_message(update, context, message)
        i += 1
        message = ''
    message = f"一共有{i}位客户登记在列"
    reply_long_message(update, context, message)
    return ConversationHandler.END

"""
###################################################################################
                                Inventory 库存登记
###################################################################################
"""
def show_product_message(update: Update, context: CallbackContext, product_data: list):
    i = 0
    message = ''
    logging.info("Show product message")
    for product in product_data:
        product_info = f"{product.get_product_chinese()}：{product.get_product()},\n" \
                    f"{product.get_total_inventory_chinese()}：{product.get_total_inventory()},\n" \
                    f"{product.get_in_stock_chinese()}：{product.get_in_stock()}\n\n"
        
        message += product_info
        i += 1
        if i >= 10:
            send_long_text(update.effective_chat.id, message, context.bot)
            i = 0 
            message = ''
    if message != '':
        send_long_text(update.effective_chat.id, message, context.bot)
        
def list_all_products(update: Update, context: CallbackContext) -> None:
    all_products = inventory_manager.get_all()  
    
    # 检查是否有产品
    if not all_products:
        # update.message.reply_text("当前库存中没有产品。")
        reply_message(update, context, "当前库存中没有产品。", None)
        return ConversationHandler.END
    
    # 格式化产品信息为文本
    message = "当前库存中的所有产品：\n\n"
    # send_long_text(update.effective_chat.id, message, context.bot)
    reply_long_message(update, context, message)
    show_product_message(update, context, all_products)
    return ConversationHandler.END


PRODUCT_QUERY = range(1)

def start_get_product_data(update: Update, context: CallbackContext) -> int:
    flag, reply_markup = get_product_buttons(update, context, manual_input=False, cancel=True) 
    if flag is False:
        return cancel(update, context)
    reply_message(update, context, '请选择您想查询的产品名称：', reply_markup)
    return PRODUCT_QUERY

def product_query(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer() 
    product_name = query.data
    if product_name.startswith('cancel'):
        return cancel(update, context)
    logging.info(f"we are looking for product: {product_name}")
    flag, product_data = inventory_manager.get_product_data(product_name)
    
    if flag:
        logging.info(f"product: {product_data[0].to_dict()}")
        show_product_message(update, context, product_data)
    else:
        response = f"未找到产品：{product_name}"
        query.edit_message_text(text=response)
    return ConversationHandler.END

"""
###################################################################################
                                Warehousing 入货记录
###################################################################################
"""
def show_warehousing_records(update, context, warehousing):
    i = 0
    message = ''
    logging.info("Show warehousing message")
    for item in warehousing:
        message = f"\n到货日期: {item.get_arrival_date()}, \n"
        message += f"供货商: {item.get_supplier()}, \n" 
        message += f"产品: {item.get_product()}, \n"
        message += f"入库数量: {item.get_stock_in()}\n" 
        message += f"单价: {item.get_unit_price()},\n"
        message += f"总价: {item.get_unit_price()}\n"
        # send_long_text(update.effective_chat.id, message, context.bot)
        # reply_long_message(update, context, message)
        reply_message(update, context, message)
        i += 1
        message = ''
    if message != '':
        # send_long_text(update.effective_chat.id, message, context.bot)
        # reply_long_message(update, context, message)
        reply_message(update, context, message)
    message = f'一共{i}条记录。'
    # send_long_text(update.effective_chat.id, message, context.bot)
    # reply_long_message(update, context, message)
    reply_message(update, context, message)

FIND_BY_DATE, MANUAL_FIND_WAREHOUSING_DATE = range(2)

def start_find_by_date(update: Update, context: CallbackContext) -> int:
    """启动对话，询问用户想查询的日期"""
    # update.message.reply_text('请选择日期:', reply_markup=build_date_keyboard())
    logging.info(f"start find by date")
    reply_message(update, context, '请选择日期:', reply_markup=build_date_keyboard())
    return FIND_BY_DATE

def find_by_date(update: Update, context: CallbackContext) -> int:
    """处理用户输入的日期，并查找匹配的记录"""
    query = update.callback_query
    query.answer()
    selected_date = query.data
    if selected_date == 'choose_today':
        selected_date = datetime.now().strftime('%d/%m/%Y')
        get_warehousing_info_by_date(update, context, selected_date)
    else: 
        query.edit_message_text(text="请输入日期：请使用DD/MM/YYYY格式输入")
        return MANUAL_FIND_WAREHOUSING_DATE
    return ConversationHandler.END

def get_warehousing_info_by_date(update, context, selected_date):
    # text = update.message.text
    flag, matching_records = warehousing_manager.find_by_date(selected_date)
    if flag:
        # update.message.reply_text(text=f"{selected_date} 找到以下匹配的记录\n")
        reply_message(update, context, f"{selected_date} 找到以下匹配的记录\n", reply_markup=None)
        show_warehousing_records(update, context, matching_records)
    else:
        # update.message.reply_text(text=f"{selected_date} 没有找到匹配的记录。")
        reply_message(update, context, f"{selected_date} 没有找到匹配的记录。", reply_markup=None)

def manual_find_warehousing_date(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    try:
        # Attempt to convert the text input into a datetime object
        # custom_date = datetime.strptime(text, '%d/%m/%Y')
        flag, custom_date = check_shipping_date(text)
        if flag:
            get_warehousing_info_by_date(update, context, custom_date)
            return ConversationHandler.END
        else:
            update.message.reply_text("日期格式不正确，请使用DD/MM/YYYY格式重新输入：")
        return MANUAL_FIND_WAREHOUSING_DATE
        
    except ValueError:
        # If the date format is incorrect, prompt the user to try again
        update.message.reply_text("日期格式不正确，请使用DD/MM/YYYY格式重新输入：")
        return MANUAL_FIND_WAREHOUSING_DATE

def get_all_warehousing(update: Update, context: CallbackContext) -> None:
    all_records = warehousing_manager.get_all()
    
    if not all_records:
        # update.message.reply_text("当前没有入库记录。")
        reply_message(update, context,"当前没有入库记录。", None)
        return ConversationHandler.END

    message = "所有入库记录：\n"
    # send_long_text(update.effective_chat.id, message, context.bot)
    reply_long_message(update, context, message)
    show_warehousing_records(update, context, all_records)    
    return ConversationHandler.END
