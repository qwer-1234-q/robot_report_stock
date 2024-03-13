from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
import json
import os 
import telebot
import requests

# 导入之前定义的类
from read_sales import Sales
from read_warehousing import Warehousing_read
from read_inventory import Inventories
from read_customer import Customers

from datetime import datetime 

# Telegram Bot Token
TOKEN = '6487583852:AAGH3YlPRpfuOtLt-GlWvyI4Ss-B1lxOdtA'

# Telegram 
website = 'https://web.telegram.org/a/#6487583852'

# 实例化管理对象
sales_manager = Sales()
warehousing_manager = Warehousing_read()
inventory_manager = Inventories()
customers_manager = Customers()

"""
###################################################################################
                            Start 开始
###################################################################################
"""
def start(update: Update, context: CallbackContext) -> None:
    """发送一个消息，当命令 /start 被调用时。"""
    update.message.reply_text("Hello! I am your bot. Send me a command to get started./nIf you don't know how to start, type /help")
    update.message.reply_text('欢迎使用我们的Telegram机器人！')

"""
###################################################################################
                             Handle message
###################################################################################
"""
def send_long_text(chat_id, text, bot):
    MAX_LENGTH = 4096
    parts = [text[i:i+MAX_LENGTH] for i in range(0, len(text), MAX_LENGTH)]
    for part in parts:
        bot.send_message(chat_id=chat_id, text=part)

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('操作已取消。')
    return ConversationHandler.END

def help(update: Update, context: CallbackContext) -> int:
    command_list = [
        "/start - 开始与机器人的对话 / Start interacting with the bot.",
        "/sale_add - 添加新的销售记录 / Add a new sales record.",
        "/sale_get_all - 获得所有销售记录 / Retrieve all sales records.",
        "/sale_delete - 删除指定销售ID的记录 / Delete a sales record by ID.",
        "/sale_find - 根据销售ID查找销售记录 / Find a sales record by ID.",
        "/customer_add - 添加新客户及其付款信息 / Add a new customer and their payment info.",
        "/get_customers_with_debt - 查找有欠款的客户 / Find customers with outstanding debt.",
        "/update_payment - 更新客户付款信息 / Update customer payment information.",
        "/get_all_customers - 获取所有客户记录 / Retrieve all customer records.",
        "/get_product_data - 获取指定产品的详细信息 / Get detailed information of a specific product.",
        "/add_or_update_product - 添加或更新产品信息 / Add or update product information.",
        "/delete_product - 删除指定的产品记录 / Delete a specified product record.",
        "/list_all_products - 列出所有产品信息 / List all product information.",
        "/add_warehousing - 添加仓库入库记录 / Add warehousing record.",
        "/delete_warehousing - 删除仓库入库记录 / Delete warehousing record.",
        "/update_warehousing - 更新仓库入库记录信息 / Update warehousing record.",
        "/get_all_warehousing - 获取所有仓库入库记录 / Retrieve all warehousing records.",
        "/find_inventory_by_date - 根据到货日期查找入库记录 / Find warehousing records by arrival date.",
        "请使用这些命令与机器人进行交互 / Please use these commands to interact with the bot."
    ]
    # Join the command list into a single string message
    help_message = "\n".join(command_list)
    send_long_text(update.effective_chat.id, help_message, context.bot)
    return ConversationHandler.END

"""
###################################################################################
                            Sales records 销售记录表
###################################################################################
"""
SALE_CUSTOMER, SALE_PRODUCT, SALE_SHIPPING_DATE, SALE_SHIPPING_TIME, SALE_OUTBOUND_QUANTITY, SALE_UNIT_PRICE, SALE_SELLER, SALE_PAYMENT, SALE_CONFIRMATION, SALE_DELETE, SALE_FIND, SALE_FIND_CUSTOMER = range(12)

def sale_start(update: Update, context: CallbackContext) -> str:
    update.message.reply_text('请输入客户名 / Please input customer name:')
    return SALE_CUSTOMER

def sale_customer(update: Update, context: CallbackContext) -> str:
    context.user_data['sale_customer'] = update.message.text
    update.message.reply_text('请输入产品名称 / Please input product name:')
    return SALE_PRODUCT

def sale_product(update: Update, context: CallbackContext) -> str:
    context.user_data['sale_product'] = update.message.text
    update.message.reply_text('请输入出货日期 (格式为DD/MM/YYYY) / Please input shipping date (format DD/MM/YYYY):')
    return SALE_SHIPPING_DATE

def sale_shipping_date(update: Update, context: CallbackContext) -> str:
    context.user_data['sale_shipping_date'] = update.message.text
    update.message.reply_text('请输入出货时间 (格式为HH:MM) / Please input shipping time (format HH:MM):')
    return SALE_SHIPPING_TIME

def sale_shipping_time(update: Update, context: CallbackContext) -> str:
    context.user_data['sale_shipping_time'] = update.message.text
    update.message.reply_text('请输入出库数量 / Please input outbound quantity:')
    return SALE_OUTBOUND_QUANTITY

