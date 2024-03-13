import csv
from datetime import datetime

class Warehousing:
    def __init__(self, arrival_date, supplier, product, inbound_quantity, 
                 unit_price, total_price):
        self._arrival_date = arrival_date
        self._arrival_date_chinese = "到货日期"
        self._supplier = supplier
        self._supplier_chinese = "供应商"
        self._product = product 
        self._product_chinese = "产品名称"
        self._inbound_quantity = inbound_quantity 
        self._inbound_quantity_chinese = "入库数量"
        self._unit_price = unit_price 
        self._unit_price_chinese = "单价"
        self._total_price = total_price 
        self._total_price_chinese = "总价"
    
    @staticmethod
    def _validate_and_format_date(date_str):
        """验证并格式化日期为日/月/年格式"""
        try:
            # 尝试根据预期格式解析日期字符串
            date_obj = datetime.strptime(date_str, "%d/%m/%Y")
        except ValueError:
            # 如果解析失败，提供中英文结合的错误消息
            raise ValueError("到货日期格式不正确，正确格式应为日/月/年。 / Arrival date format is incorrect, the correct format should be DD/MM/YYYY.")
        # 如果解析成功，返回格式化的日期字符串
        return date_obj.strftime("%d/%m/%Y")
    
    def get_arrival_date(self):
        return self._arrival_date
    
    def get_arrival_date_chinese(self):
        return self._arrival_date_chinese
    
    def get_supplier(self):
        return self._supplier 

    def get_supplier_chinese(self):
        return self._supplier_chinese 
    
    def get_product(self):
        return self._product
    
    def get_product_chinese(self):
        return self._product_chinese 
    
    def get_inbound_quantity(self):
        return self._inbound_quantity 
    
    def get_inbound_quantity_chinese(self):
        return self._inbound_quantity_chinese
    
    def get_unit_price(self):
        return self._unit_price
    
    def get_unit_price_chinese(self):
        return self._unit_price_chinese
    
    def get_total_price(self):
        return self._total_price
    
    def get_total_price_chinese(self):
        return self._total_price_chinese
    

