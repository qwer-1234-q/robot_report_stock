import logging
import telegram
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, CallbackQueryHandler

from datetime import datetime
"""
###################################################################################
                            Start 开始
###################################################################################
"""
def start(update: Update, context: CallbackContext) -> None:
    """发送一个消息，当命令 /start 被调用时。"""
    update.message.reply_text('欢迎使用我们的Telegram机器人！')
    main_menu(update, context)

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
    reply_message(update, context,'操作已取消。', None)
    context.user_data.clear()
    return ConversationHandler.END

def build_menu(buttons, n_cols):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    return menu

def handle_input(data):
    if data in ["None", "none", "None", "", " "] or data is None:
        return None 
    return data

def reply_message(update, context, message, reply_markup=None):
    query = update.callback_query
    bot = context.bot
    if query:
        query.answer()
        query.edit_message_text(text=message, reply_markup=reply_markup)
        # bot.send_message(chat_id=query.message.chat.id, text=message, reply_markup=reply_markup)
    else:
        update.message.reply_text(message, reply_markup=reply_markup)
        # bot.send_message(update.effective_chat.id, text=message, reply_markup=reply_markup)

def reply_long_message(update, context, response):
    query = update.callback_query
    if query:
        send_long_text(query.message.chat.id, response, context.bot)
    else:
        send_long_text(update.effective_chat.id, response, context.bot)

def help(update: Update, context: CallbackContext) -> int:
    command_list = [
        "主页",
        "/main_menu - 主菜单/主目录",
        "/help - 列出所有功能并帮助你找你想要的操作。",
        "/sale_menu - 销售记录",
        "/customer_menu - 客户记录",
        "/inventory_menu - 库存表",
        "/warehousing_menu - 入库记录",
        "\n-----------------------------------------",
        "销售记录表",
        "-----------------------------------------\n",
        "/record_out - 添加新的销售记录。",
        "/sale_get_all - 获取所有销售记录。",
        "/sale_delete_by_id - 删除指定销售ID的记录。",
        "/sale_get_by_id - 根据销售ID查找销售记录。",
        "/sale_by_customer - 根据销售客户名字查找销售记录。",
        "/add_staff - 添加新的销售员名字",
        "\n-----------------------------------------",
        "客户记录表",
        "-----------------------------------------\n",
        "/add_customer - 添加新客户及其付款信息，或更新已有的客户的客户付款信息。",
        "/delete_customer - 删除客户及其付款信息（注意：只删除客户表的信息，不删除其他表格）。",
        "/get_customers_with_debt - 查找有欠款的客户。",
        "/customer_excess_payment - 查找有超额的客户。",
        "/get_all_customers - 获取所有客户记录。",
        "\n-----------------------------------------",
        "库存表",
        "-----------------------------------------\n",
        "/get_product_data - 获取指定产品的详细信息。",
        "/add_product_name - 只添加产品名称，不添加其他内容 。",
        "/add_or_update_product - 添加或更新产品信息。会有预选产品供选择，如果目录没有，可选择自行添加。",
        "/delete_product - 删除指定的产品记录。",
        "/list_all_products - 列出所有产品信息。",
        "\n-----------------------------------------",
        "入库记录表",
        "-----------------------------------------\n",
        "/record_in - 添加仓库入库记录。",
        "/add_supplier - 添加供应商的名称。",
        "/delete_record_in - 删除仓库入库记录。",
        # "/update_warehousing - 更新仓库入库记录信息。（未完成）",
        "/get_all_warehousing - 获取所有仓库入库记录。",
        "/get_record_in_by_date - 根据到货日期查找入库记录。",
        "\n-----------------------------------------",
        "-----------------------------------------",
        "请使用这些命令与机器人进行交互。"
    ]
    # 将命令列表连接成单个字符串消息
    help_message = "\n".join(command_list)
    send_long_text(update.effective_chat.id, help_message, context.bot)
    return ConversationHandler.END

"""
###################################################################################
                              Build Menu
###################################################################################
"""
MAIN_MENU, CHOOSE_ACTION, SALE_MENU, HANDLE_SALE, HANDLE_INVENTORY = range(5)
INVENTORY_MENU, CUSTOMER_MENU, HANDLE_INVENTORY, WAREHOUSING_MENU = range(4)
HANDLE_WAREHOUSING, HANDLE_CUSTOMER = range(2)

