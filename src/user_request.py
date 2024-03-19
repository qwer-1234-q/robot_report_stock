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
                             Menu 菜单
###################################################################################
"""
from user_handle_message import (MAIN_MENU, CHOOSE_ACTION, SALE_MENU, HANDLE_SALE, HANDLE_INVENTORY,
                                INVENTORY_MENU, CUSTOMER_MENU, HANDLE_INVENTORY, WAREHOUSING_MENU,
                                HANDLE_WAREHOUSING, HANDLE_CUSTOMER)
from user_handle_message import handle_sale_menu_choice
from user_handle_message import SALE_MENU, sale_menu, handle_sale_menu_choice
from user_handle_message import customer_menu, handle_customer_menu_choice
from user_handle_message import inventory_menu, handle_inventory_menu_choice
from user_handle_message import warehousing_menu, handle_warehousing_menu_choice


### the message handle features from other files
from user_handle_message import start, main_menu, menu_handler, send_long_text, cancel, build_menu, help, handle_input


"""
###################################################################################
                            Sales records 销售记录表
###################################################################################
"""
# record out functions 
from user_record_out import (start_record_out, record_out_customer, record_out_product, record_out_shipping_date,
                             record_out_stock_out, record_out_unit_price, record_out_staff, manual_input_staff,
                             record_out_payment, manual_input_customer, manual_sold_product, manual_sold_shipping_date)
from user_record_out import (RECORD_OUT_CUSTOMER, RECORD_OUT_PRODUCT, RECORD_OUT_SHIPPING_DATE, RECORD_OUT_STOCK_OUT, 
                             RECORD_OUT_UNIT_PRICE, RECORD_OUT_STAFF, RECORD_OUT_PAYMENT, RECORD_OUT_CONFIRMATION, 
                             MANUAL_INPUT_CUSTOMER, MANUAL_SOLD_PRODUCT, MANUAL_SOLD_SHIPPING_DATE, MANUAL_SOLD_STAFF)

# RECORD_OUT_START = range(1)
from user_handle_message import RECORD_OUT_START

# all sales records
from user_all_records import (sale_get_all, find_sale_by_id, start_find_sale, 
                            start_find_sale_by_customer_name, handle_customer_selection, handle_manual_find_customer_input)
from user_all_records import (SALE_FIND, SALE_FIND_CUSTOMER, HANDLE_MANUAL_FIND_CUSTOMER_INPUT)

# Delete a record
from user_delete import (start_delete_sale, delete_sale)
from user_delete import (SALE_DELETE)

# add a staff
from user_add_staff import ADD_STAFF, add_staff_command, add_staff_start

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

# add or update customer information, e.g. payment, payable, and debt
from user_customer_add_update import (customer_add, handle_manual_new_customer_input, customer_name, customer_payable, customer_payment, customer_confirmation)
from user_customer_add_update import (CUSTOMER_NAME, HANDLE_MANUAL_NEW_CUSTOMER_INPUT, CUSTOMER_PAYABLE, CUSTOMER_PAYMENT, CUSTOMER_COMFIRMATION)

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

# add product name only
from user_add_product import add_product_name, enter_product_name, ENTER_PRODUCT_NAME

# add product information 
from user_add_product import (PRODUCT_NAME, STOCK_IN, STOCK_OUT, MANUAL_PRODUCT_NAME,
                              SCHEDULE_INVENTORY,  PRODUCT_CONFIRMATION)
from user_add_product import (start_add_or_update_product, product_name, manual_input_product,
                              stock_in, stock_out, schedule_inventory, perform_add_or_update)

"""
###################################################################################
                                Warehousing 入货记录