class Warehousing_read:
    def __init__(self):
        self._warehousing_table = []
        self._filepath = "./data/warehousing_table.csv"
    
    def load_warehousing(self):
        self._warehousing_table.clear()
        with open(self._filepath, encoding='utf-8') as warehousing_file:
            reader = csv.DictReader(warehousing_file)
            i = 0
            for row in reader: 
                if i == 0:
                    i = 1
                    continue
                self._warehousing_table.append(
                   Warehousing(row['Arrival Date'], row['Supplier'], row['Product'],
                            row['Inbound Quantity'], row['Unit Price'], row['Total Price']) 
                )

    def sort_records(self):
        """根据到货日期从新到旧、供应商从A-Z、产品名称从A-Z、入库数量从小到大、单价从小到大进行排序"""
        self._warehousing_table = sorted(self._warehousing_table, key=lambda item: (
            datetime.strptime(item.get_arrival_date(), "%d/%m/%Y"),  # 将日期字符串转换为datetime对象进行比较
            item.get_supplier(),
            item.get_product(),
            int(item.get_inbound_quantity()),  # 确保入库数量作为整数进行比较
            float(item.get_unit_price())  # 确保单价作为浮点数进行比较
        ))
   
    def save_to_csv(self):
        """将排序后的数据保存到CSV文件"""
        self.sort_records()
        fieldnames = ['Arrival Date', 'Supplier', 'Product', 'Inbound Quantity', 'Unit Price', 'Total Price']
        with open(self._filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({
                    'Arrival Date': "到货日期",
                    'Supplier': "供应商",
                    'Product': "产品名称",
                    'Inbound Quantity': "入库数量",
                    'Unit Price': "单价",
                    'Total Price': "总价"
                })
            for item in self._warehousing_table:
                writer.writerow({
                    'Arrival Date': item.get_arrival_date(),
                    'Supplier': item.get_supplier(),
                    'Product': item.get_product(),
                    'Inbound Quantity': item.get_inbound_quantity(),
                    'Unit Price': item.get_unit_price(),
                    'Total Price': item.get_total_price()
                })

    def add_warehousing_record(self, arrival_date, supplier, product, inbound_quantity, unit_price, total_price):
        """添加一个新的仓储记录"""
        # 检验到货日期格式是否正确，如果不正确，抛出异常
        try:
            datetime.strptime(arrival_date, "%d/%m/%Y")
        except ValueError:
            # raise ValueError("到货日期格式不正确。正确格式应为日/月/年。/ Arrival date format is incorrect. The correct format is DD/MM/YYYY.")
            return "到货日期格式不正确。正确格式应为日/月/年。/ Arrival date format is incorrect. The correct format is DD/MM/YYYY."
        
        # 计算总价，如果没有提供，则根据单价和入库数量计算
        if total_price is None:
            total_price = float(unit_price) * int(inbound_quantity)
        
        # 创建一个新的Warehousing实例并添加到列表中
        new_record = Warehousing(arrival_date, supplier, product, inbound_quantity, unit_price, total_price)
        self._warehousing_table.append(new_record)
        self.save_to_csv()
        return f"{arrival_date} {supplier} {product} {inbound_quantity} 已经成功录入 / Successful!"
    
    def delete_warehousing_record(self, arrival_date, supplier, product):
        """根据到货日期、供应商和产品名称删除仓储记录"""
        # 首先检验到货日期格式是否正确
        try:
            datetime.strptime(arrival_date, "%d/%m/%Y")
        except ValueError:
            # raise ValueError("到货日期格式不正确。正确格式应为日/月/年。/ Arrival date format is incorrect. The correct format is DD/MM/YYYY.")
            return "到货日期格式不正确。正确格式应为日/月/年。/ Arrival date format is incorrect. The correct format is DD/MM/YYYY."
        
        # 查找并删除匹配的记录
        deleted = False
        for i, record in enumerate(self._warehousing_table):
            if (record.get_arrival_date() == arrival_date and 
                record.get_supplier() == supplier and 
                record.get_product() == product):
                del self._warehousing_table[i]
                deleted = True
                break  # 假设每个到货日期、供应商和产品名称的组合是唯一的，找到后即删除
                
        if not deleted:
            print(f"没有找到匹配的记录来删除。/ No matching record found to delete.")
            return f"没有找到匹配的记录来删除。/ No matching record found to delete."
        else:
            print(f"记录已被删除。/ Record has been deleted.")
            self.save_to_csv()
            return f"{supplier} 记录已被删除。/ Record has been deleted."

    def update_inbound_quantity_or_unit_price(self, arrival_date, supplier, product, new_quantity=None, unit_price=None):
        """根据到货日期、供应商和产品名称更新入库数量"""
        # 首先检验到货日期格式是否正确
        try:
            datetime.strptime(arrival_date, "%d/%m/%Y")
        except ValueError:
            # raise ValueError("到货日期格式不正确。正确格式应为日/月/年。/ Arrival date format is incorrect. The correct format is DD/MM/YYYY.")
            return "到货日期格式不正确。正确格式应为日/月/年。/ Arrival date format is incorrect. The correct format is DD/MM/YYYY."
        
        # 查找并更新匹配的记录
        updated = False
        for record in self._warehousing_table:
            if (record.get_arrival_date() == arrival_date and 
                record.get_supplier() == supplier and 
                record.get_product() == product):
                if new_quantity is not None:
                    record._inbound_quantity = new_quantity  # 直接更新入库数量
                if unit_price is not None:
                    record._unit_price = unit_price
                record._total_price = float(record.get_unit_price()) * int(record._inbound_quantity)
                updated = True
                break  # 假设每个到货日期、供应商和产品名称的组合是唯一的，找到后即更新
                
        if not updated:
            print(f"没有找到匹配的记录来更新。/ No matching record found to update.")
            return f"没有找到匹配的记录来更新。/ No matching record found to update."
        else:
            self.save_to_csv()
            print(f"记录已被更新。/ Record has been updated.")
            return f"记录已被更新。/ Record has been updated."
            
    def find_by_date(self, date_str):
        """根据到货日期查找入库记录"""
        # 将字符串日期转换为datetime对象以便比较
        target_date = datetime.strptime(date_str, "%d/%m/%Y")
        # 查找所有与给定日期匹配的记录
        matching_records = [item for item in self._warehousing_table if datetime.strptime(item.get_arrival_date(), "%d/%m/%Y") == target_date]
        return matching_records
    
    def find_by_supplier(self, supplier_name):
        """根据供应商查找入库记录"""
        # 查找所有与给定供应商名称匹配的记录
        matching_records = [item for item in self._warehousing_table if item.get_supplier() == supplier_name]
        return matching_records
    
    def get_all(self):
        self.load_warehousing()
        return self._warehousing_table

if __name__ == "__main__":
    warehousing_manager = Warehousing_read()
    for item in warehousing_manager.get_all():
        print(f"{item.get_arrival_date_chinese()}: {item.get_arrival_date()} | {item.get_supplier_chinese()}: {item.get_supplier()} | {item.get_product_chinese()}: {item.get_product()} | {item.get_inbound_quantity_chinese()}: {item.get_inbound_quantity()} | {item.get_unit_price_chinese()}: {item.get_unit_price()} | {item.get_total_price_chinese()}: {item.get_total_price()}")
    
    # 添加一个新的记录示例
    warehousing_manager.add_warehousing_record("15/03/2024", "供应商A", "产品X", 100, 20.5, None)
    warehousing_manager.add_warehousing_record("15/03/2024", "供应商B", "产品Y", 200, 10, None)
    warehousing_manager.add_warehousing_record("15/03/2024", "供应商C", "产品Z", 300, 10.23, None)
    # 打印所有记录，验证新记录已被添加
    for item in warehousing_manager.get_all():
        print(f"{item.get_arrival_date_chinese()}: {item.get_arrival_date()} | {item.get_supplier_chinese()}: {item.get_supplier()} | {item.get_product_chinese()}: {item.get_product()} | {item.get_inbound_quantity_chinese()}: {item.get_inbound_quantity()} | {item.get_unit_price_chinese()}: {item.get_unit_price()} | {item.get_total_price_chinese()}: {item.get_total_price()}")
    
    print("\n")
    print("-"*50)
    # 更新一个记录的入库数量示例
    warehousing_manager.update_inbound_quantity_or_unit_price("15/03/2024", "供应商A", "产品X", 500)
    warehousing_manager.update_inbound_quantity_or_unit_price("15/03/2024", "供应商B", "产品Y", 500, 4000)
    warehousing_manager.update_inbound_quantity_or_unit_price("15/03/2024", "供应商C", "产品Z", unit_price=500)
    # 打印所有记录，验证入库数量已被更新
    for item in warehousing_manager.get_all():
        print(f"{item.get_arrival_date_chinese()}: {item.get_arrival_date()} | {item.get_supplier_chinese()}: {item.get_supplier()} | {item.get_product_chinese()}: {item.get_product()} | {item.get_inbound_quantity_chinese()}: {item.get_inbound_quantity()} | {item.get_unit_price_chinese()}: {item.get_unit_price()} | {item.get_total_price_chinese()}: {item.get_total_price()}")
    
    print("\n")
    print("-"*50)
    # 删除一个记录示例
    warehousing_manager.delete_warehousing_record("15/03/2024", "供应商A", "产品X")
    # 打印所有记录，验证记录已被删除
    for item in warehousing_manager.get_all():
        print(f"{item.get_arrival_date_chinese()}: {item.get_arrival_date()} | {item.get_supplier_chinese()}: {item.get_supplier()} | {item.get_product_chinese()}: {item.get_product()} | {item.get_inbound_quantity_chinese()}: {item.get_inbound_quantity()} | {item.get_unit_price_chinese()}: {item.get_unit_price()} | {item.get_total_price_chinese()}: {item.get_total_price()}")
    
    print("\n")
    print("-"*50)
    date_str = "12/03/2024"  # 示例日期，根据需要更改
    matching_records = warehousing_manager.find_by_date(date_str)
    # 打印找到的记录
    for item in matching_records:
        print(f"{item.get_arrival_date_chinese()}: {item.get_arrival_date()} | {item.get_supplier_chinese()}: {item.get_supplier()} | {item.get_product_chinese()}: {item.get_product()} | {item.get_inbound_quantity_chinese()}: {item.get_inbound_quantity()} | {item.get_unit_price_chinese()}: {item.get_unit_price()} | {item.get_total_price_chinese()}: {item.get_total_price()}")
    
    print("\n")
    print("-"*50)
    supplier_name = "供应商A"  # 示例供应商名称，根据需要更改
    matching_records = warehousing_manager.find_by_supplier(supplier_name)
    # 打印找到的记录
    for item in matching_records:
        print(f"{item.get_arrival_date_chinese()}: {item.get_arrival_date()} | {item.get_supplier_chinese()}: {item.get_supplier()} | {item.get_product_chinese()}: {item.get_product()} | {item.get_inbound_quantity_chinese()}: {item.get_inbound_quantity()} | {item.get_unit_price_chinese()}: {item.get_unit_price()} | {item.get_total_price_chinese()}: {item.get_total_price()}")
