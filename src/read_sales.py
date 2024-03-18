import csv 
from datetime import datetime, time as datetime_time
from read_customer import Customers 
from read_inventory import Inventories
from helper import check_shipping_date, get_time 

customers_manager = Customers()
inventories_manager = Inventories()

def title_sales():
    return {
            'Sale ID': "销售ID",
            'Shipping Date': "出货日期",
            'Customer': "客户",
            'Product': "产品名称",
            'Stock Out': "出库数量",
            'Unit Price': "单价",
            'Total Price': "总价",
            'Staff': "销售员",
            'Payment': "款项"
        }

class Sale: 
    def __init__(self, sale_id, customer, product, shipping_date=None, 
                 stock_out=0, unit_price=0, staff=None, payment=0):
        if not sale_id:
            # raise ValueError("销售ID为必填项。/ Sale ID are required fields.")
            return ("销售ID为必填项。/ Sale ID are required fields.")
        if not customer or not product or staff is None:
            return ("客户、产品名称和销售员为必填项。/ Customer, product name, and staff are required fields.")
        self._sale_id = sale_id
        self._sale_id_chinese = "销售ID"
        _, self._shipping_date = check_shipping_date(shipping_date)
        self._shipping_date_chinese = "出货日期"
        self._customer = customer
        self._customer_chinese = "客户"
        self._product = product
        self._product_chinese = "产品名称"
        self._stock_out = int(stock_out) if stock_out else 0
        self._stock_out_chinese = "出库数量"
        self._unit_price = float(unit_price) if unit_price else 0 
        self._unit_price_chinese = "单价"
        self._total_price = self._unit_price * self._stock_out
        self._total_price_chinese = "总价"
        self._staff = staff 
        self._staff_chinese = "销售员"
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

    def get_customer(self):
        return self._customer

    def get_customer_chinese(self):
        return self._customer_chinese

    def get_product(self):
        return self._product

    def get_product_chinese(self):
        return self._product_chinese

    def get_stock_out(self):
        return self._stock_out

    def get_stock_out_chinese(self):
        return self._stock_out_chinese

    def get_unit_price(self):
        return self._unit_price

    def get_unit_price_chinese(self):
        return self._unit_price_chinese

    def get_total_price(self):
        return self._total_price

    def get_total_price_chinese(self):
        return self._total_price_chinese

    def get_staff(self):
        return self._staff

    def get_staff_chinese(self):
        return self._staff_chinese

    def get_payment(self):
        return self._payment

    def get_payment_chinese(self):
        return self._payment_chinese
    
    def to_dict(self):
        return {
            'Sale ID': self._sale_id,
            'Shipping Date': self._shipping_date,
            'Customer': self._customer,
            'Product': self._product,
            'Stock Out': self._stock_out,
            'Unit Price': self._unit_price,
            'Total Price': self._total_price,
            'Staff': self._staff,
            'Payment': self._payment
        }

