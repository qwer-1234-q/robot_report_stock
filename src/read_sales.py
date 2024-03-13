import csv 
from datetime import datetime, time as datetime_time

def title_sales():
    return {
            'Sale ID': "销售ID",
            'Shipping Date': "出货日期",
            'Time': "出货时间",
            'Customer': "客户",
            'Product': "产品名称",
            'Outbound Quantity': "出库数量",
            'Unit Price': "单价",
            'Total Price': "总价",
            'Seller': "销售员",
            'Payment': "款项"
        }

def check_shipping_date(shipping_date):
    # Validate and format shipping_date
    # Check if shipping_date is already a datetime object
    if isinstance(shipping_date, datetime):
        return shipping_date.strftime('%Y%m%d'), shipping_date.strftime('%d/%m/%Y')

    # If shipping_date is a string, proceed with the original logic
    if shipping_date:
        try:
            # Try to parse the string as a date        
            shipping_date = str(shipping_date)
            date_obj = datetime.strptime(shipping_date, '%d/%m/%Y')
            return date_obj.strftime('%Y%m%d'), date_obj.strftime('%d/%m/%Y')
        except ValueError:
            try:
                # Try another format
                date_obj = datetime.strptime(shipping_date, '%d-%m-%Y')
                return date_obj.strftime('%Y%m%d'), date_obj.strftime('%d/%m/%Y')
            except ValueError:
                # If input doesn't match expected formats, raise an error
                # raise ValueError(f"{shipping_date} - 提供的出货日期无效或格式不正确。/ Provided shipping date is invalid or in incorrect format.")
                return False, (f"{shipping_date} - 提供的出货日期无效或格式不正确。/ Provided shipping date is invalid or in incorrect format.")
    else:
        # If no shipping_date is provided, use the current date
        date_obj = datetime.now()
        return date_obj.strftime('%Y%m%d'), date_obj.strftime('%d/%m/%Y')

def check_time(time):
    # Validate and format time
    # Remove any trailing periods or other unexpected characters
    if time:
        time = time.rstrip('.')  # Remove trailing period
        format_options = [
            '%H:%M:%S.%f',  # Format including milliseconds
            '%H:%M:%S',  # Format without milliseconds
            '%H%M%S%f',  # Compact format including milliseconds
            '%H%M%S',  # Compact format without milliseconds
            '%H%M',
            '%H:%M'
        ]
        for format_option in format_options:
            try:
                time_obj = datetime.strptime(time, format_option)
                return time_obj.strftime('%H%M%S%f')[:9], time_obj.strftime('%H:%M:%S.%f')[:12]  # Correct formatting
            except ValueError:
                continue  # Try the next format option
        # If none of the formats match, raise an error
        return False, (f"{time} : 提供的出货时间无效或格式不正确。/ Provided shipping time is invalid or in incorrect format.")
        # raise ValueError(f"{time} : 提供的出货时间无效或格式不正确。/ Provided shipping time is invalid or in incorrect format.")
    else:
        # Use the current time if no time is provided
        time_obj = datetime.now()
        return time_obj.strftime('%H%M%S%f')[:9], time_obj.strftime('%H:%M:%S.%f')[:12]