###################################################################################
"""
# record in functions
from user_record_in import (RECORD_IN_ARRIVAL_DATE, RECORD_IN_SUPPLIER, 
                            RECORD_IN_PRODUCT, RECORD_IN_STOCK_IN, RECORD_IN_UNIT_PRICE, 
                            MANUAL_RECORD_IN_ARRIVAL_DATE, ADD_SUPPLIER)
from user_record_in import (start_add_warehousing, record_in_arrival_date, 
                            record_in_supplier, record_in_product, record_in_stock_in, 
                            record_in_unit_price, manual_record_in_shipping_date,
                            add_supplier, start_add_supplier)

# get the warehousing data 
from user_all_records import FIND_BY_DATE, MANUAL_FIND_WAREHOUSING_DATE 
from user_all_records import start_find_by_date, find_by_date, manual_find_warehousing_date, get_all_warehousing

# delete a warehousing data
from user_delete import (DELETE_ARRIVAL_DATE, DELETE_SUPPLIER, DELETE_PRODUCT, MANUAL_DELETE_WAREHOUSING_DATE, DELETE_SUPPLIER_CONFIRMATION)
from user_delete import (start_delete_warehousing, delete_warehousing_arrival_date, manual_delete_warehousing_date,
                         delete_warehousing_supplier, delete_warehousing_product, delete_warehousing_confirmation)

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
    
    # help
    dispatcher.add_handler(CommandHandler("help", help))

    ########################################### MENU #############################################################
    
    ### Main Menu 
    dispatcher.add_handler(CommandHandler("main_menu", main_menu))
    dispatcher.add_handler(CallbackQueryHandler(main_menu, pattern='^main_menu$'))

    #### Sale Menu
    dispatcher.add_handler(CommandHandler("sale_menu", sale_menu))
    dispatcher.add_handler(CallbackQueryHandler(sale_menu, pattern='^sale_menu$'))

    #### Customer Menu
    dispatcher.add_handler(CommandHandler("customer_menu", customer_menu))
    dispatcher.add_handler(CallbackQueryHandler(customer_menu, pattern='^customer_menu$'))

    #### Inventory Menu 
    dispatcher.add_handler(CommandHandler("inventory_menu", inventory_menu))
    dispatcher.add_handler(CallbackQueryHandler(inventory_menu, pattern='^inventory_menu$'))

    #### Warehousing Menu 
    dispatcher.add_handler(CommandHandler("warehousing_menu", warehousing_menu))
    dispatcher.add_handler(CallbackQueryHandler(warehousing_menu, pattern='^warehousing_menu$'))

    ########################################### SALES ############################################################
    ## sale get all
    dispatcher.add_handler(CommandHandler("sale_get_all", sale_get_all))
    dispatcher.add_handler(CallbackQueryHandler(sale_get_all, pattern='^sale_get_all$'))

    ## record out
    conv_handler_record_out = ConversationHandler(
        entry_points=[CommandHandler('record_out', start_record_out)],
        states={
            # RECORD_OUT_CUSTOMER: [MessageHandler(Filters.text & ~Filters.command, record_out_customer)],
            RECORD_OUT_CUSTOMER: [CallbackQueryHandler(record_out_customer)],
            # MANUAL_INPUT_CUSTOMER: [MessageHandler(Filters.text & ~Filters.command, manual_input_customer)],
            # RECORD_OUT_PRODUCT: [MessageHandler(Filters.text & ~Filters.command, record_out_product)],
            RECORD_OUT_PRODUCT: [CallbackQueryHandler(record_out_product)],
            # MANUAL_SOLD_PRODUCT: [MessageHandler(Filters.text & ~Filters.command, manual_sold_product)],
            # MANUAL_SOLD_SHIPPING_DATE:[MessageHandler(Filters.text & ~Filters.command, manual_sold_shipping_date)],
            RECORD_OUT_SHIPPING_DATE: [CallbackQueryHandler(record_out_shipping_date)],
            MANUAL_SOLD_SHIPPING_DATE:[MessageHandler(Filters.text & ~Filters.command, manual_sold_shipping_date)],
            # RECORD_OUT_SHIPPING_DATE: [MessageHandler(Filters.text & ~Filters.command, record_out_shipping_date)],
            RECORD_OUT_STOCK_OUT: [MessageHandler(Filters.text & ~Filters.command, record_out_stock_out)],
            RECORD_OUT_UNIT_PRICE: [MessageHandler(Filters.text & ~Filters.command, record_out_unit_price)],
            # RECORD_OUT_STAFF: [MessageHandler(Filters.text & ~Filters.command, record_out_staff)],
            RECORD_OUT_STAFF: [CallbackQueryHandler( record_out_staff)],
            # MANUAL_SOLD_STAFF: [MessageHandler(Filters.text  & ~Filters.command, manual_input_staff)],
            RECORD_OUT_PAYMENT: [MessageHandler(Filters.text & ~Filters.command, record_out_payment)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    dispatcher.add_handler(conv_handler_record_out)
    
    conv_handler_record_out_2_call = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_record_out, pattern='^record_out$')],
        states={
            # RECORD_OUT_CUSTOMER: [MessageHandler(Filters.text & ~Filters.command, record_out_customer)],
            RECORD_OUT_CUSTOMER: [CallbackQueryHandler(record_out_customer)],
            # MANUAL_INPUT_CUSTOMER: [MessageHandler(Filters.text & ~Filters.command, manual_input_customer)],
            # RECORD_OUT_PRODUCT: [MessageHandler(Filters.text & ~Filters.command, record_out_product)],
            RECORD_OUT_PRODUCT: [CallbackQueryHandler(record_out_product)],
            # MANUAL_SOLD_PRODUCT: [MessageHandler(Filters.text & ~Filters.command, manual_sold_product)],
            # MANUAL_SOLD_SHIPPING_DATE:[MessageHandler(Filters.text & ~Filters.command, manual_sold_shipping_date)],
            RECORD_OUT_SHIPPING_DATE: [CallbackQueryHandler(record_out_shipping_date)],
            MANUAL_SOLD_SHIPPING_DATE:[MessageHandler(Filters.text & ~Filters.command, manual_sold_shipping_date)],
            # RECORD_OUT_SHIPPING_DATE: [MessageHandler(Filters.text & ~Filters.command, record_out_shipping_date)],
            RECORD_OUT_STOCK_OUT: [MessageHandler(Filters.text & ~Filters.command, record_out_stock_out)],
            RECORD_OUT_UNIT_PRICE: [MessageHandler(Filters.text & ~Filters.command, record_out_unit_price)],
            # RECORD_OUT_STAFF: [MessageHandler(Filters.text & ~Filters.command, record_out_staff)],
            RECORD_OUT_STAFF: [CallbackQueryHandler( record_out_staff)],
            # MANUAL_SOLD_STAFF: [MessageHandler(Filters.text  & ~Filters.command, manual_input_staff)],
            RECORD_OUT_PAYMENT: [MessageHandler(Filters.text & ~Filters.command, record_out_payment)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    dispatcher.add_handler(conv_handler_record_out_2_call)

    ## add staff
    conv_handler_add_staff = ConversationHandler(
        entry_points=[CommandHandler("add_staff", add_staff_start)],
        states={
            ADD_STAFF: [MessageHandler(Filters.text & ~Filters.command, add_staff_command)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler_add_staff)
    
    conv_handler_add_staff_call = ConversationHandler(
        entry_points=[CallbackQueryHandler(add_staff_start, pattern='^add_staff$')],
        states={
            ADD_STAFF: [MessageHandler(Filters.text & ~Filters.command, add_staff_command)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler_add_staff_call)

    # sale delete by id
    conv_handler_sale_delete = ConversationHandler(
        entry_points=[CommandHandler('sale_delete_by_id', start_delete_sale)],
        states={
            SALE_DELETE: [MessageHandler(Filters.text & ~Filters.command, delete_sale)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler_sale_delete)

    conv_handler_sale_delete_call = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_delete_sale, pattern='^sale_delete_by_id$')],
        states={
            SALE_DELETE: [MessageHandler(Filters.text & ~Filters.command, delete_sale)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler_sale_delete_call)

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
    
    conv_handler_sales_find_by_customer_call = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_find_sale_by_customer_name, pattern='^sale_by_customer$')],
        states={
            SALE_FIND_CUSTOMER: [CallbackQueryHandler(handle_customer_selection)],
            HANDLE_MANUAL_FIND_CUSTOMER_INPUT: [MessageHandler(Filters.text & ~Filters.command, handle_manual_find_customer_input)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler_sales_find_by_customer_call)

    ## sales result get by sale id 
    conv_handler_sales_get_by_id = ConversationHandler(
        entry_points=[CommandHandler('sale_get_by_id', start_find_sale)],
        states={
            SALE_FIND: [MessageHandler(Filters.text & ~Filters.command, find_sale_by_id)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler_sales_get_by_id)

    conv_handler_sales_get_by_id_call = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_find_sale, pattern='^sale_get_by_id$')],
        states={
            SALE_FIND: [MessageHandler(Filters.text & ~Filters.command, find_sale_by_id)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler_sales_get_by_id_call)

    
    ################################################# Customer ######################################################
    ### add customer name into the customer list
    conv_handler_customer_add = ConversationHandler(
        entry_points=[CommandHandler('add_customer', customer_add)],
        states={
            CUSTOMER_NAME: [CallbackQueryHandler(customer_name)],
            HANDLE_MANUAL_NEW_CUSTOMER_INPUT: [MessageHandler(Filters.text, handle_manual_new_customer_input)],
            CUSTOMER_PAYABLE: [MessageHandler(Filters.text, customer_payable)],
            CUSTOMER_PAYMENT: [MessageHandler(Filters.text, customer_payment)],         
            CUSTOMER_COMFIRMATION: [CallbackQueryHandler(customer_confirmation, pattern=('^(confirm|reenter)$'))]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler_customer_add)

    conv_handler_customer_add_call = ConversationHandler(
        entry_points=[CallbackQueryHandler(customer_add, pattern='^add_customer$')],
        states={
            CUSTOMER_NAME: [CallbackQueryHandler(customer_name)],
            HANDLE_MANUAL_NEW_CUSTOMER_INPUT: [MessageHandler(Filters.text, handle_manual_new_customer_input)],
            CUSTOMER_PAYABLE: [MessageHandler(Filters.text, customer_payable)],
            CUSTOMER_PAYMENT: [MessageHandler(Filters.text, customer_payment)],         
            CUSTOMER_COMFIRMATION: [CallbackQueryHandler(customer_confirmation, pattern=('^(confirm|reenter)$'))]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler_customer_add_call)

    ### Get the customer list which the customers with debt
    debt_handler = CommandHandler('get_customers_with_debt', get_customers_with_debt)
    dispatcher.add_handler(debt_handler)
    dispatcher.add_handler(CallbackQueryHandler(get_customers_with_debt, pattern='^get_customers_with_debt$'))

    ### Get the customer list which the customers with payment
    dispatcher.add_handler(CommandHandler('customer_excess_payment', get_customers_with_excess_payment_handler))
    dispatcher.add_handler(CallbackQueryHandler(get_customers_with_excess_payment_handler, pattern='^customer_excess_payment$'))

    conv_handler_delete_customer = ConversationHandler(
        entry_points=[CommandHandler('delete_customer', customer_delete_start)],
        states={
            CUSTOMER_DELETE_NAME: [CallbackQueryHandler( customer_delete_name)],
            CUSTOMER_DELETE_CONFIRMATION: [CallbackQueryHandler(delete_customer_confirmation, pattern=('^(confirm_delete|cancel_delete)$'))],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler_delete_customer)

    conv_handler_delete_customer_call = ConversationHandler(
        entry_points=[CallbackQueryHandler(customer_delete_start, pattern='^delete_customer$')],
        states={
            CUSTOMER_DELETE_NAME: [CallbackQueryHandler(customer_delete_name)],
            CUSTOMER_DELETE_CONFIRMATION: [CallbackQueryHandler(delete_customer_confirmation, pattern=('^(confirm_delete|cancel_delete)$'))],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler_delete_customer_call)

    ### Get customer list with their details
    dispatcher.add_handler(CommandHandler("get_all_customers", get_all_customers))
    dispatcher.add_handler(CallbackQueryHandler(get_all_customers, pattern="^get_all_customers$"))

    ########################################### Inventory ###########################################
    ## Get product data
    conv_handler_get_product_data = ConversationHandler(
        entry_points=[CommandHandler('get_product_data', start_get_product_data)],
        states={
            PRODUCT_QUERY: [CallbackQueryHandler(product_query)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler_get_product_data)

    conv_handler_get_product_data_call = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_get_product_data, pattern='^get_product_data$')],
        states={
            PRODUCT_QUERY: [CallbackQueryHandler(product_query)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler_get_product_data_call)

    # delete the inventory from inventory list
    conv_handler_inventory_delete = ConversationHandler(
        entry_points=[CommandHandler('delete_product', start_delete_product)],
        states={DELETE_PRODUCT: [CallbackQueryHandler(delete_product)],},
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler_inventory_delete)
    
    conv_handler_inventory_delete_call = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_delete_product, pattern='^delete_product$')],
        states={DELETE_PRODUCT: [CallbackQueryHandler(delete_product)],},
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler_inventory_delete_call)

    ## List all products in the inventory
    dispatcher.add_handler(CommandHandler('list_all_products', list_all_products))
    dispatcher.add_handler(CallbackQueryHandler(list_all_products, pattern='list_all_products'))

    # add or update the inventory from inventory list
    conv_handler_add_or_update_product = ConversationHandler(
        entry_points=[CommandHandler('add_or_update_product', start_add_or_update_product)],
            states={
                PRODUCT_NAME: [CallbackQueryHandler(product_name)],
                MANUAL_PRODUCT_NAME : [MessageHandler(Filters.text & ~Filters.command, manual_input_product)],
                STOCK_IN: [MessageHandler(Filters.text & ~Filters.command, stock_in)],
                STOCK_OUT: [MessageHandler(Filters.text & ~Filters.command, stock_out)],
                SCHEDULE_INVENTORY: [MessageHandler(Filters.text & ~Filters.command, schedule_inventory)],
                PRODUCT_CONFIRMATION: [CallbackQueryHandler(perform_add_or_update, pattern=('^(confirm|cancel)$'))]
            },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    dispatcher.add_handler(conv_handler_add_or_update_product)
    
    conv_handler_add_or_update_product_call = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_add_or_update_product, pattern='^add_or_update_product$')],
            states={
                PRODUCT_NAME: [CallbackQueryHandler(product_name)],
                MANUAL_PRODUCT_NAME : [MessageHandler(Filters.text & ~Filters.command, manual_input_product)],
                STOCK_IN: [MessageHandler(Filters.text & ~Filters.command, stock_in)],
                STOCK_OUT: [MessageHandler(Filters.text & ~Filters.command, stock_out)],
                SCHEDULE_INVENTORY: [MessageHandler(Filters.text & ~Filters.command, schedule_inventory)],
                PRODUCT_CONFIRMATION: [CallbackQueryHandler(perform_add_or_update, pattern=('^(confirm|cancel)$'))]
            },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    dispatcher.add_handler(conv_handler_add_or_update_product_call)

    ## add product name without add other information 
    conv_handler_add_product_name = ConversationHandler(
        entry_points=[CommandHandler('add_product_name', add_product_name)],
        states={
            ENTER_PRODUCT_NAME: [MessageHandler(Filters.text & ~Filters.command, enter_product_name)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler_add_product_name)
    
    conv_handler_add_product_name_call = ConversationHandler(
        entry_points=[CallbackQueryHandler(add_product_name, pattern='^add_product_name$')],
        states={
            ENTER_PRODUCT_NAME: [MessageHandler(Filters.text & ~Filters.command, enter_product_name)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler_add_product_name_call)

    ######################################### Warehousing #########################################
    ## record in that the company purchased inventories from a supplier
    conv_handler_record_in = ConversationHandler(
        entry_points=[CommandHandler('record_in', start_add_warehousing)],
        states={
            # RECORD_IN_ARRIVAL_DATE: [MessageHandler(Filters.text & ~Filters.command, record_in_arrival_date)],
            RECORD_IN_ARRIVAL_DATE: [CallbackQueryHandler(record_in_arrival_date)],
            MANUAL_RECORD_IN_ARRIVAL_DATE:[MessageHandler(Filters.text & ~Filters.command, manual_record_in_shipping_date)],
            # RECORD_IN_SUPPLIER: [MessageHandler(Filters.text & ~Filters.command, record_in_supplier)],
            RECORD_IN_SUPPLIER: [CallbackQueryHandler(record_in_supplier)],
            # MANUAL_RECORD_IN_SUPPLIER:[MessageHandler(Filters.text, manual_record_in_supplier)],
            # RECORD_IN_PRODUCT: [MessageHandler(Filters.text & ~Filters.command, record_in_product)],
            RECORD_IN_PRODUCT: [CallbackQueryHandler(record_in_product)],
            # MANUAL_RECORD_IN_PRODUCT: [MessageHandler(Filters.text, manual_record_in_product)],
            RECORD_IN_STOCK_IN: [MessageHandler(Filters.text & ~Filters.command, record_in_stock_in)],
            RECORD_IN_UNIT_PRICE: [MessageHandler(Filters.text & ~Filters.command, record_in_unit_price)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler_record_in)
    
    conv_handler_record_in_call = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_add_warehousing, pattern='^record_in$')],
        states={
            # RECORD_IN_ARRIVAL_DATE: [MessageHandler(Filters.text & ~Filters.command, record_in_arrival_date)],
            RECORD_IN_ARRIVAL_DATE: [CallbackQueryHandler(record_in_arrival_date)],
            MANUAL_RECORD_IN_ARRIVAL_DATE:[MessageHandler(Filters.text, manual_record_in_shipping_date)],
            # RECORD_IN_SUPPLIER: [MessageHandler(Filters.text & ~Filters.command, record_in_supplier)],
            RECORD_IN_SUPPLIER: [CallbackQueryHandler(record_in_supplier)],
            # MANUAL_RECORD_IN_SUPPLIER:[MessageHandler(Filters.text, manual_record_in_supplier)],
            # RECORD_IN_PRODUCT: [MessageHandler(Filters.text & ~Filters.command, record_in_product)],
            RECORD_IN_PRODUCT: [CallbackQueryHandler(record_in_product)],
            # MANUAL_RECORD_IN_PRODUCT: [MessageHandler(Filters.text, manual_record_in_product)],
            RECORD_IN_STOCK_IN: [MessageHandler(Filters.text & ~Filters.command, record_in_stock_in)],
            RECORD_IN_UNIT_PRICE: [MessageHandler(Filters.text & ~Filters.command, record_in_unit_price)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler_record_in_call)

    ############################################################
    # add supplier 
    conv_handler_add_supplier = ConversationHandler(
        entry_points=[CommandHandler("add_supplier", start_add_supplier)],
        states={
            ADD_SUPPLIER: [MessageHandler(Filters.text & ~Filters.command, add_supplier)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler_add_supplier)
    
    conv_handler_add_supplier_call = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_add_supplier, pattern="^add_supplier$")],
        states={
            ADD_SUPPLIER: [MessageHandler(Filters.text & ~Filters.command, add_supplier)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler_add_supplier_call)

    ## delete a record in data
    delete_warehousing_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('delete_record_in', start_delete_warehousing)],
        states={
            DELETE_ARRIVAL_DATE: [CallbackQueryHandler(delete_warehousing_arrival_date)],
            MANUAL_DELETE_WAREHOUSING_DATE: [MessageHandler(Filters.text & ~Filters.command, manual_delete_warehousing_date)],
            DELETE_SUPPLIER: [CallbackQueryHandler(delete_warehousing_supplier)],
            DELETE_PRODUCT: [CallbackQueryHandler(delete_warehousing_product)],
            DELETE_SUPPLIER_CONFIRMATION: [CallbackQueryHandler(delete_warehousing_confirmation, pattern=('^(confirm_delete|cancel)$'))]
        },
        fallbacks=[CommandHandler('cancel', cancel)],  
    )
    dispatcher.add_handler(delete_warehousing_conv_handler)
    
    delete_warehousing_conv_handler_call = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_delete_warehousing, pattern='^delete_record_in$', )],
        states={
            DELETE_ARRIVAL_DATE: [CallbackQueryHandler(delete_warehousing_arrival_date)],
            MANUAL_DELETE_WAREHOUSING_DATE: [MessageHandler(Filters.text & ~Filters.command, manual_delete_warehousing_date)],
            DELETE_SUPPLIER: [CallbackQueryHandler(delete_warehousing_supplier)],
            DELETE_PRODUCT: [CallbackQueryHandler(delete_warehousing_product)],
            DELETE_SUPPLIER_CONFIRMATION: [CallbackQueryHandler(delete_warehousing_confirmation, pattern=('^(confirm_delete|cancel)$'))]
        },
        fallbacks=[CommandHandler('cancel', cancel)],  
    )
    dispatcher.add_handler(delete_warehousing_conv_handler_call)

    ## get record results by date 
    conv_handler_find_by_date = ConversationHandler(
        entry_points=[CommandHandler('get_record_in_by_date', start_find_by_date)],
        states={
            FIND_BY_DATE: [CallbackQueryHandler(find_by_date)],
            MANUAL_FIND_WAREHOUSING_DATE: [MessageHandler(Filters.text & ~Filters.command, manual_find_warehousing_date)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler_find_by_date)
    
    conv_handler_find_by_date_call = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_find_by_date, pattern='^get_record_in_by_date$')],
        states={
            FIND_BY_DATE: [CallbackQueryHandler(find_by_date)],
            MANUAL_FIND_WAREHOUSING_DATE: [MessageHandler(Filters.text & ~Filters.command, manual_find_warehousing_date)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler_find_by_date_call)
    
    ## get all record in data
    get_all_warehousing_handler = CommandHandler('get_all_warehousing', get_all_warehousing)
    dispatcher.add_handler(get_all_warehousing_handler)
    dispatcher.add_handler(CallbackQueryHandler(get_all_warehousing, pattern='^get_all_warehousing$'))
    
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
