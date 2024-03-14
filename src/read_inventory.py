import csv 
from datetime import datetime
import random
from helper import handle_data

def get_inventory_title():
    return {
                'Product': "产品名称",
                'Opening inventory': "初始库存数量",
                'Stock In': "入库总数量",
                'Stock out': "出库总数量",
                'Schedule inventory': "预定总数量",
                'Total inventory': "库存总数量",
                'In stock': "可用库存"
            }

class Inventory:
    def __init__(self, product, opening_inventory=0, stock_in=0, 
                 stock_out=0, schedule_inventory=0, total_inventory=None, in_stock=None):
        self._product = product 
        self._product_chinese = "产品名称"
        self._opening_inventory = int(opening_inventory)
        self._opening_inventory_chinese = "初始库存数量"
        self._stock_in = int(stock_in)
        self._stock_in_chinese = "入库总数量"
        self._stock_out = int(stock_out) 
        self._stock_out_chinese = "出库总数量"
        self._schedule_inventory = int(schedule_inventory)
        self._schedule_inventory_chinese = "预定总数量"
        if handle_data(total_inventory) == 0:
            self._total_inventory = str(int(self._opening_inventory) - int(self._stock_out) + int(self._stock_in))
        else:
            self._total_inventory = int(total_inventory)
        self._total_inventory_chinese = "库存总数量"
         
        if handle_data(in_stock) == 0:
            self._in_stock = str(int(self._total_inventory) - int(self._schedule_inventory))
        else: 
            self._in_stock = int(in_stock)
        self._in_stock_chinese = "可用库存"
        
    def get_product(self):
        return self._product 
    
    def get_product_chinese(self):
        return self._product_chinese 
    
    def get_opening_inventory(self):
        return self._opening_inventory 
    
    def get_opening_inventory_chinese(self):
        return self._opening_inventory_chinese 
    
    def get_stock_in(self):
        return self._stock_in
    
    def get_stock_in_chinese(self):
        return self._stock_in_chinese 
    
    def get_stock_out(self):
        return self._stock_out 
    
    def get_stock_out_chinese(self):
        return self._stock_out_chinese 
    
    def get_schedule_inventory(self):
        return self._schedule_inventory 
    
    def get_schedule_inventory_chinese(self):
        return self._schedule_inventory_chinese 
    
    def get_total_inventory(self):
        return self._total_inventory 
    
    def get_total_inventory_chinese(self):
        return self._total_inventory_chinese

    def get_in_stock(self):
        return self._in_stock  
    
    def get_in_stock_chinese(self):
        return self._in_stock_chinese
    
    def to_dict(self):
        return {
                    'Product': self.get_product(),
                    'Opening inventory': self.get_opening_inventory(),
                    'Stock In': self.get_stock_in(),
                    'Stock out': self.get_stock_out(),
                    'Schedule inventory': self.get_schedule_inventory(),
                    'Total inventory': self.get_total_inventory(),
                    'In stock': self.get_in_stock()
                }
    