class Sale: 
    def __init__(self, sale_id, customer, product, shipping_date=None, time=None,
                 outbound_quantity=0, unit_price=0, seller=None, payment=0):
        if not sale_id:
            # raise ValueError("销售ID为必填项。/ Sale ID are required fields.")
            return ("销售ID为必填项。/ Sale ID are required fields.")
        if not customer or not product or seller is None:
            return ("客户、产品名称和销售员为必填项。/ Customer, product name, and seller are required fields.")
        self._sale_id = sale_id
        self._sale_id_chinese = "销售ID"
        _, self._shipping_date = check_shipping_date(shipping_date)
        self._shipping_date_chinese = "出货日期"
        _, self._time = check_time(time) 
        self._time_chinese = "出货时间"
        self._customer = customer
        self._customer_chinese = "客户"
        self._product = product
        self._product_chinese = "产品名称"
        self._outbound_quantity = int(outbound_quantity) if outbound_quantity else 0
        self._outbound_quantity_chinese = "出库数量"
        self._unit_price = float(unit_price) if unit_price else 0 
        self._unit_price_chinese = "单价"
        self._total_price = self._unit_price * self._outbound_quantity
        self._total_price_chinese = "总价"
        self._seller = seller 
        self._seller_chinese = "销售员"
        self._payment = float(payment) if payment else 0
        self._payment_chinese = "款项"

    def get_sale_id(self):
        return self._sale_id
    
    def get_sale_id_chinese(self):
        return self._sale_id_chinese
    
    def get_shipping_date(self):
        return self._shipping_date

    def get_shipping_date_chinese(self):
        return self._shipping_date_chinese

    def get_time(self):
        return self._time
    
    def get_time_chinese(self):
        return self._time_chinese

    def get_customer(self):
        return self._customer

    def get_customer_chinese(self):
        return self._customer_chinese

    def get_product(self):
        return self._product

    def get_product_chinese(self):
        return self._product_chinese

    def get_outbound_quantity(self):
        return self._outbound_quantity

    def get_outbound_quantity_chinese(self):
        return self._outbound_quantity_chinese

    def get_unit_price(self):
        return self._unit_price

    def get_unit_price_chinese(self):
        return self._unit_price_chinese

    def get_total_price(self):
        return self._total_price

    def get_total_price_chinese(self):
        return self._total_price_chinese

    def get_seller(self):
        return self._seller

    def get_seller_chinese(self):
        return self._seller_chinese

    def get_payment(self):
        return self._payment

    def get_payment_chinese(self):
        return self._payment_chinese
    
    def to_dict(self):
        return {
            'Sale ID': self._sale_id,
            'Shipping Date': self._shipping_date,
            'Time': self._time,
            'Customer': self._customer,
            'Product': self._product,
            'Outbound Quantity': self._outbound_quantity,
            'Unit Price': self._unit_price,
            'Total Price': self._total_price,
            'Seller': self._seller,
            'Payment': self._payment
        }

