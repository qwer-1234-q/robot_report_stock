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

### the message handle features from other files
from user_handle_message import cancel, build_date_keyboard, build_menu


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 实例化管理对象
sales_manager = Sales()
warehousing_manager = Warehousing_read()
inventory_manager = Inventories()
customers_manager = Customers()

(WAREHOUSING_ARRIVAL_DATE, WAREHOUSING_SUPPLIER, WAREHOUSING_UNIT_PRICE) = range(3)
(CHOOSE_SUPPLIER_METHOD, MANUAL_INPUT_SUPPLIER, SUPPLIER_PRODUCT) = range(3)
(CHOOSE_PRODUCT_METHOD, MANUAL_INPUT_PRODUCT, WAREHOUSING_STOCK_IN) = range(3)
(MANUAL_INPUT_ARRIVAL_DATE, WAREHOUSING_TOTAL_PRICE, SUPPLIER_CONFIRMATION) = range(3)

def start_add_warehousing(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("请选择到货日期:", reply_markup=build_date_keyboard())
    logging.info("start_add_warehousing")
    return WAREHOUSING_ARRIVAL_DATE

def arrival_date(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    logging.info(f"warehousing arrival date input, {query.data}")

    if query.data == 'enter_custom_date':
        query.message.reply_text("请输入自定义到货日期（格式DD/MM/YYYY）:")
        return MANUAL_INPUT_ARRIVAL_DATE
    context.user_data['arrival_date'] = datetime.now().strftime('%d/%m/%Y')
    query.message.reply_text(f"今天日期是{datetime.now().strftime('%d/%m/%Y')}")
    logging.info(f"current arrival date: {datetime.now().strftime('%d/%m/%Y')}")
    message = f"到货日期: {datetime.now().strftime('%d/%m/%Y')}\n请选择供应商:"
    update.message.reply_text(text=message, reply_markup=get_supplier_buttons())
    return CHOOSE_SUPPLIER_METHOD

def manual_input_arrival_date(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    try:
        # Attempt to convert the text input into a datetime object
        custom_date = datetime.strptime(text, '%d/%m/%Y')
        # If successful, store the date in context.user_data
        context.user_data['arrival_date'] = custom_date
        message = f"到货日期: {datetime.now().strftime('%d/%m/%Y')}\n请选择供应商:"
        update.message.reply_text(text=message, reply_markup=get_supplier_buttons())
        return CHOOSE_SUPPLIER_METHOD
    except ValueError:
        # If the date format is incorrect, prompt the user to try again
        update.message.reply_text("日期格式不正确，请使用DD/MM/YYYY格式重新输入：")
        return MANUAL_INPUT_ARRIVAL_DATE    

def get_supplier_buttons():
    suppliers = warehousing_manager.get_supplier_list() 
    buttons = [InlineKeyboardButton(supplier, callback_data=supplier) for supplier in suppliers]
    buttons.append(InlineKeyboardButton("手动输入", callback_data="manual_input_supplier"))
    keyboard = InlineKeyboardMarkup(build_menu(buttons, n_cols=2)) 
    return keyboard

def choose_supplier_method(update: Update, context: CallbackContext) -> int:
    logging.info("choose supplier method")
    if update.callback_query:
        query = update.callback_query
        query.answer()
        
        if query.data == 'manual_input_supplier':
            query.edit_message_text(text="请输入供应商名称:")
            return MANUAL_INPUT_SUPPLIER
        else: 
            context.user_data['supplier'] = query.data 
            reply_markup = get_product_buttons() 
            query.edit_message_text(text=f"供应商名称: {query.data}\n请选择产品输入方式:", reply_markup=reply_markup)
            return SUPPLIER_PRODUCT
    else:
        text = update.message.text
        context.user_data['supplier'] = text
        logging.info("manual input supplier")
        reply_markup = get_product_buttons()
        update.message.reply_text(text=f"供应商名称: {query.data}\n请选择产品输入方式:", reply_markup=reply_markup)
        return SUPPLIER_PRODUCT 

def manual_input_supplier(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    context.user_data['supplier'] = text
    logging.info("mannual input supplier")
    update.message.reply_text(text=f"供应商名称: {text}\n请选择产品输入方式:", reply_markup=get_product_buttons())
    return SUPPLIER_PRODUCT

def get_product_buttons():
    products = inventory_manager.get_product_list()
    buttons = [InlineKeyboardButton(product, callback_data=product) for product in products]
    buttons.append(InlineKeyboardButton("手动输入", callback_data="manual_input_product"))
    return InlineKeyboardMarkup(build_menu(buttons, n_cols=2)) 

def choose_product_method(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    logging.info("choose product method")
    if query.data == 'manual_input_product':
        query.edit_message_text(text="请输入产品名称:")
        return MANUAL_INPUT_PRODUCT
    else: 
        context.user_data['supplier_product'] = query.data
        query.edit_message_text(text=f"产品名称: {query.data} \n请输入入库数量:")
        return WAREHOUSING_STOCK_IN

def manual_input_product(update: Update, context: CallbackContext) -> int:
    logging.info("mannual input product")
    text = update.message.text
    context.user_data['supplier_product'] = text
    update.message.reply_text(text=f"产品名称: {text} \n请输入入库数量:")
    return WAREHOUSING_STOCK_IN

def warehousing_stock_in(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    logging.info("warehousing stock in ")
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
    logging.info("warehousing unit price")
    try:
        price = float(text)
        if price > 0:
            context.user_data['warehousing_unit_price'] = price
                    
            # 例如，结束对话并给出确认信息
            return confirm_warehousing_information(update, context) 
        else:
            raise ValueError
    except ValueError:
        update.message.reply_text("请输入有效的正数作为单价:")
        return WAREHOUSING_UNIT_PRICE

def confirm_warehousing_information(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    # query.answer()
    logging.info("confirm warehousing information")
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

def confirm_warehousing(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    logging.info("confirm warehuosing and add warehousing")
    if query.data == 'confirm':
        # 用户确认了信息，进行数据添加操作
        result_message = inventory_manager.add_warehousing_record(
            arrival_date=context.user_data['arrival_date'],
            supplier=context.user_data['supplier'],
            product=context.user_data.get('supplier_product', None),  # 如果用户手动输入产品名称，从context.user_data中获取
            stock_in=context.user_data['warehousing_stock_in'],
            unit_price=context.user_data['warehousing_unit_price'],
        )
        query.edit_message_text(text=result_message)
    else:
        # 用户取消操作
        query.edit_message_text(text="操作已取消。")
    
    return ConversationHandler.END