class Inventories:
    def __init__(self):
        self._inventory_table = []
        self.load_inventory_data()

    def load_inventory_data(self):
        self._inventory_table.clear()
    
        with open("./data/inventory_table.csv", encoding='utf-8') as inventory_file:
            reader = csv.DictReader(inventory_file)
            i = 0
            for row in reader: 
                if i == 0:
                    i = 1
                    continue
                if row["Product"] == '' or len(row['Product']) == 0 or row["Product"] is None: 
                    continue
                tmp_opening_inventory = handle_data(row["Opening inventory"]) 
                tmp_stock_in = handle_data(row["Stock In"])
                tmp_stock_out = handle_data(row["Stock out"] )
                tmp_schedule_inventory = handle_data(row["Schedule inventory"]) 
                tmp_total_inventory = handle_data(row["Total inventory"]) 
                tmp_in_stock = handle_data(row["In stock"]) 
                self._inventory_table.append(
                    Inventory(row['Product'], tmp_opening_inventory, tmp_stock_in, 
                            tmp_stock_out, tmp_schedule_inventory, tmp_total_inventory, tmp_in_stock)
                )

    def save_inventory_table(self):
        self._inventory_table = self.get_sorted_inventory_by_stock('all')
        with open("./data/inventory_table.csv", 'w', encoding='utf-8', newline='') as inventory_file:            
            writer = csv.DictWriter(inventory_file, fieldnames=get_inventory_title().keys())
            writer.writeheader()
            writer.writerow(get_inventory_title())
            for item in self._inventory_table:
                writer.writerow(item.to_dict())

    def clear_inventory_table(self):
        self._inventory_table.clear()
        with open("./data/inventory_table.csv", 'w', encoding='utf-8', newline='') as inventory_file:
            writer = csv.DictWriter(inventory_file, fieldnames=get_inventory_title().keys())
            writer.writeheader()
            writer.writerow(get_inventory_title())

    def get_product_data(self, product_name):
        for product in self._inventory_table:
            if str(product.get_product()) == str(product_name):
                # Product found, return its data
                return product.to_dict()
        # Product not found, return a message indicating so
        return f"产品 '{product_name}' 未找到。"

    def add_or_update_product(self, product, stock_in=None, stock_out=None, schedule_inventory=None):
        self.get_sorted_products_by_name()  # 首先排序库存信息
        found = False

        for item in self._inventory_table:
            if (item.get_product()) == product:
                # 找到产品后，更新库存信息
                found = True
                item._opening_inventory = item.total_inventory 
                item._stock_in = int(handle_data(stock_in))
                item._stock_out = int(handle_data(stock_out))
                item._schedule_inventory += int(handle_data(schedule_inventory))
                
                # 重新计算总库存和可用库存
                item._total_inventory = item._opening_inventory + item._stock_in - item._stock_out
                item._in_stock = item._total_inventory - item._schedule_inventory
                break

        if not found:
            # 如果没有找到产品，则添加新的产品记录
            new_product = Inventory(product, 0, int(stock_in), int(stock_out), int(schedule_inventory), total_inventory=None, in_stock=None)
            self._inventory_table.append(new_product)

        self.save_inventory_table()
        return f"产品 '{product}' 的库存信息已更新。"

    def delete_product_by_name(self, product_name):
        """
        根据产品名称删除库存中的产品。
        Deletes a product from the inventory based on the product name.

        Parameters:
        - product_name (str): 要删除的产品名称。
                              The name of the product to be deleted.

        Returns:
        - None, but prints a message indicating the outcome.
        """
        # Search for the product by name
        for i, item in enumerate(self._inventory_table):
            if item.get_product() == product_name:
                # If found, delete the product from the inventory
                del self._inventory_table[i]
                print(f"产品 '{product_name}' 已从库存中删除。/ Product '{product_name}' has been deleted from inventory.")
                self.save_inventory_table()
                return f"产品 '{product_name}' 已从库存中删除。"
        
        # If the product is not found, print a message indicating so
        print(f"未找到产品 '{product_name}'。/ Product '{product_name}' not found.")
        return f"未找到产品 '{product_name}'"

    def get_sorted_products_by_name(self, sort_order='asc', number_of_items=None):
        """
        根据产品名称对库存项进行排序并返回。
        Fetches inventory items sorted by product name.

        Parameters:
        - sort_order (str): 确定排序顺序。可选项为 'asc' 或 'desc'。
                            Determines the sorting order. Options are 'asc' or 'desc'.
        - number_of_items (int): 要返回的项目数量。如果为 None，则返回所有项目。
                                 The number of items to return. If None, returns all items.

        Returns:
        - 按指定标准排序的库存项列表。
          A list of sorted inventory items according to the specified criteria.
        """
        if sort_order == 'asc':
            sorted_products = sorted(self._inventory_table, key=lambda item: item.get_product())
        elif sort_order == 'desc':
            sorted_products = sorted(self._inventory_table, key=lambda item: item.get_product(), reverse=True)
        else:
            print("指定的排序顺序无效。默认按产品名称升序排序。/ Invalid sort order specified. Defaulting to ascending order by product name.")
            sorted_products = sorted(self._inventory_table, key=lambda item: item.get_product())

        if number_of_items is not None:
            return sorted_products[:number_of_items]
        return sorted_products

    def get_sorted_inventory_by_stock(self, sort_order='all', number_of_items=None):
        """
        根据库存数量对库存项进行排序并返回。
        Fetches inventory items sorted by stock quantity.

        Parameters:
        - sort_order (str): 确定排序顺序。可选项为 'top', 'bottom', 或 'all'。
                            Determines the sorting order. Options are 'top', 'bottom', or 'all'.
        - number_of_items (int): 要返回的项目数量。如果为 None，则根据排序顺序返回所有项目。
                                 The number of items to return. If None, returns all items according to the sort order.

        Returns:
        - 按指定标准排序的库存项列表。
          A list of sorted inventory items according to the specified criteria.
        """
        # Sort inventory items by their in-stock quantity
        sorted_inventory = sorted(self._inventory_table, key=lambda item: int(item.get_in_stock()))

        if sort_order == 'top':
            return sorted_inventory[::-1][:number_of_items] if number_of_items else sorted_inventory[::-1]
        elif sort_order == 'bottom':
            return sorted_inventory[:number_of_items] if number_of_items else sorted_inventory
        elif sort_order == 'all':
            return sorted_inventory
        else:
            print("指定的排序顺序无效。按最少库存先返回所有项目。")
            return sorted_inventory
    
    def get_product_list(self):
        """
        返回库存中所有产品的名称列表。
        
        Returns:
        - A list of strings, where each string is a product name from the inventory.
        """
        product_list = [product.get_product() for product in self._inventory_table]
        return product_list
    
    def get_all(self):
        self.load_inventory_data()
        return self._inventory_table

