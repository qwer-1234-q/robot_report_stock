from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, CallbackQueryHandler
import json
import os 
import telebot
import requests
import logging 

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

def build_date_keyboard():
    today = datetime.date.today()
    keyboard = [
        [InlineKeyboardButton(text=today.strftime('%d/%m/%Y'), callback_data='date_' + today.strftime('%d/%m/%Y'))]
    ]
    return InlineKeyboardMarkup(keyboard)

def help(update: Update, context: CallbackContext) -> int:
    command_list = [
        "/start - 开始与机器人的对话。",
        "/sale_add - 添加新的销售记录。",
        "/sale_get_all - 获取所有销售记录。",
        "/sale_delete - 删除指定销售ID的记录。",
        "/sale_find - 根据销售ID查找销售记录。",
        "/customer_add - 添加新客户及其付款信息。",
        "/get_customers_with_debt - 查找有欠款的客户。",
        "/update_payment - 更新客户付款信息。",
        "/get_all_customers - 获取所有客户记录。",
        "/get_product_data - 获取指定产品的详细信息。",
        "/add_product_name - 只添加产品名称",
        "/add_or_update_product - 添加或更新产品信息。",
        "/delete_product - 删除指定的产品记录。",
        "/list_all_products - 列出所有产品信息。",
        "/add_warehousing - 添加仓库入库记录。",
        "/delete_warehousing - 删除仓库入库记录。",
        "/update_warehousing - 更新仓库入库记录信息。",
        "/get_all_warehousing - 获取所有仓库入库记录。",
        "/find_by_date - 根据到货日期查找入库记录。",
        "请使用这些命令与机器人进行交互。"
    ]
    # 将命令列表连接成单个字符串消息
    help_message = "\n".join(command_list)
    send_long_text(update.effective_chat.id, help_message, context.bot)
    return ConversationHandler.END

"""
###################################################################################
                            Sales records 销售记录表
###################################################################################
"""
SALE_CUSTOMER, SALE_PRODUCT, SALE_SHIPPING_DATE, SALE_STOCK_OUT, SALE_UNIT_PRICE, SALE_SELLER, SALE_PAYMENT, SALE_CONFIRMATION = range(8)

def sale_start(update: Update, context: CallbackContext) -> str:
    # 获取已知的客户列表
    customer_list = customers_manager.get_customer_name_list()  # 示例客户列表，实际应根据情况替换为真实数据
    # 创建客户名的按钮列表
    buttons = [InlineKeyboardButton(name, callback_data=name) for name in customer_list]
    # 将按钮列表分为一行一行
    keyboard = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    # 创建 InlineKeyboardMarkup 对象
    reply_markup = InlineKeyboardMarkup(keyboard)
    # 发送消息并附带按钮
    update.message.reply_text('请选择客户名：', reply_markup=reply_markup)
    # 返回下一个对话状态
    return SALE_CUSTOMER

def sale_customer(update: Update, context: CallbackContext) -> str:
    # 获取用户选择的客户名
    selected_customer = update.callback_query.data
    # 将选择的客户名保存到用户数据中
    context.user_data['sale_customer'] = selected_customer
    # 发送带有产品名称按钮的消息
    keyboard = inventory_manager.get_product_list()
    update.callback_query.message.reply_text('请选择或输入产品名称：', reply_markup=keyboard)
    # 返回下一个对话状态
    return SALE_PRODUCT

def sale_product(update: Update, context: CallbackContext) -> str:
    query = update.callback_query
    query.answer()
    # 从回调查询中获取产品名称
    selected_product = query.data
    # 保存选定的产品名称
    context.user_data['sale_product'] = selected_product
    # 这里继续你的对话流程，比如请求下一个输入
    query.edit_message_text(text=f"已选择产品：{selected_product}\n请输入出货日期 (格式为DD/MM/YYYY):")
    return SALE_SHIPPING_DATE