def sale_outbound_quantity(update: Update, context: CallbackContext) -> str:
    context.user_data['sale_outbound_quantity'] = update.message.text
    update.message.reply_text('请输入单价 / Please input unit price:')
    return SALE_UNIT_PRICE

def sale_unit_price(update: Update, context: CallbackContext) -> str:
    context.user_data['sale_unit_price'] = update.message.text
    update.message.reply_text('请输入销售员 / Please input seller name:')
    return SALE_SELLER

def sale_seller(update: Update, context: CallbackContext) -> str:
    context.user_data['sale_seller'] = update.message.text
    update.message.reply_text('请输入款项 / Please input payment:')
    return SALE_PAYMENT

def sale_payment(update: Update, context: CallbackContext) -> str:
    context.user_data['sale_payment'] = update.message.text
    # 根据收集到的信息做一次汇总确认
    update.message.reply_text(f"请确认信息 / Please confirm the information:\n客户 / Customer: {context.user_data['sale_customer']}\n产品 / Product: {context.user_data['sale_product']}\n出货日期 / Shipping date: {context.user_data['sale_shipping_date']}\n出货时间 / Shipping time: {context.user_data['sale_shipping_time']}\n数量 / Quantity: {context.user_data['sale_outbound_quantity']}\n单价 / Unit price: {context.user_data['sale_unit_price']}\n销售员 / Seller: {context.user_data['sale_seller']}\n款项 / Payment: {context.user_data['sale_payment']}\n确认请回复 'yes' / To confirm, please reply 'yes', 重新输入请回复 'no' / To re-enter, please reply 'no'")
    return SALE_CONFIRMATION

# 确认信息处理
def sale_confirmation(update: Update, context: CallbackContext) -> str:
    if update.message.text.lower() in ['yes', 'y', 'YES', 'Y', 'true', 'T']:
        # 这里可以添加将销售记录添加到数据的逻辑
        sales_msg = sales_manager.add_sale(customer=context.user_data['sale_customer'], product=context.user_data['sale_product'], 
                                           shipping_date=context.user_data['sale_shipping_date'],
                                            time=context.user_data['sale_shipping_time'], outbound_quantity=context.user_data['sale_outbound_quantity'],
                                            unit_price=context.user_data['sale_unit_price'], seller=context.user_data['sale_seller'], 
                                            payment=context.user_data['sale_payment'])
        update.message.reply_text(sales_msg)
        return ConversationHandler.END
    else:
        update.message.reply_text('请输入客户名:')
        return SALE_CUSTOMER

# Get all sales records
def sale_get_all(update: Update, context: CallbackContext) -> None:
    # 调用销售管理对象的方法来获取销售记录
    sales = sales_manager.get_all()
    # 将销售记录转换为字符串
    response = "\n".join([str(sale.to_dict()) for sale in sales])
    # 使用 send_long_text 函数发送长文本
    send_long_text(update.effective_chat.id, response, context.bot)
    return ConversationHandler.END

