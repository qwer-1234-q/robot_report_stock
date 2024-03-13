import csv 
import random

def is_number(value):
    try:
        float(value)
        return True
    except ValueError:
        return False
    
class Inventory:
    def __init__(self, product, opening_inventory, stock_in, 
                 stock_out, schedule_inventory, total_inventory, 
                 in_stock):
        self._product = product 
        self._product_chinese = "产品名称"
        self._opening_inventory = opening_inventory
        self._opening_inventory_chinese = "初始库存数量"
        self._stock_in = stock_in
        self._stock_in_chinese = "入库总数量"
        self._stock_out = stock_out 
        self._stock_out_chinese = "出库总数量"
        self._schedule_inventory = schedule_inventory
        self._schedule_inventory_chinese = "预定总数量"
        self._total_inventory = total_inventory
        if self._total_inventory is None or self._total_inventory == '0' or self._total_inventory == 0:
            self._total_inventory = str(int(self._opening_inventory) - int(self._stock_out) + int(self._stock_in))
        self._total_inventory_chinese = "库存总数量"
        self._in_stock = in_stock 
        if self._in_stock is None or self._in_stock == '0' or self._in_stock == 0:
            self._in_stock = str(int(self._total_inventory) - int(self._schedule_inventory))
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
                tmp_opening_inventory = row["Opening inventory"] if row["Opening inventory"] != '' or row["Opening inventory"] == ' ' or row["Opening inventory"] is None else '0'
                tmp_stock_in = row["Stock In"] if row["Stock In"] != '' or row["Stock In"] == ' ' or row["Stock In"] is None else '0'
                tmp_stock_out = row["Stock out"] if row["Stock out"] != '' or row["Stock out"] == ' ' or row["Stock out"] is None else '0'
                tmp_schedule_inventory = row["Schedule inventory"] if row["Schedule inventory"] != '' or row["Schedule inventory"] == ' ' or row["Schedule inventory"] is None else '0'
                tmp_total_inventory = row["Total inventory quantity"] if row["Total inventory quantity"] != '' or row["Total inventory quantity"] == ' ' or row["Total inventory quantity"] is None else '0'
                tmp_in_stock = row["In stock"] if row["In stock"] != '' or row["In stock"] == ' ' or row["In stock"] is None else '0'
                self._inventory_table.append(
                    Inventory(row['Product'], tmp_opening_inventory, tmp_stock_in, 
                            tmp_stock_out, tmp_schedule_inventory, tmp_total_inventory, tmp_in_stock)
                )

    def save_inventory_table(self):
        self.merge_duplicate_products()
        self._inventory_table = self.get_sorted_inventory_by_stock('all')
        with open("./data/inventory_table.csv", 'w', encoding='utf-8', newline='') as inventory_file:
            fieldnames = ['Product', 'Opening inventory', 'Stock In', 'Stock out', 
                        'Schedule inventory', 'Total inventory quantity', 'In stock']
            writer = csv.DictWriter(inventory_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({
                    'Product': "产品名称",
                    'Opening inventory': "初始库存数量",
                    'Stock In': "入库总数量",
                    'Stock out': "出库总数量",
                    'Schedule inventory': "预定总数量",
                    'Total inventory quantity': "库存总数量",
                    'In stock': "可用库存"
                })
            for item in self._inventory_table:
                writer.writerow({
                    'Product': item.get_product(),
                    'Opening inventory': item.get_opening_inventory(),
                    'Stock In': item.get_stock_in(),
                    'Stock out': item.get_stock_out(),
                    'Schedule inventory': item.get_schedule_inventory(),
                    'Total inventory quantity': item.get_total_inventory(),
                    'In stock': item.get_in_stock()
                })

    def merge_duplicate_products(self):
        """
        检查库存中的重复产品名称，并合并数据。
        Checks for duplicate product names in the inventory and merges their data.
        """
        merged_inventory = []
        seen_products = {}

        for item in self._inventory_table:
            product_name = item.get_product()
            if product_name not in seen_products:
                # If it's the first time seeing this product, add it directly to the merged list
                seen_products[product_name] = item
            else:
                # If it's a duplicate, merge data
                existing_item = seen_products[product_name]
                existing_item._stock_in = str(int(existing_item.get_stock_in()) + int(item.get_stock_in()))
                existing_item._stock_out = str(int(existing_item.get_stock_out()) + int(item.get_stock_out()))
                existing_item._opening_inventory = str(int(existing_item.get_opening_inventory()) + int(item.get_opening_inventory()))
                existing_item._schedule_inventory = str(int(existing_item.get_schedule_inventory()) + int(item.get_schedule_inventory()))
                # Update total inventory and in stock based on the merged data
                existing_item._total_inventory = str(int(existing_item.get_total_inventory()) + int(item.get_total_inventory()))
                existing_item._in_stock = str(int(existing_item.get_in_stock()) + int(item.get_in_stock()))

        # Rebuild the inventory with merged items
        self._inventory_table = list(seen_products.values())

        print("重复的产品已合并。/ Duplicate products have been merged.")

    def get_product_data(self, product_name):
        self.load_inventory_data()
        for product in self._inventory_table:
            if str(product.get_product()) == str(product_name):
                # Product found, return its data
                data = {
                    'Product': product.get_product(),
                    'Opening Inventory': product.get_opening_inventory(),
                    'Stock In': product.get_stock_in(),
                    'Stock Out': product.get_stock_out(),
                    'Scheduled Inventory': product.get_schedule_inventory(),
                    'Total Inventory': product.get_total_inventory(),
                    'In Stock': product.get_in_stock(),
                }
                return data
        # Product not found, return a message indicating so
        return f"产品 '{product_name}' 未找到 / Product '{product_name}' not found."

    def add_or_update_product(self, product, opening_inventory=None, stock_in=None, 
                          stock_out=None, schedule_inventory=None, 
                          total_inventory=None, in_stock=None):
        # Validate each input to ensure it's either None or a valid number
        inputs = [opening_inventory, stock_in, stock_out, schedule_inventory, total_inventory, in_stock]
        if any(input is not None and not is_number(input) for input in inputs):
            print("错误: 所有库存数量必须是有效的数字。 / Error: All inventory quantities must be valid numbers.")
            return ("错误: 所有库存数量必须是有效的数字。 / Error: All inventory quantities must be valid numbers.")
        
        # Find the product in the inventory table
        # existing_product = None
        for item in self._inventory_table:
            if str(item.get_product()) == str(product):
                existing_product = item
                if opening_inventory is not None:
                    existing_product._opening_inventory = opening_inventory
                if stock_in is not None:
                    existing_product._stock_in = stock_in
                if stock_out is not None:
                    existing_product._stock_out = stock_out
                if schedule_inventory is not None:
                    existing_product._schedule_inventory = schedule_inventory
                if total_inventory is not None:
                    existing_product._total_inventory = total_inventory
                else:
                    existing_product._total_inventory = str(int(existing_product._opening_inventory) + int(existing_product.stock_in) - int(existing_product.stock_out)) 
                if in_stock is not None:
                    existing_product._in_stock = in_stock
                else: 
                    existing_product._in_stock = str(int(existing_product.get_total_inventory()) - int(existing_product._schedule_inventory))
                self.save_inventory_table()
                print(f"Updated product '{product}'.")
                return f"Updated product '{product}'."

        if opening_inventory is None:
            opening_inventory = 0
        if stock_in is None:
            stock_in = 0
        if stock_out is None:
            stock_out = 0
        if schedule_inventory is None:
            schedule_inventory = 0
        if total_inventory is None:
            total_inventory = opening_inventory + stock_in - stock_out 
        if in_stock is None:
            in_stock = total_inventory - schedule_inventory      
        new_product = Inventory(product=str(product), opening_inventory=str(opening_inventory), 
                                stock_in=str(stock_in), stock_out=str(stock_out), 
                                schedule_inventory=str(schedule_inventory), 
                                total_inventory=str(total_inventory), in_stock=str(in_stock))
        self._inventory_table.append(new_product)
        print(f"Added new product '{product}'.")

        # Optionally, save the updated inventory table back to the CSV file
        self.save_inventory_table()
        return (f"Added new product '{product}'.")

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
                return f"产品 '{product_name}' 已从库存中删除。/ Product '{product_name}' has been deleted from inventory."
        
        # If the product is not found, print a message indicating so
        print(f"未找到产品 '{product_name}'。/ Product '{product_name}' not found.")
        return f"未找到产品 '{product_name}'。/ Product '{product_name}' not found."

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
            print("指定的排序顺序无效。按最少库存先返回所有项目。/ Invalid sort order specified. Returning all items sorted by least stock first.")
            return sorted_inventory
    
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


