import csv 
from helper import handle_data

def customer_title():
    return {
                'Customer': "客户姓名",
                'Payable': "应付金额",
                'Payment': "实付金额",
                'Debt': "欠款金额"
            }

class Customer:
    def __init__(self, customer, payable=0, payment=0, debt=None):
        self._customer = customer 
        self._customer_chinese = "客户姓名"
        self._payable = float(handle_data(payable))
        self._payable_chinese = "应付金额"
        self._payment = float(handle_data(payment)) 
        self._payment_chinese = "实付金额"
        if debt is not None:
            self._debt = float(debt)
        self._debt = self._payment - self._payable         
        self._debt_chinese = "欠款金额"
    
    def get_customer(self):
        return self._customer
    
    def get_customer_chinese(self):
        return self._customer_chinese 
    
    def get_payable(self):
        return self._payable
    
    def get_payable_chinese(self):
        return self._payable_chinese
    
    def get_payment(self):
        return self._payment 
    
    def get_payment_chinese(self):
        return self._payment_chinese
    
    def get_debt(self):
        return self._debt
    
    def get_debt_chinese(self):
        return self._debt_chinese
    
    def to_dict(self):
        return {
            'Customer': self.get_customer(),
            'Payable': self.get_payable(),
            'Payment': self.get_payment(),
            'Debt': self.get_debt()
        }

class Customers:
    def __init__(self):
        self._customer_payment_history = []
        self.filepath = "./data/customer_payment_history.csv"
    
    def load_customer(self):
        self._customer_payment_history.clear()
        self._customer_payment_history = []
        with open(self.filepath, encoding='utf-8') as customer_file:
            reader = csv.DictReader(customer_file)
            i = 0
            for row in reader: 
                if i == 0:
                    i = 1
                    continue
                if row["Customer"] == '' or len(row['Customer']) == 0 or row["Customer"] is None: 
                    continue
                tmp_payable = float(handle_data(row['Payable']))
                tmp_payment = float(handle_data(row["Payment"]))
                tmp_debt = float(handle_data(row["Debt"]))
                self._customer_payment_history.append(
                    Customer(row['Customer'], tmp_payable, tmp_payment, tmp_debt)
                )
    
    def save_customers(self):
        with open(self.filepath, 'w', encoding='utf-8', newline='') as customer_file:
            writer = csv.DictWriter(customer_file, fieldnames=customer_title().keys())
            writer.writeheader()
            if self._customer_payment_history[0].get_customer() != "客户姓名":
                writer.writerow(customer_title())
            for customer in self._customer_payment_history:
                writer.writerow(customer.to_dict())

    def clean_customers(self):
        with open(self.filepath, 'w', encoding='utf-8', newline='') as customer_file:
            writer = csv.DictWriter(customer_file, fieldnames=customer_title.keys())
            writer.writeheader()
            if len(self._customer_payment_history) == 0 or self._customer_payment_history[0].get_customer() != "客户姓名":
                writer.writerow(customer_title())
        self._customer_payment_history.clear()
        self._customer_payment_history = []

    def add_or_update_customer(self, customer_name, payable, payment):
        try:
            if payable is not None:
                payable = float(payable)
            else: 
                payable = 0
            if payment is not None:
                payment = float(payment)
            else: 
                payment = 0
        except ValueError:
            return "错误：'应付金额'或'实付金额'不是有效的数字。"
        
        # 查找现有客户并更新
        for customer in self._customer_payment_history:
            if str(customer.get_customer()) == str(customer_name):
                try:
                    # 更新支付和债务信息
                    existing_payable = float(customer.get_payable()) + payable
                    existing_payment = float(customer.get_payment()) + payment
                    debt = existing_payable - existing_payment
                    customer._payable = str(existing_payable)
                    customer._payment = str(existing_payment)
                    customer._debt = str(debt)

                    self.save_customers()  # 保存更新
                    return f"客户 '{customer_name}' 的信息已更新，当前债务为：{debt}。"
                except ValueError as e:
                    return f"更新失败：{str(e)}"

        # 如果未找到客户，则添加新客户
        debt = payable - payment
        new_customer = Customer(customer_name, str(payable), str(payment), str(debt))
        self._customer_payment_history.append(new_customer)
        self.save_customers()
        return f"已添加新客户 '{customer_name}'，当前债务为：{debt}。"

    def delete_customer(self, customer_name):
        # 在列表中查找客户
        for i, customer in enumerate(self._customer_payment_history):
            if str(customer.get_customer()) == str(customer_name):
                # 从列表中移除客户
                del self._customer_payment_history[i]
                print(f"客户 '{customer_name}' 已被删除。")
                # 将更新后的客户列表保存回CSV或数据库
                self.save_customers()
                return True, f"客户 '{customer_name}' 已被删除。"
        
        # 未找到客户
        print(f"未找到客户 '{customer_name}'。")
        return False, f"未找到客户 '{customer_name}'。"
    
    def customer_exists(self, customer_name):
        for customer in self._customer_payment_history:
            if str(customer.get_customer()) == str(customer_name):
                return True
        return False
    
    def get_customers_with_debt(self):
        """
        This method creates an empty list customers_with_debt, then iterates through each customer 
        in _customer_payment_history. It checks if the customer's debt (converted to a float for 
        comparison) is greater than zero. If so, the customer is added to the list. After all 
        customers have been checked, the list of customers with debt is returned.
        """
        customers_with_debt = []
        flag = False
        self.load_customer()
        for customer in self._customer_payment_history:
            if str(customer.get_debt()) == customer.get_debt_chinese() or customer.get_debt() == '':
                continue
            customer._debt = float(customer.get_payable()) - float(customer.get_payment())
            print(f"customer {customer.get_customer()} get debt excess {float(customer.get_payable())} - {float(customer.get_payment())}= {customer.get_debt()}")
            if float(customer.get_debt()) > 0:  # Assuming debt is stored as a string that can be converted to float
                customers_with_debt.append(customer)
                flag = True
        return flag, customers_with_debt

    def get_customers_with_excess_payment(self):
        customers_with_excess_payment = []
        flag = False
        self.load_customer()
        for customer in self._customer_payment_history:
            if str(customer.get_debt()) == customer.get_debt_chinese() or customer.get_debt() == '':
                continue
            customer._debt = float(customer.get_payable()) - float(customer.get_payment())
            print(f"customer {customer.get_customer()} get debt excess {float(customer.get_payable())} - {float(customer.get_payment())}= {customer.get_debt()}")
            if float(customer.get_debt()) < 0:
                customers_with_excess_payment.append(customer)
                flag = True
        
        return flag, customers_with_excess_payment

    def get_customer_name_list(self):
        """
        Returns a list of all unique customer names from the payment history.
        """
        name_list = set()
        self.load_customer()
        print("let search customer names")
        for customer in self._customer_payment_history:
            print(f"{customer.get_customer()}")
            if customer.get_customer() not in name_list:
                name_list.add(customer.get_customer())
        print(name_list)
        return list(name_list)

    def get_all(self):
        self.load_customer()
        return self._customer_payment_history
    