def main_menu(update: Update, context: CallbackContext) -> None:
    """主页菜单"""
    keyboard = [
        [InlineKeyboardButton("销售记录", callback_data='sale_menu')],
        [InlineKeyboardButton("客户记录", callback_data='customer_menu')],
        [InlineKeyboardButton("库存表", callback_data='inventory_menu')],
        [InlineKeyboardButton("入库记录", callback_data='warehousing_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = '请选择菜单:'
    reply_message(update, context, message, reply_markup)
    # update.message.reply_text('请选择菜单:', reply_markup=reply_markup)
    # return CHOOSE_ACTION

def menu_handler(update: Update, context: CallbackContext) -> None:
    """处理菜单的回调查询"""
    query = update.callback_query
    query.answer()
    logging.info(f"{query.data} in the menu_handler")
    if query.data == 'sale_menu':
        logging.info(f"1 GO TO THE {query.data} in the menu_handler")
        sale_menu(update, context)
        # return HANDLE_SALE
        return SALE_MENU
    elif query.data == 'customer_menu':
        logging.info(f"2 GO TO THE {query.data} in the menu_handler")
        # return customer_menu(update, context)
        return CUSTOMER_MENU
    elif query.data == 'inventory_menu':
        logging.info(f"3 GO TO THE {query.data} in the menu_handler")
        # inventory_menu(update, context)
        # return HANDLE_INVENTORY
        return INVENTORY_MENU
    elif query.data == 'warehousing_menu':
        logging.info(f"4 GO TO THE {query.data} in the menu_handler")
        # return warehousing_menu(update, context)
        return WAREHOUSING_MENU
    elif query.data == 'main_manu':
        logging.info(f"5 GO TO THE {query.data} in the menu_handler")
        # main_menu(update, context)
        return MAIN_MENU 
    
def sale_menu(update: Update, context: CallbackContext) -> None:
    """销售记录菜单"""
    logging.info("sale_menu")
    keyboard = [
        [InlineKeyboardButton("添加销售记录", callback_data='record_out')],
        [InlineKeyboardButton("查看所有销售记录", callback_data='sale_get_all')],
        [InlineKeyboardButton("删除指定销售ID的记录", callback_data='sale_delete_by_id')],
        [InlineKeyboardButton("根据销售ID查找销售记录", callback_data='sale_get_by_id')],
        [InlineKeyboardButton("根据销售客户名字查找销售记录", callback_data='sale_by_customer')],
        [InlineKeyboardButton("添加新的销售员名字", callback_data='add_staff')],
        [InlineKeyboardButton("返回主菜单", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query = update.callback_query
    if query:
        query.answer()
        query.edit_message_text(text="销售记录操作:", reply_markup=reply_markup)
    else: 
        update.message.reply_text("销售记录操作:", reply_markup=reply_markup)
    # return handle_sale_menu_choice(update, context)
    logging.info("Go to the handle_sale_menu_choice ")
    # return HANDLE_SALE
    
from user_record_out import start_record_out 
from user_all_records import sale_get_all, start_find_sale_by_customer_name, start_find_sale
from user_delete import start_delete_sale
from user_add_staff import add_staff_start

RECORD_OUT_START = range(1)

def handle_sale_menu_choice(update: Update, context: CallbackContext):
    query = update.callback_query
    if query:
        query.answer() 
        data = query.data
    else:
        data = update.message.text
    logging.info(f"handle_sale_menu choics {data}")
    if data == 'record_out':
        query.edit_message_text('/record_out 请点击')
        # start_record_out(update, context)
        # message = '/record_out'
        # context.bot.send_message(chat_id=query.message.chat_id, text=message)
        return start_record_out(update, context)
        # return RECORD_OUT_START
    elif data == 'sale_get_all':
        query.edit_message_text('/sale_get_all 请点击')
        # sale_get_all(update, context)
        return sale_get_all(update, context)
    elif data == 'sale_delete_by_id':
        query.edit_message_caption('/sale_delete_by_id 请点击')
        # start_delete_sale(update, context)
        return start_delete_sale(update, context)
    elif data == 'add_staff':
        # add_staff_start(update, context)
        query.edit_message_caption('/add_staff 请点击')
        return add_staff_start(update, context)
    elif data == 'sale_by_customer':
        # start_find_sale_by_customer_name(update, context)
        return start_find_sale_by_customer_name(update, context)
    elif data == 'sale_get_by_id':
        # start_find_sale(update, context)
        query.edit_message_caption('/sale_get_by_id 请点击')
        return start_find_sale(update, context)
    elif data == 'main_menu':
        query.edit_message_caption('/main_menu 请点击')
        # main_menu(update, context)
        return main_menu(update, context)
    
def customer_menu(update: Update, context: CallbackContext) -> None:
    """客户记录菜单"""
    keyboard = [
        [InlineKeyboardButton("添加/更新客户信息", callback_data='add_customer')],
        [InlineKeyboardButton("删除客户信息", callback_data='delete_customer')],
        [InlineKeyboardButton("查找有欠款的客户", callback_data='get_customers_with_debt')],
        [InlineKeyboardButton("查找有超额付款的客户", callback_data='customer_excess_payment')],
        [InlineKeyboardButton("获取所有客户记录", callback_data='get_all_customers')],
        [InlineKeyboardButton("返回主菜单", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query = update.callback_query
    if query:
        query.edit_message_text(text="请选择客户记录操作:", reply_markup=reply_markup)
    else:
        update.message.reply_text('请选择客户记录操作:', reply_markup=reply_markup)
    # handle_customer_menu_choice(update, context)
    # return HANDLE_CUSTOMER 

def handle_customer_menu_choice(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer() 
    
    # 根据用户的选择进行分支处理
    if query.data == 'add_customer':
        query.edit_message_text(text="请输入客户信息。")        
    elif query.data == 'delete_customer':
        query.edit_message_text(text="请输入要删除的客户ID。")
    elif query.data == 'get_customers_with_debt':
        query.edit_message_text(text="有欠款的客户列表。")
    elif query.data == 'customer_excess_payment':
        query.edit_message_text(text="有超额付款的客户列表。")
    elif query.data == 'get_all_customers':
        query.edit_message_text(text="所有客户记录。")
    elif query.data == 'main_menu':
        # return main_menu(update, context)
        return MAIN_MENU

def inventory_menu(update: Update, context: CallbackContext) -> None:
    """库存表菜单"""
    keyboard = [
        [InlineKeyboardButton("获取产品信息", callback_data='get_product_data')],
        [InlineKeyboardButton("添加产品名称", callback_data='add_product_name')],
        [InlineKeyboardButton("添加或更新产品", callback_data='add_or_update_product')],
        [InlineKeyboardButton("删除产品记录", callback_data='delete_product')],
        [InlineKeyboardButton("列出所有产品", callback_data='list_all_products')],
        [InlineKeyboardButton("返回主菜单", callback_data='main_menu')]
    ]
    # query = update.callback_query
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = "库存操作:"
    reply_message(update, context, message, reply_markup)
    # query.edit_message_text(text="库存操作:", reply_markup=reply_markup)
    # return HANDLE_INVETORY

def handle_inventory_menu_choice(update, context):
    """处理库存菜单的选择"""
    query = update.callback_query
    query.answer()
    data = query.data

    if data == 'get_product_data':
        # 执行获取产品信息的操作
        query.edit_message_text(text="请输入产品名称以获取详细信息。")
    elif data == 'add_product_name':
        # 执行添加产品名称的操作
        query.edit_message_text(text="请输入要添加的产品名称。")
    elif data == 'add_or_update_product':
        # 执行添加或更新产品的操作
        query.edit_message_text(text="请输入产品详细信息以添加或更新。")
    elif data == 'delete_product':
        # 执行删除产品记录的操作
        query.edit_message_text(text="请输入要删除的产品名称。")
    elif data == 'list_all_products':
        # 执行列出所有产品的操作
        query.edit_message_text(text="所有产品信息如下：")
    elif data == 'main_menu':
        # main_menu(update, query)
        return MAIN_MENU
    else:
        query.edit_message_text(text="无法识别的操作。")

def warehousing_menu(update: Update, context: CallbackContext) -> None:
    """入库记录菜单"""
    keyboard = [
        [InlineKeyboardButton("添加仓库入库记录", callback_data='record_in')],
        [InlineKeyboardButton("添加供应商的名称", callback_data='add_supplier')],
        [InlineKeyboardButton("删除仓库入库记录", callback_data='delete_record_in')],
        [InlineKeyboardButton("获取所有仓库入库记录", callback_data='get_all_warehousing')],
        [InlineKeyboardButton("根据到货日期查找入库记录", callback_data='get_record_in_by_date')],
        [InlineKeyboardButton("返回主菜单", callback_data='main_menu')]
    ]
    query = update.callback_query
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = "入库记录操作:"
    reply_message(update, context, message, reply_markup)
    # query.edit_message_text(text="入库记录操作:", reply_markup=reply_markup)
    # return HANDLE_WAREHOUSING

def handle_warehousing_menu_choice(update, context):
    """处理入库记录菜单的选择"""
    query = update.callback_query
    query.answer()
    data = query.data

    # 根据 data 的值调用相应的功能
    if data == 'record_in':
        # 执行添加仓库入库记录的操作
        query.edit_message_text(text="请按照格式输入入库记录信息。")
    elif data == 'add_supplier':
        # 执行添加供应商的操作
        query.edit_message_text(text="请输入供应商名称。")
    elif data == 'delete_record_in':
        # 执行删除仓库入库记录的操作
        query.edit_message_text(text="请输入要删除的入库记录ID。")
    elif data == 'get_all_warehousing':
        # 执行获取所有仓库入库记录的操作
        query.edit_message_text(text="所有仓库入库记录如下：")
    elif data == 'get_warehousing_by_date':
        # 执行根据到货日期查找入库记录的操作
        query.edit_message_text(text="请输入要查询的到货日期。")
    elif data == 'main_menu':
        # main_menu(update, query)
        return MAIN_MENU
    else:
        query.edit_message_text(text="无法识别的操作。")