def sale_shipping_date(update: Update, context: CallbackContext) -> str:
    update.message.reply_text('请选择出货日期：', reply_markup=build_date_keyboard())
    return SALE_STOCK_OUT  # 保持状态，直到用户选择日期

def date_selected(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    selected_date = query.data.replace('date_', '')
    context.user_data['sale_shipping_date'] = selected_date
    query.edit_message_text(text=f"已选择日期：{selected_date}\n请输入出库数量：")
    return SALE_STOCK_OUT

def sale_stock_out(update: Update, context: CallbackContext) -> str:
    context.user_data['sale_stock_out'] = update.message.text
    update.message.reply_text('请输入单价:')
    return SALE_UNIT_PRICE

def sale_unit_price(update: Update, context: CallbackContext) -> int:
    context.user_data['sale_unit_price'] = update.message.text
    # 假设已经有一个销售员列表
    seller_list = sales_manager.get_seller_name_list()  # 假设这个方法可以提供销售员的名单
    buttons = [InlineKeyboardButton(seller, callback_data=seller) for seller in seller_list]
    keyboard = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('请选择销售员：', reply_markup=reply_markup)
    return SALE_SELLER

def sale_seller(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    selected_seller = query.data
    context.user_data['sale_seller'] = selected_seller
    query.edit_message_text(text=f"已选择销售员：{selected_seller}\n请输入款项：")
    return SALE_PAYMENT

def sale_payment(update: Update, context: CallbackContext) -> str:
    context.user_data['sale_payment'] = update.message.text
    # 根据收集到的信息生成确认信息
    confirmation_message = generate_new_sale_confirmation_message(context.user_data)
    # 创建确认和取消的按钮
    keyboard = [
        [InlineKeyboardButton("确认", callback_data='confirm')],
        [InlineKeyboardButton("重新输入", callback_data='reenter')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # 发送带有按钮的确认信息
    update.message.reply_text(confirmation_message, reply_markup=reply_markup)
    return SALE_CONFIRMATION

# 生成确认信息的辅助函数
def generate_new_sale_confirmation_message(user_data):
    message = "请确认以下信息：\n"
    message += f"客户名：{user_data['sale_customer']}\n"
    message += f"产品名称：{user_data['sale_product']}\n"
    message += f"出货日期：{user_data['sale_shipping_date']}\n"
    message += f"出库数量：{user_data['sale_stock_out']}\n"
    message += f"单价：{user_data['sale_unit_price']}\n"
    message += f"销售员：{user_data['sale_seller']}\n"
    message += f"款项：{user_data['sale_payment']}\n"
    message += "\n请回复 'yes' 确认，回复 'no' 重新输入。"
    return message

# 提交销售记录的辅助函数
def submit_sale_record(user_data):
    customer = user_data['sale_customer']
    product = user_data['sale_product']
    shipping_date = user_data['sale_shipping_date']
    stock_out = int(user_data['sale_stock_out'])
    unit_price = float(user_data['sale_unit_price'])
    seller = user_data['sale_seller']
    payment = float(user_data['sale_payment'])
    sales_manager.add_sale(customer, product, shipping_date, stock_out, unit_price, seller, payment)

# 确认信息处理
def sale_confirmation(update: Update, context: CallbackContext) -> int:
    # 获取用户的确认信息
    query = update.callback_query
    query.answer()
    # 根据按钮的回调数据处理用户的选择
    if query.data == 'confirm':
        # 用户确认了信息，处理销售记录的添加逻辑
        sales_msg = submit_sale_record(context.user_data)  # 假设这是添加销售记录的函数
        query.edit_message_text(text=sales_msg)
        return ConversationHandler.END
    elif query.data == 'reenter':
        # 用户选择重新输入，指引用户从头开始
        query.edit_message_text(text="请重新开始输入销售信息。")
        return sale_start(update, context)  # 假设sale_start是开始销售对话流程的函数

# Get all sales records
# 获取所有销售记录
def sale_get_all(update: Update, context: CallbackContext) -> None:
    # 调用销售管理对象的方法来获取销售记录
    sales = sales_manager.get_all()
    # 检查是否有销售记录
    if not sales:
        update.message.reply_text("当前没有销售记录。")
        return ConversationHandler.END
    
    # 将销售记录格式化为字符串
    response_lines = []
    for sale in sales:
        sale_info = sale.to_dict()  # 假设有一个转换为字典的方法
        sale_line = f"销售ID: {sale_info['Sale ID']},客户: {sale_info['Customer']}, "
        sale_line += f"\n产品: {sale_info['Product']}, \n出货日期: {sale_info['Shipping Date']}, "
        sale_line += f"\n出库数量: {sale_info['Stock Out']}, \n单价: {sale_info['Unit Price']}, "
        sale_line += f"\n总价: {sale_info['Total Price']}, \n销售员: {sale_info['Seller']}, "
        sale_line += f"\n支付: {sale_info['Payment']}"
        response_lines.append(sale_line)
    
    # 将所有销售记录的字符串连接起来
    response = "\n\n".join(response_lines)
    
    # 使用 send_long_text 函数发送长文本
    send_long_text(update.effective_chat.id, response, context.bot)
    return ConversationHandler.END

SALE_DELETE, SALE_FIND, SALE_FIND_CUSTOMER = range(3)

# Function to start deleting a sale record by ID
def start_delete_sale(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('请输入要删除的销售记录ID:')
    return SALE_DELETE

def delete_sale(update: Update, context: CallbackContext) -> int:
    args = context.args  # Assuming args are passed as: /delete_sale sale_id
    
    if len(args) != 1:
        update.message.reply_text("请输入要删除的销售记录ID")
        return
    
    sale_id = args[0]
    deletion_message = sales_manager.delete_sale(sale_id)  # Assuming this method returns a message about the deletion result
    update.message.reply_text(deletion_message)
    return ConversationHandler.END

# Function to start finding a sale record by ID
def start_find_sale(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('请输入要查找的销售记录ID:')
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
        response_message = f"销售记录已找到:\n{response}"
    else:  # If sale_info is None or not found
        response_message = f"未找到销售ID为 '{sale_id}' 的记录。"
    
    # 使用 send_long_text 函数发送长文本
    send_long_text(update.effective_chat.id, response_message, context.bot)
    return ConversationHandler.END

# Function to start finding sale records by customer name
def start_find_sale_by_customer_name(update: Update, context: CallbackContext) -> int:
    # 假设这是一个从销售记录中获取所有客户名字的列表
    customer_list = sales_manager.get_customer_name_list()
    # 添加一个手动输入的选项
    customer_list.append("手动输入客户名")
    
    # 创建客户名的按钮列表
    buttons = [InlineKeyboardButton(name, callback_data=name) for name in customer_list]
    # 将按钮列表分为一行一行
    keyboard = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    # 创建 InlineKeyboardMarkup 对象
    reply_markup = InlineKeyboardMarkup(keyboard)
    # 发送消息并附带按钮
    update.message.reply_text('请选择或输入客户名字：', reply_markup=reply_markup)
    return SALE_FIND_CUSTOMER

def handle_customer_selection(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    selected_customer = query.data
    if selected_customer == "手动输入客户名":
        query.edit_message_text(text="请输入客户名字：")
        return SALE_FIND_CUSTOMER
    else:
        # 直接调用查找销售记录的逻辑
        return find_sale_by_customer_name_with_data(update, context, selected_customer)

# Function to find a sale record by customer name
def find_sale_by_customer_name_with_data(update: Update, context: CallbackContext, customer: str) -> int:
    got_it, sale_info = sales_manager.find_sales_by_customer(customer) 
    if got_it:
        response = "\n".join([str(sale.to_dict()) for sale in sale_info])
        response_message = f"找到的销售记录：\n{response}"
    else:
        response_message = f"未找到客户名为 '{customer}' 的记录。"
    send_long_text(update.effective_chat.id, response_message, context.bot)
    return ConversationHandler.END

"""
###################################################################################
                            Customer 客户记录表
###################################################################################
"""
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

def get_customers_with_excess_payment_handler(update: Update, context: CallbackContext) -> None:
    flag, customers_with_excess_payment = customers_manager.get_customers_with_excess_payment()
    
    if not flag:
        update.message.reply_text("没有找到超额支付的客户。")
        return ConversationHandler.END
    
    response = "超额支付的客户列表:\n"
    for customer in customers_with_excess_payment:
        excess_payment = float(customer.get_payment()) - float(customer.get_payable())
        response += f"- 客户 {customer.get_customer()}: 支付了 {customer.get_payment()}，但应付金额仅为 {customer.get_payable()}。超额: {excess_payment}\n"
        
    send_long_text(update.effective_chat.id, response, context.bot)
    return ConversationHandler.END

CUSTOMER_DELETE_NAME, CUSTOMER_DELETE_CONFIRMATION = range(2)

def customer_delete_start(update: Update, context: CallbackContext) -> int:
    # 假设有一个方法返回所有客户名列表
    customer_list = customers_manager.get_customer_name_list()
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
    
# Get all customers
def get_all_customers(update: Update, context: CallbackContext) -> None:
    all_customers = customers_manager.get_all()
    
    if not all_customers:
        update.message.reply_text("没有找到客户。")
        return ConversationHandler.END

    # 格式化客户列表以便显示
    message = "所有客户列表：\n"
    for customer in all_customers:
        customer_info = customer.to_dict()  # 假设每个客户都有一个 to_dict 方法以便格式化
        message += f"客户名：{customer_info['Customer']}, 应付金额：{customer_info['Payable']}元, 实付金额：{customer_info['Payment']}元, 欠款金额：{customer_info['Debt']}元\n"

    # 如果信息太长，则分段发送
    send_long_text(update.effective_chat.id, message, context.bot)
    return ConversationHandler.END

"""
###################################################################################
                                Inventory 库存登记
###################################################################################
"""
PRODUCT_QUERY = range(1)

def start_get_product_data(update: Update, context: CallbackContext) -> int:
    product_list = inventory_manager.get_product_list()
    keyboard = [[InlineKeyboardButton(product, callback_data=product)] for product in product_list]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('请选择您想查询的产品名称：', reply_markup=reply_markup)
    return PRODUCT_QUERY

def product_query(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()  # 确认收到回调查询
    product_name = query.data
    product_data = inventory_manager.get_product_data(product_name)
    
    if isinstance(product_data, dict):
        response = '\n'.join([f"{key}: {value}" for key, value in product_data.items()])
    else:
        response = f"未找到产品：{product_name}"
    
    query.edit_message_text(text=response)
    return ConversationHandler.END

DELETE_PRODUCT = range(1)

def start_delete_product(update: Update, context: CallbackContext) -> int:
    # 假设这是你的产品列表
    product_list = inventory_manager.get_product_list()
    
    # 创建按钮列表
    keyboard = [[InlineKeyboardButton(product, callback_data=product)] for product in product_list]
    
    # 创建 InlineKeyboardMarkup 对象
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # 发送消息并附带按钮
    update.message.reply_text('请选择您要删除的产品名称：', reply_markup=reply_markup)

    return DELETE_PRODUCT

def delete_product(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    
    # 必须调用 answer
    query.answer()
    
    # 获取选择的产品名称
    selected_product = query.data
    
    # 在这里添加删除产品的逻辑
    response = inventory_manager.delete_product_by_name(selected_product)
    response = f"已删除产品：{selected_product}"
    
    # 向用户发送响应
    query.edit_message_text(text=response)

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

ENTER_PRODUCT_NAME = range(1)

def add_product_name(update: Update, context: CallbackContext) -> int:
    """开始添加或更新产品的对话"""
    update.message.reply_text('请输入产品名称：')
    return ENTER_PRODUCT_NAME

def enter_product_name(update: Update, context: CallbackContext) -> int:
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
(WAREHOUSING_ARRIVAL_DATE, WAREHOUSING_SUPPLIER, SUPPLIER_PRODUCT, WAREHOUSING_STOCK_IN, WAREHOUSING_UNIT_PRICE, WAREHOUSING_TOTAL_PRICE, SUPPLIER_CONFIRMATION) = range(7)
(CHOOSE_SUPPLIER_METHOD, MANUAL_INPUT_SUPPLIER, SUPPLIER_PRODUCT) = range(3)
(CHOOSE_PRODUCT_METHOD, MANUAL_INPUT_PRODUCT, WAREHOUSING_STOCK_IN) = range(3)

def get_supplier_buttons(suppliers):
    buttons = [InlineKeyboardButton(supplier, callback_data=supplier) for supplier in suppliers]
    buttons.append(InlineKeyboardButton("手动输入", callback_data="manual_input_supplier"))
    return InlineKeyboardMarkup([buttons])

def get_product_buttons(products):
    buttons = [InlineKeyboardButton(product, callback_data=product) for product in products]
    buttons.append(InlineKeyboardButton("手动输入", callback_data="manual_input_product"))
    return InlineKeyboardMarkup([buttons])

def start_add_warehousing(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("请选择到货日期:", reply_markup=build_date_keyboard())
    return WAREHOUSING_ARRIVAL_DATE

def arrival_date(update, context):
    query = update.callback_query
    query.answer()
    context.user_data['warehousing_arrival_date'] = query.data

    # 创建选择手动输入或从列表选择的按钮
    keyboard = [
        [InlineKeyboardButton("手动输入供应商", callback_data='manual_input_supplier')],
        [InlineKeyboardButton("从列表中选择供应商", callback_data='choose_from_list_supplier')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="请选择供应商输入方式:", reply_markup=reply_markup)

    return CHOOSE_SUPPLIER_METHOD

def choose_supplier_method(update, context):
    query = update.callback_query
    query.answer()

    if query.data == 'manual_input_supplier':
        query.edit_message_text(text="请输入供应商名称:")
        return MANUAL_INPUT_SUPPLIER
    elif query.data == 'choose_from_list_supplier':
        suppliers = warehousing_manager.get_supplier_list()  # 获取供应商列表
        keyboard = [[InlineKeyboardButton(supplier, callback_data=supplier)] for supplier in suppliers]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="请选择供应商名称:", reply_markup=reply_markup)
        return SUPPLIER_PRODUCT

def manual_input_supplier(update, context):
    text = update.message.text
    context.user_data['supplier'] = text
    products = inventory_manager.get_product_list()  # 获取产品列表
    keyboard = [[InlineKeyboardButton(product, callback_data=product)] for product in products]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text="请选择产品名称:", reply_markup=reply_markup)
    return SUPPLIER_PRODUCT

def supplier(update, context):
    query = update.callback_query
    query.answer()
    context.user_data['supplier'] = query.data

    # 创建选择手动输入或从列表选择的按钮
    keyboard = [
        [InlineKeyboardButton("手动输入产品", callback_data='manual_input_product')],
        [InlineKeyboardButton("从列表中选择产品", callback_data='choose_from_list_product')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="请选择产品输入方式:", reply_markup=reply_markup)

    return CHOOSE_PRODUCT_METHOD

def choose_product_method(update, context):
    query = update.callback_query
    query.answer()

    if query.data == 'manual_input_product':
        query.edit_message_text(text="请输入产品名称:")
        return MANUAL_INPUT_PRODUCT
    elif query.data == 'choose_from_list_product':
        products = inventory_manager.get_product_list()  # 获取产品列表
        keyboard = [[InlineKeyboardButton(product, callback_data=product)] for product in products]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text="请选择产品名称:", reply_markup=reply_markup)
        return WAREHOUSING_STOCK_IN

def supplier_product(update, context):
    query = update.callback_query
    query.answer()
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

def manual_input_product(update, context):
    text = update.message.text
    context.user_data['supplier_product'] = text
    update.message.reply_text(text="请输入入库数量:")
    return WAREHOUSING_STOCK_IN

def warehousing_stock_in(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    try:
        quantity = int(text)
        if quantity > 0:
            context.user_data['warehousing_stock_in'] = quantity
            update.message.reply_text("请输入单价:")
            return WAREHOUSING_UNIT_PRICE
        else:
            raise ValueError
    except ValueError:
        update.message.reply_text("请输入有效的正整数作为入库数量:")
        return WAREHOUSING_STOCK_IN

def warehousing_unit_price(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    try:
        price = float(text)
        if price > 0:
            context.user_data['warehousing_unit_price'] = price
                    
            # 例如，结束对话并给出确认信息
            return confirm_warehousing_information(update, context)  # 假设有一个函数用于确认信息
        else:
            raise ValueError
    except ValueError:
        update.message.reply_text("请输入有效的正数作为单价:")
        return WAREHOUSING_UNIT_PRICE

def confirm_warehousing_information(update, context):
    query = update.callback_query
    query.answer()
    confirmation_text = "请确认您提供的信息：\n"
    confirmation_text += f"到货日期: {context.user_data['arrival_date']}\n"
    confirmation_text += f"供应商: {context.user_data['supplier']}\n"

    # 检查是否用户已经手动输入了产品名称
    if context.user_data.get('manual_input_for_product', False):
        confirmation_text += f"产品: {context.user_data.get('supplier_product', '未提供')}\n"
    else:
        confirmation_text += f"产品: {context.user_data.get('supplier_product', '未选择')}\n"
    
    confirmation_text += f"入库数量: {context.user_data['warehousing_stock_in']}\n"
    confirmation_text += f"单价: {context.user_data['warehousing_unit_price']}\n"

    keyboard = [[InlineKeyboardButton("确认", callback_data='confirm'), 
                 InlineKeyboardButton("取消", callback_data='cancel')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=confirmation_text, reply_markup=reply_markup)

    return SUPPLIER_CONFIRMATION

def confirm_warehousing(update, context):
    query = update.callback_query
    query.answer()
    if query.data == 'confirm':
        # 用户确认了信息，进行数据添加操作
        result_message = inventory_manager.add_warehousing_record(
            arrival_date=context.user_data['arrival_date'],
            supplier=context.user_data['supplier'],
            product=context.user_data.get('product', '未提供'),  # 如果用户手动输入产品名称，从context.user_data中获取
            stock_in=context.user_data['warehousing_stock_in'],
            unit_price=context.user_data['warehousing_unit_price'],
        )
        query.edit_message_text(text=result_message)
    else:
        # 用户取消操作
        query.edit_message_text(text="操作已取消。")
    
    return ConversationHandler.END

DELETE_ARRIVAL_DATE, DELETE_SUPPLIER, DELETE_PRODUCT, DELETE_SUPPLIER_CONFIRMATION = range(4)

(DELETE_ARRIVAL_DATE, DELETE_SUPPLIER, DELETE_PRODUCT, DELETE_SUPPLIER_CONFIRMATION) = range(4)

def build_date_keyboard():
    # 生成日期选择键盘，这里仅为示例，您可能需要生成实际的日期列表
    keyboard = [[InlineKeyboardButton("日期1", callback_data='2022-01-01')],
                [InlineKeyboardButton("日期2", callback_data='2022-01-02')],
                [InlineKeyboardButton("取消", callback_data='cancel')]]
    return InlineKeyboardMarkup(keyboard)

def build_selection_keyboard(options, callback_prefix):
    # 根据选项列表生成选择键盘
    keyboard = [[InlineKeyboardButton(option, callback_data=f"{callback_prefix}_{option}")] for option in options]
    keyboard.append([InlineKeyboardButton("取消", callback_data='cancel')])
    return InlineKeyboardMarkup(keyboard)

def start_delete_warehousing(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("请选择要删除的仓储记录的到货日期：", reply_markup=build_date_keyboard())
    return DELETE_ARRIVAL_DATE

def delete_warehousing_arrival_date(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    if query.data == 'cancel':
        query.edit_message_text("操作已取消。")
        return ConversationHandler.END
    context.user_data['delete_arrival_date'] = query.data
    suppliers = warehousing_manager.get_supplier_list()  # 假设有此函数获取供应商列表
    query.edit_message_text("请选择供应商名称：", reply_markup=build_selection_keyboard(suppliers, 'supplier'))
    return DELETE_SUPPLIER

def delete_warehousing_supplier(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    if query.data.startswith('supplier_'):
        context.user_data['delete_supplier'] = query.data.split('_', 1)[1]
        products = warehousing_manager.get_product_list()  # 假设有此函数获取产品列表
        query.edit_message_text("请选择产品名称：", reply_markup=build_selection_keyboard(products, 'product'))
        return DELETE_PRODUCT
    elif query.data == 'cancel':
        query.edit_message_text("操作已取消。")
        return ConversationHandler.END

def delete_warehousing_product(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    if query.data.startswith('product_'):
        context.user_data['delete_product'] = query.data.split('_', 1)[1]
        # 构建确认删除的消息和键盘
        confirmation_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("确认", callback_data='confirm_delete'), InlineKeyboardButton("取消", callback_data='cancel')]])
        query.edit_message_text(f"您要删除的记录信息如下：\n到货日期：{context.user_data['delete_arrival_date']}\n供应商：{context.user_data['delete_supplier']}\n产品名称：{context.user_data['delete_product']}\n请确认是否删除：", reply_markup=confirmation_keyboard)
        return DELETE_SUPPLIER_CONFIRMATION
    elif query.data == 'cancel':
        query.edit_message_text("操作已取消。")
        return ConversationHandler.END

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

FIND_BY_DATE = range(1)

def start_find_by_date(update: Update, context: CallbackContext) -> int:
    """启动对话，询问用户想查询的日期"""
    update.message.reply_text('请选择日期:', reply_markup=build_date_keyboard())
    return FIND_BY_DATE

def find_by_date(update: Update, context: CallbackContext) -> int:
    """处理用户输入的日期，并查找匹配的记录"""
    query = update.callback_query
    query.answer()
    selected_date = query.data
    context.user_data['selected_date'] = selected_date

    # 根据选择的日期查找记录
    matching_records = warehousing_manager.find_by_date(selected_date)
    if matching_records:
        response = "\n\n".join([f"到货日期: {item.get_arrival_date()}, \n产品: {item.get_product()}, \n入库数量: {item.get_stock_out()}" for item in matching_records])
        query.edit_message_text(text=f"找到以下匹配的记录：\n{response}")
    else:
        query.edit_message_text(text="没有找到匹配的记录。")
    return ConversationHandler.END

def get_all_warehousing(update: Update, context: CallbackContext) -> None:
    all_records = warehousing_manager.get_all()
    
    if not all_records:
        update.message.reply_text("当前没有入库记录。")
        return

    # 构建回复消息
    reply_message = "所有入库记录：\n"
    for record in all_records:
        reply_message += f"\n到货日期: {record.get_arrival_date()}, \n供应商: {record.get_supplier()}, \n产品: {record.get_product()}, \n入库数量: {record.get_stock_out()}, 单价: {record.get_unit_price()}, 总价: {record.get_total_price()}\n"

    # 由于消息可能会很长, 使用send_long_text函数来分段发送
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
    dp = updater.dispatcher

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    try:
        
        dispatcher.add_handler(CommandHandler("start", start))

        dispatcher.add_handler(CommandHandler("help", help))

        # 这里用MessageHandler来处理普通消息
        # dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, process_command))

        ########################################### SALES ############################################################
        dispatcher.add_handler(CommandHandler("sale_get_all", sale_get_all))

        conv_handler_sale_start = ConversationHandler(
            entry_points=[CommandHandler('start_sale', sale_start)],
            states={
                SALE_CUSTOMER: [CallbackQueryHandler(sale_customer)],
                SALE_PRODUCT: [CallbackQueryHandler(sale_product)],
                SALE_SHIPPING_DATE: [CallbackQueryHandler(date_selected)],
                SALE_STOCK_OUT: [MessageHandler(Filters.text, sale_stock_out)],
                SALE_UNIT_PRICE: [MessageHandler(Filters.text, sale_unit_price)],
                SALE_SELLER: [MessageHandler(Filters.text, sale_seller)],
                SALE_PAYMENT: [MessageHandler(Filters.text, sale_payment)],
                SALE_CONFIRMATION: [MessageHandler(Filters.text, sale_confirmation)]
            },
            fallbacks=[]
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
                SALE_FIND_CUSTOMER: [MessageHandler(Filters.text & ~Filters.command, find_sale_by_customer_name_with_data)],
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )

        dispatcher.add_handler(conv_handler_sales_find_by_customer)
        
        dispatcher.add_handler(CallbackQueryHandler(start_find_sale_by_customer_name))

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

        dispatcher.add_handler(CommandHandler('cts_excess_payment', get_customers_with_excess_payment_handler))

        # conv_handler_delete_customer = ConversationHandler(
        #     entry_points=[CommandHandler('delete_customer', customer_delete_start)],
        #     states={
        #         CUSTOMER_DELETE_NAME: [MessageHandler(Filters.text, customer_delete_name)],
        #         CUSTOMER_DELETE_CONFIRMATION: [MessageHandler(Filters.regex('^(yes|no)$'), delete_customer_confirmation)],
        #     },
        #     fallbacks=[CommandHandler('cancel', cancel)]
        # )

        # dispatcher.add_handler(conv_handler_delete_customer)

        dispatcher.add_handler(CallbackQueryHandler(customer_delete_name, pattern='^'+CUSTOMER_DELETE_NAME+'$'))
        dispatcher.add_handler(CallbackQueryHandler(delete_customer_confirmation, pattern='^(confirm_delete|cancel_delete)$'))

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
        entry_points=[CommandHandler('add_warehousing', start_add_warehousing)],
            states={
                WAREHOUSING_ARRIVAL_DATE: [CallbackQueryHandler(arrival_date)],
                CHOOSE_SUPPLIER_METHOD: [CallbackQueryHandler(choose_supplier_method)],
                MANUAL_INPUT_SUPPLIER: [MessageHandler(Filters.text & ~Filters.command, manual_input_supplier)],
                SUPPLIER_PRODUCT: [CallbackQueryHandler(supplier_product), MessageHandler(Filters.text & ~Filters.command, manual_input_product)],
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
                DELETE_SUPPLIER: [CallbackQueryHandler(delete_warehousing_supplier)],
                DELETE_PRODUCT: [CallbackQueryHandler(delete_warehousing_product)],
                DELETE_SUPPLIER_CONFIRMATION: [CallbackQueryHandler(delete_warehousing_confirmation)]
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
            entry_points=[CommandHandler('find_by_date', start_find_by_date)],
            states={
                FIND_BY_DATE: [CallbackQueryHandler(find_by_date)],
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
    except Exception or TypeError or AttributeError as e:
        error_message = f"发生错误：{e}"
        updater.message.reply_text(error_message)
        updater.message.reply_text('尽管发生了错误，但我们可以继续进行其他操作。请输入下一步命令。')
        

if __name__ == '__main__':
    main()