if __name__ == "__main__":
    print("TESTING: test the customer files----------------------------------------------------------------------------------")
    customer_manager = Customers()
    for item in customer_manager.get_all():
        print(f"{item.get_customer_chinese()}: {item.get_customer()} | {item.get_payable_chinese()}: {item.get_payable()} AUD | {item.get_payment_chinese()} : {item.get_payment()} AUD | {item.get_debt_chinese()}: {item.get_debt()} AUD")
    
    # new_customer = Customer("New Customer Name", "1000", "800", "200")
    # customer_manager.add_customer(new_customer)
    # new_customer = Customer("李四", "10.0", "0.0", "10.0")
    # customer_manager.add_customer(new_customer)
    # new_customer = Customer("张三", "100", "100", "0")
    # customer_manager.add_customer(new_customer)
    
    for item in customer_manager.get_all():
        print(f"{item.get_customer_chinese()}: {item.get_customer()} | {item.get_payable_chinese()}: {item.get_payable()} AUD | {item.get_payment_chinese()} : {item.get_payment()} AUD | {item.get_debt_chinese()}: {item.get_debt()} AUD")
    
    search_name = "Customer Name"

    if customer_manager.customer_exists(search_name):
        print(f"Customer '{search_name}' exists in the payment history.")
    else:
        print(f"Customer '{search_name}' does not exist in the payment history.")
    
    flag, debt_customers = customer_manager.get_customers_with_debt()

    print("--欠款的顾客")
    for customer in debt_customers:
        print(f"{customer.get_customer_chinese()}: {customer.get_customer()} | "
              f"{customer.get_payable_chinese()}: {customer.get_payable()} AUD | "
              f"{customer.get_payment_chinese()}: {customer.get_payment()} AUD | "
              f"{customer.get_debt_chinese()}: {customer.get_debt()} AUD")
    
    customer_manager.add_or_update_customer("李四", 10, 0)
    customer_manager.add_or_update_customer("张三", 0, 505)
    customer_manager.add_or_update_customer("王八", 40, 0)
    
    print("--客户支付的金额大于付款金额：")
    _, excess_payment_customers = customer_manager.get_customers_with_excess_payment()

    for customer in excess_payment_customers:
        print(f"{customer.get_customer_chinese()}: {customer.get_customer()} | "
              f"{customer.get_payable_chinese()}: {customer.get_payable()} | "
              f"{customer.get_payment_chinese()}: {customer.get_payment()} | "
              f"{customer.get_debt_chinese()}: {customer.get_debt()}")
    
    customer_name_to_delete = "John Doe"  # Example customer name
    customer_manager.delete_customer(customer_name_to_delete)
    # customer_manager.delete_customer("张三")
    print(customer_manager.get_customer_name_list())