class Sales: 
    def __init__(self):
        self._sales_record_sheet = []
        self._filepath = "./data/sales_record_sheet.csv"        
        self._staff_list = []
        self._filepath_staff = "./data/staff_sheet.csv"
        self.load_sales()
        self.load_staff()

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
                    if float(row['Unit Price']) * int(row['Stock Out']) != float(row['Total Price']):
                        print(f"原来的表格中,日期为{row['Shipping Date']}, 客户为{row['Customer']}，产品为{row['Product']}，销售员为{row['Staff']} 的总价不等于单价x出库数量")
                    self._sales_record_sheet.append(
                        Sale(sale_id=row['Sale ID'], shipping_date=row['Shipping Date'], 
                             customer=row['Customer'], product=row['Product'], stock_out=row['Stock Out'], 
                             unit_price=row['Unit Price'], staff=row['Staff'], payment=row['Payment'])
                    )
                    if row['Staff'] not in self._staff_list:
                        self._staff_list.append(row['Staff'])
        except FileNotFoundError:
            print("销售记录文件未找到，开始为空记录表。/ Sales record file not found. Starting with an empty record sheet.")

    def load_staff(self):
        self._staff_list = []
        try:
            with open(self._filepath_staff, encoding='utf-8') as staff_file:
                reader = csv.DictReader(staff_file)
                i = 0
                for row in reader: 
                    if i == 0:
                        i = 1
                        continue
                    if row['Staff'] not in self._staff_list:
                        self._staff_list.append(row['Staff'])
        except FileNotFoundError:
            print("销售员记录文件未找到，开始为空记录表。")

    def save_staff_to_csv(self):
        with open(self._filepath_staff, 'w', newline='', encoding='utf-8') as staff_file:
            writer = csv.DictWriter(staff_file, fieldnames=['Staff'])
            writer.writeheader()
            writer.writerow({'Staff': "销售员"})
            for staff in self._staff_list:
                writer.writerow({'Staff': staff})

    def clear_staff(self):
        self._staff_list = []
        with open(self._filepath_staff, 'w', newline='', encoding='utf-8') as staff_file:
            writer = csv.DictWriter(staff_file, fieldnames=['Staff'])
            writer.writeheader()
            writer.writerow({'Staff': "销售员"})

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

    def clear_sales(self):
        with open(self._filepath, 'w', newline='', encoding='utf-8') as file:
            fieldnames = title_sales().keys()
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(title_sales())
        self._sales_record_sheet.clear()
        self._sales_record_sheet = []

    def sort_sales_by_id(self):
        # Sort the sales record sheet by sale ID
        self._sales_record_sheet.sort(key=lambda sale: sale.get_sale_id())

    def create_sale_id(self, shipping_date):
        current_datetime = datetime.now()  # 当前时间对象
        if not shipping_date:
            # 如果没有提供shipping_date，使用当前日期
            shipping_date = current_datetime.strftime("%Y%m%d")  # 格式化为 'YYYYMMDD'
            date_obj = current_datetime.strftime('%d/%m/%Y')  # 格式化为 'DD/MM/YYYY'
        else:
            # 验证并格式化提供的shipping_date
            shipping_date, date_obj = check_shipping_date(shipping_date)
            if not shipping_date:
                return False, date_obj  # 如果日期验证失败，返回错误信息

        # 获取当前时间
        time = get_time()

        # 组合shipping_date和time作为唯一ID
        return shipping_date + time, date_obj

    def sale_id_exists(self, sale_id):
        for sale in self._sales_record_sheet:
            if sale._sale_id == sale_id:
                return True
        return False
    
    def add_sale(self, customer, product, shipping_date=None,
                 stock_out=0, unit_price=0, staff=None, payment=0):            
        print(f"received {customer}, {shipping_date}")
        self.load_sales()
        self.load_staff()
        tmp_sale_id, shipping_date = self.create_sale_id(shipping_date)
        if tmp_sale_id is False:
            return shipping_date
        
        # 检查销售ID是否存在
        i = 0
        while self.sale_id_exists(tmp_sale_id) and i <= 10:
            tmp_sale_id, shipping_date = self.create_sale_id(shipping_date)
            i += 1

        if i >= 10 and self.sale_id_exists(tmp_sale_id):
            return f"销售记录ID {tmp_sale_id} 已存在，不能添加重复记录。"
        
        sale = Sale(sale_id=tmp_sale_id, shipping_date=shipping_date, customer=customer, 
                    product=product, stock_out=stock_out, unit_price=unit_price, 
                    staff=staff, payment=payment)
        self._sales_record_sheet.append(sale)
        if staff is not None:
            if staff not in self._staff_list:
                self._staff_list.append(staff)
                self.save_staff_to_csv()
        self.save_sales_to_csv()
        self.add_customer_and_inventories(customer, (float(unit_price) * int(stock_out)), payment, product, stock_out)
        print(f"销售记录ID {tmp_sale_id} 已成功添加。/ Sale with ID {tmp_sale_id} added successfully.")        
        return f"销售记录ID {tmp_sale_id} 已成功添加。"
    
    def add_customer_and_inventories(self, customer_name, payable, payment, product, stock_out):
        customers_manager.add_or_update_customer(customer_name=customer_name, payable=payable, payment=payment)
        inventories_manager.add_or_update_product(product=product, stock_in=0, stock_out=stock_out, schedule_inventory=None)

    def add_staff(self, staff):
        self.load_sales()
        self.load_staff()
        if staff is not None and staff not in self._staff_list:
            self._staff_list.append(staff)
            self.save_staff_to_csv()
            return True 
        return False
        

    def delete_sale(self, sale_id):
        """删除指定销售ID的销售记录"""
        self.load_sales()
        for i, sale in enumerate(self._sales_record_sheet):
            if str(sale.get_sale_id()) != str(sale_id):
                self.add_customer_and_inventories(sale.get_customer(), -sale.get_total_price(), -sale.get_payment(), sale.get_product(), -sale.get_stock_out())
                del self._sales_record_sheet[i]
                print(f"销售记录ID {sale_id} 已被删除。")
        # self._sales_record_sheet = [sale for sale in self._sales_record_sheet if str(sale.get_sale_id()) != str(sale_id)]
        self.save_sales_to_csv()  # 更新CSV文件
        return f"销售记录ID {sale_id} 已被删除。"

    def find_sale_by_id(self, sale_id):
        """根据销售ID查找销售记录"""
        self.load_sales()
        for sale in self._sales_record_sheet:
            if str(sale.get_sale_id()) == str(sale_id):
                return True, [sale]
        return False, (f"{sale_id} -- 没有找到匹配的记录")
    
    def find_sales_by_customer(self, customer_name):
        """根据客户名称查找该客户的所有购买记录"""
        self.load_sales()
        matching_sales = []
        flag = False
        for sale in self._sales_record_sheet:
            if sale.get_customer() == customer_name:
                matching_sales.append(sale)
                flag = True
        return flag, matching_sales
    
    def get_staff_name_list(self):
        # sales_list = set()
        self.load_staff()
        self.load_sales()
        # for sale in self._sales_record_sheet:
        #     if sale.get_staff() not in sales_list:
        #         sales_list.add(sale.get_staff())
        print(f"supplier list : {self._staff_list}")
        return self._staff_list
    
    def get_customer_name_list(self):
        sales_list = set()
        self.load_sales()
        for sale in self._sales_record_sheet:
            if sale.get_customer() not in sales_list:
                sales_list.add(sale.get_customer())
        print(f"customer list in sales: {sales_list}")
        return list(sales_list)
    
    def get_all(self):
        self.load_sales()
        return self._sales_record_sheet 

if __name__ == "__main__":
    sales_manager = Sales()
    all_sales = sales_manager.get_all()
    
    print(sales_manager.find_sales_by_customer("小明"))
    # print(sales_manager.find_sales_by_customer("Customer 3"))
    _, sales_info = sales_manager.find_sales_by_customer("Customer 3")
    for sale in sales_info:
        print(f"{sale.get_product()}")
    print(sales_manager.find_sale_by_id("20240313013422266"))