if __name__ == "__main__":
    inventory_manager = Inventories()
    for item in inventory_manager.get_all():
        print(f"{item.get_product_chinese()}: {item.get_product()} | {item.get_in_stock_chinese()}: {item.get_in_stock()}")

    product_name = "ExampleProduct"  # Replace with the actual product name you're looking for
    product_data = inventory_manager.get_product_data(product_name)
    
    if isinstance(product_data, dict):
        # If a dictionary is returned, the product was found
        print("Product Data Found:")
        for key, value in product_data.items():
            print(f"{key}: {value}")
    else:
        # If a string is returned, it's the product not found message
        print(product_data)


    # List of 20 fruits
    fruits = [
        "Apple", "Banana", "Cherry", "Date", "Elderberry",
        "Fig", "Grape", "Honeydew", "Italian Plum", "Jackfruit",
        "Kiwi", "Lemon", "Mango", "Nectarine", "Orange",
        "Papaya", "Quince", "Raspberry", "Strawberry", "Tomato"
    ]
    
    for fruit in fruits:
        # Generate random values for inventory attributes
        opening_inventory = str(random.randint(10, 100))
        stock_in = str(random.randint(5, 50))
        stock_out = str(random.randint(0, 30))
        schedule_inventory = str(random.randint(5, 20))
        total_inventory = str(random.randint(10, 100))
        in_stock = str(random.randint(10, 100))
        
        # Create and add the new fruit to the inventory
        new_fruit = Inventory(fruit, opening_inventory, stock_in, stock_out,
                              schedule_inventory, total_inventory, in_stock)
        inventory_manager._inventory_table.append(new_fruit)
    
    # Save the updated inventory table to the CSV file
    inventory_manager.save_inventory_table()
    
    print(f"Added {len(fruits)} specific fruits to the inventory.")
    print("-"*50)
    print('\n')
    # Example: Fetch and print all products sorted by name in ascending order
    print("按产品名称升序排序的所有库存项 / All Inventory Items Sorted by Product Name in Ascending Order:")
    for item in inventory_manager.get_sorted_products_by_name('asc'):
        print(f"{item.get_product_chinese()}({item.get_product()}): {item.get_in_stock_chinese()}({item.get_in_stock()})")

    # Example: Fetch and print top 10 products sorted by name in descending order
    print("\n按产品名称降序排序的前10个库存项 / Top 10 Inventory Items Sorted by Product Name in Descending Order:")
    for item in inventory_manager.get_sorted_products_by_name('desc', 10):
        print(f"{item.get_product_chinese()}({item.get_product()}): {item.get_in_stock_chinese()}({item.get_in_stock()})")
    
    print("-"*50)
    print('\n')
    # 取最多库存的前N个项目 / Fetch and print top N items with the most stock
    N = 5  # 示例变量，项目数量 / Example variable for number of items
    print(f"库存最多的前 {N} 个项目 / Top {N} Items with Most Stock:")
    for item in inventory_manager.get_sorted_inventory_by_stock('top', N):
        print(f"{item.get_product_chinese()}({item.get_product()}): {item.get_in_stock_chinese()}({item.get_in_stock()}) in stock")

    # 取最少库存的前N个项目 / Fetch and print bottom N items with the least stock
    print(f"\n库存最少的前 {N} 个项目 / Bottom {N} Items with Least Stock:")
    for item in inventory_manager.get_sorted_inventory_by_stock('bottom', N):
        print(f"{item.get_product_chinese()}({item.get_product()}): {item.get_in_stock_chinese()}({item.get_in_stock()}) in stock")

    # 按库存数量排序返回所有项目 / Fetch and print all items, sorted by stock quantity
    print("\n按库存数量排序的所有项目 / All Items Sorted by Stock Quantity:")
    for item in inventory_manager.get_sorted_inventory_by_stock('all'):
        print(f"{item.get_product_chinese()}({item.get_product()}): {item.get_in_stock_chinese()}({item.get_in_stock()}) in stock")
    
    print("-"*50)
    print('\n')
    product_name_to_delete = "ExampleProduct"  # Replace with the actual product name you wish to delete
    inventory_manager.delete_product_by_name(product_name_to_delete)