# Function to start deleting a sale record by ID
def start_delete_sale(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('请输入要删除的销售记录ID / Please enter the sale ID you want to delete:')
    return SALE_DELETE

def delete_sale(update: Update, context: CallbackContext) -> int:
    args = context.args  # Assuming args are passed as: /delete_sale sale_id
    
    if len(args) != 1:
        update.message.reply_text("请输入要删除的销售记录ID / Please provide the sale ID.")
        return
    
    sale_id = args[0]
    deletion_message = sales_manager.delete_sale(sale_id)  # Assuming this method returns a message about the deletion result
    update.message.reply_text(deletion_message)
    return ConversationHandler.END


# Function to start finding a sale record by ID
def start_find_sale(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('请输入要查找的销售记录ID / Please enter the sale ID you want to find:')
    return SALE_FIND

# Function to find a sale record by ID
def find_sale(update: Update, context: CallbackContext) -> int:
    args = update.message.text  # Assuming args are passed as: /find_sale sale_id
    
    if ' ' in args:
        args = args.repalce(' ')

    sale_id = args
    got_it, sale_info = sales_manager.find_sale_by_id(sale_id)  # Assuming this method returns sale information or a message
    # Check if sale_info is a single Sale object
    if got_it:  # Check if sale_info is a list of Sale objects
        response = "\n".join([str(sale.to_dict()) for sale in sale_info])
        response_message = f"Sale records found:\n{response}\n销售记录已找到:\n{response}"
    else:  # If sale_info is None or not found
        response_message = f"No sale record found with ID '{sale_id}'.\n未找到销售ID为 '{sale_id}' 的记录。"
    
    # 使用 send_long_text 函数发送长文本
    send_long_text(update.effective_chat.id, response_message, context.bot)
    return ConversationHandler.END

# Function to start finding sale records by customer name
def start_find_sale_by_customer_name(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('请输入要查找的客户名字 / Please enter the customer name you want to find:')
    return SALE_FIND_CUSTOMER

# Function to find a sale record by customer name
def find_sale_by_customer_name(update: Update, context: CallbackContext) -> int:
    customer = update.message.text  
    got_it, sale_info = sales_manager.find_sales_by_customer(customer) 
    # Check if sale_info is a single Sale object
    if got_it:  # Check if sale_info is a list of Sale objects
        response = "\n".join([str(sale.to_dict()) for sale in sale_info])
        response_message = f"Sale records found:\n{response}\n销售记录已找到:\n{response}"
    else:  # If sale_info is None or not found
        response_message = f"No sale record found with customer name '{customer}'.\n未找到客户名为为 '{customer}' 的记录。"
    
    # 使用 send_long_text 函数发送长文本
    send_long_text(update.effective_chat.id, response_message, context.bot)
    return ConversationHandler.END

"""
###################################################################################
                            Customer 客户记录表
###################################################################################
"""
CUSTOMER_NAME, CUSTOMER_PAYABLE, CUSTOMER_PAYMENT, CUSTOMER_COMFIRMATION = range(4)

def customer_add(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('请输入客户名 / Please input customer name:')
    return CUSTOMER_NAME

def customer_name(update: Update, context: CallbackContext) -> int:
    context.user_data['customer_name'] = update.message.text
    update.message.reply_text('请输入应付金额 / Please input Payable:')
    return CUSTOMER_PAYABLE

def customer_payable(update: Update, context: CallbackContext) -> int:
    context.user_data['customer_payable'] = update.message.text
    update.message.reply_text('请输入实付金额 / Please input Payment:')
    return CUSTOMER_PAYMENT

def customer_payment(update: Update, context: CallbackContext) -> int:
    context.user_data['customer_payment'] = update.message.text
    # update.message.reply_text('请输入欠款金额 / Please input Debt:')
    # return CUSTOMER_DEBT
    # 根据收集到的信息做一次汇总确认
    # update.message.reply_text(f"请确认信息 / Please confirm the information:\n客户 / Customer: {context.user_data['customer_name']}\n应付金额 / Payable: {context.user_data['customer_payable']}\n实付金额 / Payment: {context.user_data['customer_payment']}\n欠款金额 / Debt: {context.user_data['customer_debt']}\n确认请回复 'yes' / To confirm, please reply 'yes', 重新输入请回复 'no' / To re-enter, please reply 'no'")
    # tmp_debt = float(context.user_data['customer_payment']) - float(context.user_data['customer_payable'])
    update.message.reply_text(f"请确认信息 / Please confirm the information:\n客户 / Customer: {context.user_data['customer_name']}\n应付金额 / Payable: {context.user_data['customer_payable']}\n实付金额 / Payment: {context.user_data['customer_payment']}\n确认请回复 'yes' / To confirm, please reply 'yes', 重新输入请回复 'no' / To re-enter, please reply 'no'")
    return CUSTOMER_COMFIRMATION

# 确认信息处理
def customer_confirmation(update: Update, context: CallbackContext) -> str:
    if update.message.text.lower() in ['yes', 'y', 'YES', 'Y', 'true', 'T']:
        # 这里可以添加将销售记录添加到数据的逻辑
        customer_msg = customers_manager.add_customer(customer_name=context.user_data['customer_name'], payable=context.user_data['customer_payable'],
                                            payment=context.user_data['customer_payment'])
        # customer_msg = customers_manager.add_customer(customer=context.user_data['customer_name'], payable=context.user_data['customer_payable'],
        #                                     debt=context.user_data['customer_debt'], payment=context.user_data['customer_payment'])
        update.message.reply_text(customer_msg)
        return ConversationHandler.END
    else:
        update.message.reply_text('请输入客户名:')
        return CUSTOMER_NAME

def get_customers_with_debt(update: Update, context: CallbackContext) -> None:
    # Call the method to get customers with debt
    flag, customers_with_debt = customers_manager.get_customers_with_debt()
    
    # Check if there are any customers with debt
    if flag:
        response = "有欠款的客户 / Customers with outstanding debt:\n"
        for customer in customers_with_debt:
            customer_info = f"- {customer.get_customer()} / Debt 欠款金额: {customer.get_debt()}\n"
            response += customer_info
    else:
        response = "目前没有客户欠款 / No customers with outstanding debt at the moment."
    
    # Send the response back to the user
    send_long_text(update.effective_chat.id, response, context.bot)
    return ConversationHandler.END

# Define states for the conversation
UPDATE_CUSTOMER_NAME, UPDATE_PAYABLE, UPDATE_PAYMENT, UPDATE_CONFIRMATION = range(4)

def update_payment_start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('请输入客户名 / Please input the customer name:')
    return UPDATE_CUSTOMER_NAME

def update_payment_customer_name(update: Update, context: CallbackContext) -> int:
    context.user_data['update_customer_name'] = update.message.text
    update.message.reply_text('请输入应付金额 / Please input the amount payable:')
    return UPDATE_PAYABLE

def update_payment_payable(update: Update, context: CallbackContext) -> int:
    context.user_data['update_payable'] = update.message.text
    update.message.reply_text('请输入新的支付金额 / Please input the new payment amount:')
    return UPDATE_PAYMENT

def update_payment(update: Update, context: CallbackContext) -> int:
    context.user_data['update_payment'] = update.message.text
    # Recap the information for confirmation
    update.message.reply_text(
        f"请确认信息 / Please confirm the information:\n"
        f"客户 / Customer: {context.user_data['update_customer_name']}\n"
        f"应付金额 / Payable: {context.user_data['update_payable']}\n"
        f"新的支付金额 / New payment: {context.user_data['update_payment']}\n"
        f"确认请回复 'yes'，重新输入请回复 'no' / Reply 'yes' to confirm, 'no' to re-enter"
    )
    return UPDATE_CONFIRMATION

def update_payment_confirmation(update: Update, context: CallbackContext) -> int:
    if update.message.text.lower() in ['yes', 'y']:
        response = customers_manager.update_customer_payment(
            context.user_data['update_customer_name'], 
            context.user_data['update_payable'], 
            context.user_data['update_payment']
        )
        update.message.reply_text(response)
        return ConversationHandler.END
    else:
        update.message.reply_text('请输入客户名 / Please input the customer name again:')
        return UPDATE_CUSTOMER_NAME

def get_customers_with_excess_payment_handler(update: Update, context: CallbackContext) -> None:
    flag, customers_with_excess_payment = customers_manager.get_customers_with_excess_payment()
    
    if not flag:
        update.message.reply_text("没有找到超额支付的客户。\nNo customers with excess payments found.")
        return ConversationHandler.END
    
    response = "超额支付的客户列表:\nList of customers with excess payments:\n"
    for customer in customers_with_excess_payment:
        excess_payment = float(customer.get_payment()) - float(customer.get_payable())
        response += f"- 客户 {customer.get_customer()}: 支付了 {customer.get_payment()}，但应付金额仅为 {customer.get_payable()}。超额: {excess_payment}\n"
        response += f"  Customer {customer.get_customer()}: Paid {customer.get_payment()}, but only {customer.get_payable()} was due. Excess: {excess_payment}\n"
    
    send_long_text(update.effective_chat.id, response, context.bot)
    return ConversationHandler.END

CUSTOMER_DELETE_NAME, CUSTOMER_DELETE_CONFIRMATION = range(2)

def customer_delete_start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("请提供客户名以删除。/ Please provide the customer name to delete.")
    return CUSTOMER_DELETE_NAME

def customer_delete_name(update: Update, context: CallbackContext) -> int:
    context.user_data['customer_delete_name'] = update.message.text
    # 请求确认信息
    update.message.reply_text(f"您要删除的客户名是：{context.user_data['customer_delete_name']}\n确认请回复 'yes' / To confirm, please reply 'yes', 重新输入请回复 'no' / To re-enter, please reply 'no'")
    return CUSTOMER_DELETE_CONFIRMATION

def delete_customer_confirmation(update: Update, context: CallbackContext) -> None:
    if update.message.text.lower() in ['yes', 'y']:
        customer_name = context.user_data['customer_delete_name']
        success, response = customers_manager.delete_customer(customer_name)  # 使用此方法
        update.message.reply_text(response)
    else:
        update.message.reply_text('请重新输入客户名 / Please input the customer name again:')
        return CUSTOMER_DELETE_NAME
    return ConversationHandler.END
    

def get_all_customers(update: Update, context: CallbackContext) -> None:
    # Assuming customers_manager is an instance of the Customers class
    all_customers = customers_manager.get_all()
    
    if not all_customers:
        update.message.reply_text("No customers found.")
        return ConversationHandler.END

    # Formatting the list of customers for display
    message = "List of all customers:\n"
    for customer in all_customers:
        customer_info = customer.to_dict()  # Assuming each customer has a to_dict method for easy formatting
        message += f"Customer: {customer_info['Customer']}, Payable: {customer_info['Payable']}, Payment: {customer_info['Payment']}, Debt: {customer_info['Debt']}\n"

    # Sending the formatted message in parts if it's too long
    send_long_text(update.effective_chat.id, message, context.bot)
    return ConversationHandler.END

"""
###################################################################################
                                Inventory 库存登记
###################################################################################
"""
PRODUCT_QUERY = range(1)

def start_get_product_data(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('请输入您想查询的产品名称：/ Please enter the name of the product you want to query:')
    return PRODUCT_QUERY

def product_query(update: Update, context: CallbackContext) -> int:
    product_name = update.message.text
    product_data = inventory_manager.get_product_data(product_name)
    if isinstance(product_data, dict):
        response = '\n'.join([f"{key}: {value}" for key, value in product_data.items()])
    else:
        response = product_data  # If the product was not found, it returns a string message.
    
    update.message.reply_text(response)
    return ConversationHandler.END

PRODUCT_NAME = range(1)

def start_delete_product(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('请输入要删除的产品名称：')
    return PRODUCT_NAME

def delete_product(update: Update, context: CallbackContext) -> int:
    product_name = update.message.text
    response = inventory_manager.delete_product_by_name(product_name)
    update.message.reply_text(response)
    return ConversationHandler.END

def list_all_products(update: Update, context: CallbackContext) -> None:
    all_products = inventory_manager.get_all()  # 调用 get_all 方法获取所有产品信息
    
    # 检查是否有产品
    if not all_products:
        update.message.reply_text("当前库存中没有产品。")
        return ConversationHandler.END
    
    # 格式化产品信息为文本
    message = "当前库存中的所有产品：\n\n"
    for product in all_products:
        product_info = f"{product.get_product_chinese()}：{product.get_product()}，" \
                       f"{product.get_total_inventory_chinese()}：{product.get_total_inventory()}，" \
                       f"{product.get_in_stock_chinese()}：{product.get_in_stock()}\n"
        message += product_info
    
    # 发送长文本可能需要分多次发送
    send_long_text(update.effective_chat.id, message, context.bot)
    return ConversationHandler.END

# 定义状态常量
(PRODUCT_NAME, OPENING_INVENTORY, STOCK_IN, STOCK_OUT, SCHEDULE_INVENTORY, TOTAL_INVENTORY, IN_STOCK, PRODUCT_CONFIRMATION) = range(8)

def start_add_or_update_product(update: Update, context: CallbackContext) -> None:
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
(ARRIVAL_DATE, SUPPLIER, SUPPLIER_PRODUCT, INBOUND_QUANTITY, UNIT_PRICE, TOTAL_PRICE, SUPPLIER_CONFIRMATION) = range(7)

def start_add_warehousing(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("请输入到货日期（格式为DD/MM/YYYY）:")
    return ARRIVAL_DATE

def arrival_date(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    try:
        # 尝试将用户输入的文本解析为日期
        datetime.strptime(text, "%d/%m/%Y")
        context.user_data['arrival_date'] = text
        update.message.reply_text("请输入供应商名称:")
        return SUPPLIER
    except ValueError:
        # 如果解析失败，提示用户输入正确的日期格式
        update.message.reply_text("日期格式不正确，请按照 DD/MM/YYYY 的格式输入，例如 31/12/2020:")
        return ARRIVAL_DATE
    return SUPPLIER

def supplier(update: Update, context: CallbackContext) -> int:
    context.user_data['supplier'] = update.message.text
    update.message.reply_text("请输入产品名称:")
    return SUPPLIER_PRODUCT

def supplier_product(update: Update, context: CallbackContext) -> int:
    context.user_data['supplier_product'] = update.message.text
    update.message.reply_text("请输入入库数量:")
    return INBOUND_QUANTITY

def inbound_quantity(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    try:
        quantity = int(text)
        if quantity > 0:
            context.user_data['inbound_quantity'] = quantity
            update.message.reply_text("请输入单价:")
            return UNIT_PRICE
        else:
            raise ValueError
    except ValueError:
        update.message.reply_text("请输入有效的正整数作为入库数量:")
        return INBOUND_QUANTITY

def unit_price(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    try:
        price = float(text)
        if price > 0:
            context.user_data['unit_price'] = price
            update.message.reply_text("如有，请输入总价，否则回复 '跳过' / 'NONE' :")
            return TOTAL_PRICE
        else:
            raise ValueError
    except ValueError:
        update.message.reply_text("请输入有效的正数作为单价:")
        return UNIT_PRICE

def total_price(update: Update, context: CallbackContext) -> int:
    text = update.message.text.lower()  # 将输入转换为小写以方便比较
    if text == '跳过' or text == 'none':
        context.user_data['total_price'] = None  # 用户选择跳过输入总价
        # 继续下一步，或结束对话
        # 例如，结束对话并给出确认信息
        return confirm_warehousing_information(update, context)  # 假设有一个函数用于确认信息
    else:
        try:
            price = float(text)
            if price > 0:
                context.user_data['total_price'] = price
                # 继续下一步，或结束对话
                # 例如，结束对话并给出确认信息
                return confirm_warehousing_information(update, context)  # 假设有一个函数用于确认信息
            else:
                raise ValueError
        except ValueError:
            update.message.reply_text("请输入有效的正数作为总价，或回复 '跳过' / 'NONE' 跳过此步骤:")
            return TOTAL_PRICE
        
def confirm_warehousing_information(update: Update, context: CallbackContext) -> int:
    # 构建确认信息的字符串
    confirmation_text = "请确认您提供的信息：\n"
    if 'arrival_date' in context.user_data:
        confirmation_text += f"到货日期: {context.user_data['arrival_date']}\n"
    if 'supplier' in context.user_data:
        confirmation_text += f"供应商: {context.user_data['supplier']}\n"
    if 'supplier_product' in context.user_data:
        confirmation_text += f"产品: {context.user_data['supplier_product']}\n"
    if 'inbound_quantity' in context.user_data:
        confirmation_text += f"入库数量: {context.user_data['inbound_quantity']}\n"
    if 'unit_price' in context.user_data:
        confirmation_text += f"单价: {context.user_data['unit_price']}\n"
    if 'total_price' in context.user_data:
        total_price = context.user_data['total_price'] if context.user_data['total_price'] is not None else "未提供"
        confirmation_text += f"总价: {total_price}\n"
    
    # 发送确认信息给用户
    confirmation_text += "确认请回复 'yes'，重新输入请回复 'no'。"
    update.message.reply_text(confirmation_text)
    
    # 返回一个特定状态，通常是一个等待用户确认的状态
    return SUPPLIER_CONFIRMATION

def add_warehousing_confirmation(update: Update, context: CallbackContext) -> int:
    if update.message.text.lower() in ['yes', 'y']:
        result_message = warehousing_manager.add_warehousing_record(
            arrival_date=context.user_data['arrival_date'],
            supplier=context.user_data['supplier'],
            product=context.user_data['supplier_product'],
            inbound_quantity=context.user_data['inbound_quantity'],
            unit_price=context.user_data['unit_price'],
            total_price=context.user_data['total_price']
        )
        update.message.reply_text(result_message)
    else:
        update.message.reply_text("操作已取消。")
    return ConversationHandler.END

DELETE_ARRIVAL_DATE, DELETE_SUPPLIER, DELETE_PRODUCT, DELETE_SUPPLIER_CONFIRMATION = range(4)

def start_delete_warehousing(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("请输入要删除的仓储记录的到货日期（格式为DD/MM/YYYY）：")
    return DELETE_ARRIVAL_DATE

def delete_warehousing_arrival_date(update: Update, context: CallbackContext) -> int:
    context.user_data['delete_arrival_date'] = update.message.text
    update.message.reply_text("请输入供应商名称：")
    return DELETE_SUPPLIER

def delete_warehousing_supplier(update: Update, context: CallbackContext) -> int:
    context.user_data['delete_supplier'] = update.message.text
    update.message.reply_text("请输入产品名称：")
    return DELETE_PRODUCT

def delete_warehousing_product(update: Update, context: CallbackContext) -> int:
    context.user_data['delete_product'] = update.message.text
    update.message.reply_text(f"您要删除的记录信息如下：\n到货日期：{context.user_data['delete_arrival_date']}\n供应商：{context.user_data['delete_supplier']}\n产品名称：{context.user_data['delete_product']}\n请确认是否删除（yes/no）：")
    return DELETE_SUPPLIER_CONFIRMATION

def delete_warehousing_confirmation(update: Update, context: CallbackContext) -> int:
    if update.message.text.lower() in ['yes', 'y']:
        response = warehousing_manager.delete_warehousing_record(context.user_data['delete_arrival_date'], context.user_data['delete_supplier'], context.user_data['delete_product'])
        update.message.reply_text(response)
    else:
        update.message.reply_text("操作已取消。")
    return ConversationHandler.END

UPDATE_ARRIVAL_DATE, UPDATE_SUPPLIER, UPDATE_PRODUCT, UPDATE_NEW_QUANTITY, UPDATE_NEW_UNIT_PRICE, UPDATE_SUPPLIER_CONFIRMATION = range(6)

# 开始更新记录的处理函数
def start_update_warehousing(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("请输入到货日期（格式为DD/MM/YYYY）：")
    return UPDATE_ARRIVAL_DATE

# 处理到货日期的函数
def warehousing_arrival_date(update: Update, context: CallbackContext) -> int:
    context.user_data['update_arrival_date'] = update.message.text
    update.message.reply_text("请输入供应商名：")
    return UPDATE_SUPPLIER

# 处理供应商名的函数
def warehousing_supplier(update: Update, context: CallbackContext) -> int:
    context.user_data['update_supplier'] = update.message.text
    update.message.reply_text("请输入产品名称：")
    return UPDATE_PRODUCT

# 处理产品名称的函数
def warehousing_product(update: Update, context: CallbackContext) -> int:
    context.user_data['update_product'] = update.message.text
    update.message.reply_text("请输入新的入库数量（如果不修改请回复 NONE）：")
    return UPDATE_NEW_QUANTITY

# 处理新的入库数量的函数
def warehousing_new_quantity(update: Update, context: CallbackContext) -> int:
    quantity = update.message.text
    context.user_data['update_new_quantity'] = None if quantity.lower() == 'none' else quantity
    update.message.reply_text("请输入新的单价（如果不修改请回复 NONE）：")
    return UPDATE_NEW_UNIT_PRICE

# 处理新的单价的函数
def warehousing_new_unit_price(update: Update, context: CallbackContext) -> int:
    price = update.message.text
    context.user_data['update_unit_price'] = None if price.lower() == 'none' else price
    # 确认信息
    update.message.reply_text("请确认信息，回复 'yes' 确认更新，回复 'no' 重新输入。")
    return UPDATE_SUPPLIER_CONFIRMATION

# 确认并执行更新的函数
def perform_update_warehousing(update: Update, context: CallbackContext) -> int:
    if update.message.text.lower() == 'yes':
        # 调用更新函数
        message = warehousing_manager.update_inbound_quantity_or_unit_price(
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

FIND_BY_DATE = range(1)

def start_find_by_date(update: Update, context: CallbackContext) -> int:
    """启动对话，询问用户想查询的日期"""
    update.message.reply_text('请输入您想查询的到货日期 (格式为DD/MM/YYYY)：')
    return FIND_BY_DATE

def find_by_date(update: Update, context: CallbackContext) -> int:
    """处理用户输入的日期，并查找匹配的记录"""
    date_str = update.message.text
    try:
        matching_records = warehousing_manager.find_by_date(date_str)
        if matching_records:
            response = "\n".join([f"到货日期: {item.get_arrival_date()}, 产品: {item.get_product()}, 入库数量: {item.get_inbound_quantity()}" for item in matching_records])
            update.message.reply_text(f"找到以下匹配的记录：\n{response}")
        else:
            update.message.reply_text("没有找到匹配的记录。")
    except ValueError as e:
        update.message.reply_text(str(e))
    return ConversationHandler.END

def get_all_warehousing(update: Update, context: CallbackContext) -> None:
    all_records = warehousing_manager.get_all()
    
    if not all_records:
        update.message.reply_text("当前没有入库记录。")
        return

    # 构建回复消息
    reply_message = "所有入库记录：\n"
    for record in all_records:
        reply_message += f"到货日期: {record.get_arrival_date()}, 供应商: {record.get_supplier()}, 产品: {record.get_product()}, 入库数量: {record.get_inbound_quantity()}, 单价: {record.get_unit_price()}, 总价: {record.get_total_price()}\n"

    # 由于消息可能会很长，使用send_long_text函数来分段发送
    send_long_text(update.effective_chat.id, reply_message, context.bot)
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
    
    try:
        
        dispatcher.add_handler(CommandHandler("start", start))

        dispatcher.add_handler(CommandHandler("help", help))

        # 这里用MessageHandler来处理普通消息
        # dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, process_command))

        ########################################### SALES ############################################################
        dispatcher.add_handler(CommandHandler("sale_get_all", sale_get_all))

        conv_handler_sale_start = ConversationHandler(
            entry_points=[CommandHandler('sale_add', sale_start)],
            states={
                SALE_CUSTOMER: [MessageHandler(Filters.text, sale_customer)],
                SALE_PRODUCT: [MessageHandler(Filters.text, sale_product)],
                SALE_SHIPPING_DATE: [MessageHandler(Filters.text, sale_shipping_date)],
                SALE_SHIPPING_TIME: [MessageHandler(Filters.text, sale_shipping_time)],
                SALE_OUTBOUND_QUANTITY: [MessageHandler(Filters.text, sale_outbound_quantity)],
                SALE_UNIT_PRICE: [MessageHandler(Filters.text, sale_unit_price)],
                SALE_SELLER: [MessageHandler(Filters.text, sale_seller)],
                SALE_PAYMENT: [MessageHandler(Filters.text, sale_payment)],
                SALE_CONFIRMATION: [MessageHandler(Filters.regex('^(yes|no)$'), sale_confirmation)]
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )

        dispatcher.add_handler(conv_handler_sale_start)
        # dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, process_command))

        conv_handler_sale_delete = ConversationHandler(
            entry_points=[CommandHandler('delete_sale', start_delete_sale)],
            states={
                SALE_DELETE: [MessageHandler(Filters.text & ~Filters.command, delete_sale)],
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )

        dispatcher.add_handler(conv_handler_sale_delete)

        # Add find sale conversation handler to dispatcher
        conv_handler_sales_find_by_customer = ConversationHandler(
            entry_points=[CommandHandler('sale_find_customer', start_find_sale_by_customer_name)],
            states={
                SALE_FIND_CUSTOMER: [MessageHandler(Filters.text & ~Filters.command, find_sale_by_customer_name)],
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )

        dispatcher.add_handler(conv_handler_sales_find_by_customer)
        

        ################################################# Customer ######################################################
        conv_handler_customer_add = ConversationHandler(
            entry_points=[CommandHandler('customer_add', customer_add)],
            states={
                CUSTOMER_NAME: [MessageHandler(Filters.text, customer_name)],
                CUSTOMER_PAYABLE: [MessageHandler(Filters.text, customer_payable)],
                CUSTOMER_PAYMENT: [MessageHandler(Filters.text, customer_payment)],
                # CUSTOMER_DEBT: [MessageHandler(Filters.text, customer_debt)],                
                CUSTOMER_COMFIRMATION: [MessageHandler(Filters.regex('^(yes|no)$'), customer_confirmation)]
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )

        dispatcher.add_handler(conv_handler_customer_add)

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

        dispatcher.add_handler(CommandHandler('cts_excess_payment', get_customers_with_excess_payment_handler))

        conv_handler_delete_customer = ConversationHandler(
            entry_points=[CommandHandler('delete_customer', customer_delete_start)],
            states={
                CUSTOMER_DELETE_NAME: [MessageHandler(Filters.text, customer_delete_name)],
                CUSTOMER_DELETE_CONFIRMATION: [MessageHandler(Filters.regex('^(yes|no)$'), delete_customer_confirmation)],
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )

        dispatcher.add_handler(conv_handler_delete_customer)

        dispatcher.add_handler(CommandHandler("get_all_customers", get_all_customers))

        ########################################### Inventory ###########################################
        conv_handler_get_product_data = ConversationHandler(
            entry_points=[CommandHandler('get_product_data', start_get_product_data)],
            states={
                PRODUCT_QUERY: [MessageHandler(Filters.text & ~Filters.command, product_query)],
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )

        dispatcher.add_handler(conv_handler_get_product_data)

        conv_handler_inventory_delete = ConversationHandler(
            entry_points=[CommandHandler('delete_product', start_delete_product)],
            states={PRODUCT_NAME: [MessageHandler(Filters.text & ~Filters.command, delete_product)]},
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

        ######################################### Warehousing #########################################
        conv_handler_add_warehousing = ConversationHandler(
            entry_points=[CommandHandler('add_warehousing', start_add_warehousing)],
            states={
                ARRIVAL_DATE: [MessageHandler(Filters.text & ~Filters.command, arrival_date)],
                SUPPLIER: [MessageHandler(Filters.text & ~Filters.command, supplier)],
                SUPPLIER_PRODUCT: [MessageHandler(Filters.text & ~Filters.command, supplier_product)],
                INBOUND_QUANTITY: [MessageHandler(Filters.text & ~Filters.command, inbound_quantity)],
                UNIT_PRICE: [MessageHandler(Filters.text & ~Filters.command, unit_price)],
                TOTAL_PRICE: [MessageHandler(Filters.text & ~Filters.command, total_price)],
                SUPPLIER_CONFIRMATION: [MessageHandler(Filters.text & ~Filters.command, add_warehousing_confirmation)],
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )

        dispatcher.add_handler(conv_handler_add_warehousing)

        delete_warehousing_conv_handler = ConversationHandler(
            entry_points=[CommandHandler('delete_warehousing', start_delete_warehousing)],
            states={
                DELETE_ARRIVAL_DATE: [MessageHandler(Filters.text & ~Filters.command, delete_warehousing_arrival_date)],
                DELETE_SUPPLIER: [MessageHandler(Filters.text & ~Filters.command, delete_warehousing_supplier)],
                DELETE_PRODUCT: [MessageHandler(Filters.text & ~Filters.command, delete_warehousing_product)],
                DELETE_SUPPLIER_CONFIRMATION: [MessageHandler(Filters.regex('^(yes|no)$'), delete_warehousing_confirmation)]
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )

        dispatcher.add_handler(delete_warehousing_conv_handler)


        update_warehousing_conv_handler = ConversationHandler(
            entry_points=[CommandHandler('update_warehousing', start_update_warehousing)],
            states={
                UPDATE_ARRIVAL_DATE: [MessageHandler(Filters.text & ~Filters.command, warehousing_arrival_date)],
                UPDATE_SUPPLIER: [MessageHandler(Filters.text & ~Filters.command, warehousing_supplier)],
                UPDATE_PRODUCT: [MessageHandler(Filters.text & ~Filters.command, warehousing_product)],
                UPDATE_NEW_QUANTITY: [MessageHandler(Filters.text & ~Filters.command, warehousing_new_quantity)],
                UPDATE_NEW_UNIT_PRICE: [MessageHandler(Filters.text & ~Filters.command, warehousing_new_unit_price)],
                UPDATE_SUPPLIER_CONFIRMATION: [MessageHandler(Filters.regex('^(yes|no)$'), perform_update_warehousing)]
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )

        dispatcher.add_handler(update_warehousing_conv_handler)

        conv_handler_find_inventory_by_date = ConversationHandler(
            entry_points=[CommandHandler('find_inventory_by_date', start_find_by_date)],
            states={
                FIND_BY_DATE: [MessageHandler(Filters.text & ~Filters.command, find_by_date)],
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )

        dispatcher.add_handler(conv_handler_find_inventory_by_date)

        get_all_warehousing_handler = CommandHandler('get_all_warehousing', get_all_warehousing)
        dispatcher.add_handler(get_all_warehousing_handler)
        
        #######################################################################################################
        # 开始Bot
        updater.start_polling()

        # 一直运行直到按Ctrl-C或进程收到SIGINT, SIGTERM或SIGABRT。这应该在大多数情况下用于非异步应用程序。
        updater.idle()
    except Exception or TypeError or AttributeError as e:
        error_message = f"发生错误：{e}"
        updater.message.reply_text(error_message)
        updater.message.reply_text('尽管发生了错误，但我们可以继续进行其他操作。请输入下一步命令。')
        

if __name__ == '__main__':
    main()