class Sales: 
    def __init__(self):
        self._sales_record_sheet = []
        self._filepath = "./data/sales_record_sheet.csv"
        self.load_sales()

    def load_sales(self):
        self._sales_record_sheet = []    
        try:
            with open(self._filepath, encoding='utf-8') as sales_files:
                reader = csv.DictReader(sales_files)
                i = 0
                for row in reader: 
                    if i == 0:
                        i = 1
                        continue
                    if row["Customer"] == '' or len(row['Customer']) == 0 or row["Customer"] is None: 
                        continue
                    if row['Sale ID'] is None or row['Sale ID'] == '':
                        continue 
                    if float(row['Unit Price']) * int(row['Outbound Quantity']) != float(row['Total Price']):
                        print(f"原来的表格中,日期为{row['Shipping Date']}, 客户为{row['Customer']}，产品为{row['Product']}，销售员为{row['Seller']} 的总价不等于单价x出库数量")
                    self._sales_record_sheet.append(
                        Sale(sale_id=row['Sale ID'], shipping_date=row['Shipping Date'], time=row['Time'], 
                             customer=row['Customer'], product=row['Product'], outbound_quantity=row['Outbound Quantity'], 
                             unit_price=row['Unit Price'], seller=row['Seller'], payment=row['Payment'])
                    )
        except FileNotFoundError:
            print("销售记录文件未找到，开始为空记录表。/ Sales record file not found. Starting with an empty record sheet.")

    def create_sale_id(self, shipping_date, time):
        current_datetime = datetime.now()  # This is a datetime object, not a string
        if shipping_date is None or shipping_date == '' or shipping_date == ' ':
            try:
                shipping_date = current_datetime.strftime("%Y%m%d")  # Format as 'YYYYMMDD'
                date_obj = current_datetime.strftime('%d/%m/%Y')  # Correctly format as 'DD/MM/YYYY'
            except ValueError:
                return False, (f"{shipping_date} - 提供的出货日期无效或格式不正确。/ Provided shipping date is invalid or in incorrect format."), False
        else:
            shipping_date, date_obj = check_shipping_date(shipping_date)  # Presuming check_shipping_date returns formatted shipping_date and date_obj
            if shipping_date == False:
                return False, date_obj, False

        if time is None or time == '' or time == ' ':
            try:
                time = current_datetime.strftime("%H%M%S%f")[:9]  # Format as 'HHMMSSfff' for milliseconds
                time_obj = current_datetime.strftime('%H:%M:%S.%f')[:12]  # Correctly format as 'HH:MM:SS.fff' including milliseconds
            except:
                return False, shipping_date, (f"{time} : 提供的出货时间无效或格式不正确。/ Provided shipping time is invalid or in incorrect format.")
        else:
            time, time_obj = check_time(time)  # Presuming check_time returns formatted time and time_obj
            if time is False:
                return False, shipping_date, time_obj

        return shipping_date + time, date_obj, time_obj

    def sale_id_exists(self, sale_id):
        for sale in self._sales_record_sheet:
            if sale._sale_id == sale_id:
                return True
        return False
    
    def add_sale(self, customer, product, shipping_date=None, time=None, 
                 outbound_quantity=0, unit_price=0, seller=None, payment=0):            
        print(f"received {customer}, {shipping_date}, {time}")
        if time is not None:
            hour, minute = time.split(':')
            if len(hour) < 2:
                hour = '0' + hour 
            if len(minute) < 2:
                minute = '0' + minute
            time = hour + ":" + minute
        tmp_sale_id, shipping_date, time = self.create_sale_id(shipping_date, time)
        if tmp_sale_id is False:
            if time is False: 
                return shipping_date 
            else:
                return time
        i = 0
        while self.sale_id_exists(tmp_sale_id) and i <= 10:
            tmp_sale_id, shipping_date, time = self.create_sale_id(shipping_date, time)
            i += 1
        if i >= 10:
            if self.sale_id_exists(tmp_sale_id):
                print(f"销售记录ID {tmp_sale_id} 已存在，不能添加重复记录。/ Sale with ID {tmp_sale_id} already exists. Cannot add duplicate.")
                return (f"销售记录ID {tmp_sale_id} 已存在，不能添加重复记录。/ Sale with ID {tmp_sale_id} already exists. Cannot add duplicate.")
        sale = Sale(sale_id=tmp_sale_id, shipping_date=shipping_date,time=time, customer=customer, 
                    product=product, outbound_quantity=outbound_quantity, unit_price=unit_price, 
                    seller=seller, payment=payment)
        self._sales_record_sheet.append(sale)
        self.save_sales_to_csv()
        print(f"销售记录ID {tmp_sale_id} 已成功添加。/ Sale with ID {tmp_sale_id} added successfully.")
        return (f"销售记录ID {tmp_sale_id} 已成功添加。/ Sale with ID {tmp_sale_id} added successfully.")
    
    def delete_sale(self, sale_id):
        """删除指定销售ID的销售记录"""
        self._sales_record_sheet = [sale for sale in self._sales_record_sheet if str(sale.get_sale_id()) != str(sale_id)]
        self.save_sales_to_csv()  # 更新CSV文件
        return (f"销售记录ID {sale_id} 已被删除。")

    def find_sale_by_id(self, sale_id):
        """根据销售ID查找销售记录"""
        for sale in self._sales_record_sheet:
            if str(sale.get_sale_id()) == str(sale_id):
                return True, [sale]
        return False, (f"{sale_id} -- 没有找到匹配的记录")
    
    def find_sales_by_customer(self, customer_name):
        """根据客户名称查找该客户的所有购买记录"""
        matching_sales = [sale for sale in self._sales_record_sheet if sale.get_customer() == customer_name]
        if len(matching_sales) > 1:
            return True, matching_sales
        return False, matching_sales
    
    def sort_sales_by_id(self):
        # Sort the sales record sheet by sale ID
        self._sales_record_sheet.sort(key=lambda sale: sale.get_sale_id())

    def save_sales_to_csv(self):
        self.sort_sales_by_id()
        # If a specific sale is provided, append it to the file
        with open(self._filepath, 'w', newline='', encoding='utf-8') as file:
            fieldnames = title_sales().keys()
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(title_sales())
            for sale in self._sales_record_sheet:
                writer.writerow(sale.to_dict())

    def get_all(self):
        self.load_sales()
        return self._sales_record_sheet 

if __name__ == "__main__":
    sales_manager = Sales()
    all_sales = sales_manager.get_all()
    
    print(sales_manager.find_sales_by_customer("小明"))
    print(sales_manager.find_sale_by_id("20240313013422266"))
    
