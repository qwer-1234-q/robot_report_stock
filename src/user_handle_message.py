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
    keyboard = [
        # Button for selecting today's date directly
        [InlineKeyboardButton(text="选择今日日期", callback_data='choose_today')],
        # Button for prompting the user to enter a custom date
        [InlineKeyboardButton(text="输入自定义日期", callback_data='enter_custom_date')]
    ]
    return InlineKeyboardMarkup(keyboard)

def build_menu(buttons, n_cols):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    return menu

def help(update: Update, context: CallbackContext) -> int:
    command_list = [
        "主页",
        "/start - 开始与机器人的对话。（未加菜单）",
        "\n销售记录表\n",
        "/record_out - 添加新的销售记录。（未完成）",
        "/sale_get_all - 获取所有销售记录。",
        "/sale_delete_by_id - 删除指定销售ID的记录。",
        "/sale_get_by_id - 根据销售ID查找销售记录。",
        "/sale_by_customer - 根据销售客户名字查找销售记录。",
        "\n客户记录表\n",
        "/customer_add - 添加新客户及其付款信息。（未完成）",
        "/delete_customer - 删除新客户及其付款信息（注意：只删除客户表的信息，不删除其他表格）。",
        "/get_customers_with_debt - 查找有欠款的客户。",
        "/customer_excess_payment - 查找有超额的客户。",
        "/update_payment - 更新客户付款信息。（未完成）",
        "/get_all_customers - 获取所有客户记录。",
        " ",
        "库存表\n",
        "/get_product_data - 获取指定产品的详细信息。",
        "/add_product_name - 只添加产品名称 。（未完成）",
        "/add_or_update_product - 添加或更新产品信息。（未完成）",
        "/delete_product - 删除指定的产品记录。",
        "/list_all_products - 列出所有产品信息。",
        "入库记录表\n",
        "/record_in - 添加仓库入库记录。（未完成）",
        "/delete_warehousing - 删除仓库入库记录。",
        "/update_warehousing - 更新仓库入库记录信息。（未完成）",
        "/get_all_warehousing - 获取所有仓库入库记录。",
        "/get_warehoursing_by_date - 根据到货日期查找入库记录。",
        "\n",
        "请使用这些命令与机器人进行交互。"
    ]
    # 将命令列表连接成单个字符串消息
    help_message = "\n".join(command_list)
    send_long_text(update.effective_chat.id, help_message, context.bot)
    return ConversationHandler.END