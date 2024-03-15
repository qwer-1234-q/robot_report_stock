import telegram
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, CallbackQueryHandler

# 导入之前定义的类
from read_sales import Sales
from read_warehousing import Warehousing_read
from read_inventory import Inventories
from read_customer import Customers

from datetime import datetime 
from user_handle_message import send_long_text, cancel, build_date_keyboard, build_menu

# Telegram Bot Token
TOKEN = '6487583852:AAGH3YlPRpfuOtLt-GlWvyI4Ss-B1lxOdtA'

# 实例化管理对象
sales_manager = Sales()
warehousing_manager = Warehousing_read()
inventory_manager = Inventories()
customers_manager = Customers()

SALE_CUSTOMER, MANUAL_INPUT_CUSTOMER, SALE_CONFIRM_DATE, SALE_ENTER_CUSTOM_DATE = range(4) 
SALE_PRODUCT, SALE_SHIPPING_DATE, SALE_STOCK_OUT, SALE_UNIT_PRICE, SALE_SELLER = range(5) 
SALE_PAYMENT, SALE_CONFIRMATION = range(2)

def sale_start(update: Update, context: CallbackContext) -> int:
    # 获取已知的客户列表
    customer_list = customers_manager.get_customer_name_list()
    # 创建客户名的按钮列表
    buttons = [InlineKeyboardButton(name, callback_data=name) for name in customer_list]
    # 添加一个特殊按钮用于手动输入
    buttons.append(InlineKeyboardButton("手动输入客户名", callback_data="manual_input_customer"))
    # 将按钮列表分为一行一行
    keyboard = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    # 创建 InlineKeyboardMarkup 对象
    reply_markup = InlineKeyboardMarkup(keyboard)

    # 检查是否是回调查询的上下文
    if update.callback_query:
        query = update.callback_query
        query.answer()
        query.edit_message_text(text='请选择客户名或手动输入：', reply_markup=reply_markup)
    else:
        # 发送消息并附带按钮
        update.message.reply_text('请选择客户名或手动输入：', reply_markup=reply_markup)

    return SALE_CUSTOMER


def manual_input_customer(update: Update, context: CallbackContext) -> int:
    customer_name = update.message.text
    context.user_data['sale_customer'] = customer_name
    # 接下来的逻辑，比如让用户选择产品
    update.message.reply_text(f"您输入的客户名是：{customer_name}，请继续...")
    update.message.reply_text("请选择你想要的产品：")
    return display_product_options(update, context)

def sale_customer(update: Update, context: CallbackContext) -> str:
    query = update.callback_query
    query.answer()
    selected_customer = query.data
    print(f"user have to select the customer or input the customer")
    if selected_customer == "manual_input_customer":
        context.bot.send_message(chat_id=update.effective_chat.id, text="请输入客户名：")
        return MANUAL_INPUT_CUSTOMER
    else:
        context.user_data['sale_customer'] = selected_customer
        display_product_options(update, context)
     
def display_product_options(update: Update, context: CallbackContext) -> int:
    products = inventory_manager.get_product_list() 
    buttons = [InlineKeyboardButton(product, callback_data=product) for product in products]
    keyboard = InlineKeyboardMarkup(build_menu(buttons, n_cols=2)) 
    query = update.callback_query
    if update.callback_query:
        query = update.callback_query
        try:
            query.edit_message_text(text="请选择产品名称：", reply_markup=keyboard)
        except telegram.error.BadRequest as e:
            if "Message is not modified" in str(e):
                print(f"ERR0R - display_product_options: {e}")
    else:
        # 直接从其他状态跳转而来，发送新消息
        update.message.reply_text(text="请选择产品名称：", reply_markup=keyboard)

    return SALE_CONFIRM_DATE

def sale_product(update: Update, context: CallbackContext) -> str:
    query = update.callback_query
    query.answer()
    selected_product = query.data
    context.user_data['sale_product'] = selected_product
    # 默认设置为今日日期
    today = datetime.now().strftime('%d/%m/%Y')
    context.user_data['sale_shipping_date'] = today
    # 提供选项让用户确认或更改日期
    keyboard = [
        [InlineKeyboardButton("确认今日日期", callback_data='confirm_today')],
        [InlineKeyboardButton("输入新日期", callback_data='enter_custom')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=f"已选择产品：{selected_product}\n当前出货日期默认为今日：{today}。确认或更改？", reply_markup=reply_markup)
    return SALE_CONFIRM_DATE

def sale_confirm_or_change_date(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    if query.data == 'confirm_today':
        # 用户确认日期，继续流程
        selected_date = context.user_data['sale_shipping_date']
        query.edit_message_text(text=f"已确认出货日期：{selected_date}\n请输入出库数量：")
        return SALE_STOCK_OUT
    elif query.data == 'enter_custom':
        query.edit_message_text(text="请输入新的日期（格式YYYY-MM-DD）：")
        return SALE_ENTER_CUSTOM_DATE

def sale_enter_custom_date(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    context.user_data['sale_shipping_date'] = text
    update.message.reply_text(f"已设置出货日期为：{text}。请输入出库数量：")
    return SALE_STOCK_OUT

# def sale_shipping_date(update: Update, context: CallbackContext) -> str:
#     update.message.reply_text('请选择出货日期：', reply_markup=build_date_keyboard())
#     return SALE_STOCK_OUT  # 保持状态，直到用户选择日期

# def date_selected(update: Update, context: CallbackContext) -> int:
#     query = update.callback_query
#     query.answer()
#     selected_date = query.data.replace('date_', '')
#     context.user_data['sale_shipping_date'] = selected_date
#     query.edit_message_text(text=f"已选择日期：{selected_date}\n请输入出库数量：")
#     return SALE_STOCK_OUT

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
    sale_customer = user_data.get('sale_customer', '未提供')  # 使用get方法，如果键不存在，返回'未提供'
    sale_product = user_data.get('sale_product', '未提供')
    sale_shipping_date = user_data.get('sale_shipping_date', '未提供')
    sale_stock_out = user_data.get('sale_stock_out', '未提供')
    sale_unit_price = user_data.get('sale_unit_price', '未提供')
    sale_seller = user_data.get('sale_seller', '未提供')
    sale_payment = user_data.get('sale_payment', '未提供')

    message += f"客户名：{sale_customer}\n产品名称：{sale_product}\n"
    message += f"出货日期：{sale_shipping_date}\n出库数量：{sale_stock_out}\n"
    message += f"单价：{sale_unit_price}\n销售员：{sale_seller}\n款项：{sale_payment}\n"
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
        try:
            sales_msg = submit_sale_record(context.user_data)
            query.edit_message_text(text=sales_msg)
        except KeyError as e:
            query.edit_message_text(text="销售信息不完整，请重新开始。")
        return ConversationHandler.END
    elif query.data == 'reenter':
        # 用户选择重新输入，指引用户从头开始
        context.bot.send_message(chat_id=update.effective_chat.id, text="请重新开始输入销售信息。")
        return sale_start(update, context) 
    