import csv 

class Customer:
    def __init__(self, customer, payable, payment, debt=None):
        self._customer = customer 
        self._customer_chinese = "客户姓名"
        self._payable = payable 
        self._payable_chinese = "应付金额"
        self._payment = payment 
        self._payment_chinese = "实付金额"
        self._debt = debt 
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
        with open(self.filepath, encoding='utf-8') as customer_file:
            reader = csv.DictReader(customer_file)
            i = 0
            for row in reader: 
                if i == 0:
                    i = 1
                    continue
                if row["Customer"] == '' or len(row['Customer']) == 0 or row["Customer"] is None: 
                    continue
                tmp_payable = row["Payable"] if row["Payable"] != '' or row["Payable"] == ' ' or row['Payable'] is None else '0.0'
                tmp_payment = row["Payment"] if row["Payment"] != '' or row["Payment"] == ' ' or row["Payment"] is None else '0.0'
                tmp_debt = row["Debt"] if row["Debt"] != '' or row["Debt"] == ' ' or row["Debt"] is None else '0.0'
                self._customer_payment_history.append(
                    Customer(row['Customer'], tmp_payable, tmp_payment, tmp_debt)
                )
    
    def save_customers(self):
        with open(self.filepath, 'w', encoding='utf-8', newline='') as customer_file:
            fieldnames = ['Customer', 'Payable', 'Payment', 'Debt']
            writer = csv.DictWriter(customer_file, fieldnames=fieldnames)
            writer.writeheader()
            if self._customer_payment_history[0].get_customer() != "客户姓名":
                writer.writerow({
                    'Customer': "客户姓名",
                    'Payable': "应付金额",
                    'Payment': "实付金额",
                    'Debt': "欠款金额"
                })
            for customer in self._customer_payment_history:
                writer.writerow(customer.to_dict())

    def add_customer(self, customer_name, payable, payment):
        try:
            payable_float = float(payable)
            payment_float = float(payment)
        except ValueError:
            return (f"Payment: {payment} or Payable {payable} is not a valid number. / 实付金额: {payment} 或 应付金额 {payable} 不是有效的数字")

        customer = Customer(customer_name, payable_float, payment_float, payable_float - payment_float)

        if customer.get_customer() != "客户姓名" and not self.customer_exists(customer.get_customer()):
            self._customer_payment_history.append(customer)
            self.save_customers()
            return (f"Customer '{customer.get_customer()}' saved in the payment history. / 客户 '{customer.get_customer()}' 已保存在客户付款历史记录中\n\n目前欠款金额为 {customer.get_debt()} / Current debt is {customer.get_debt()}") 
        else:
            return (f"Customer '{customer.get_customer()}' already exists in the payment history. / 客户 '{customer.get_customer()}' 已经存在于客户付款历史记录中。")

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
        for customer in self._customer_payment_history:
            if str(customer.get_debt()) == customer.get_debt_chinese() or customer.get_debt() == '':
                continue
            customer._debt = float(customer.get_payable()) - float(customer.get_payment())
            print(f"customer get debt {customer.get_debt()}")
            if float(customer.get_debt()) > 0:  # Assuming debt is stored as a string that can be converted to float
                customers_with_debt.append(customer)
                flag = True
        return flag, customers_with_debt
    
    def update_customer_payment(self, customer_name, payable, new_payment):
        # Validation for customer_name
        if not isinstance(customer_name, str) or not customer_name.strip():
            print("错误：客户名称无效。")
            return ("错误：客户名称无效。")

        # Validation for new_payment
        try:
            new_payment = float(new_payment)
        except ValueError:
            print("错误：支付金额无效。")
            return ("错误：支付金额无效。")
        
        for customer in self._customer_payment_history:
            if customer.get_customer() == customer_name:
                # Assuming 'new_payment' is the amount the customer has just paid,
                # and you want to update 'payment' and 'debt' accordingly.
                try:
                    # Convert existing data and new_payment to float for calculation
                    existing_payment = float(customer.get_payment())
                    existing_debt = float(customer.get_debt())
                    updated_payment = existing_payment + new_payment
                    updated_debt = existing_debt - new_payment

                    # Update the customer's payment and debt information
                    customer._payment = str(updated_payment)  # Assuming these attributes are stored as strings
                    # customer._debt = str(max(updated_debt, 0))  # Ensure debt doesn't go below 0
                    customer._debt = str(updated_debt)

                    # Save the updated customer list to the CSV
                    self.save_customers()
                    print(f"Payment information updated for customer '{customer_name}'.")
                    print(f"已为客户 '{customer_name}' 更新付款信息。")
                    return (f"Payment information updated for customer '{customer_name}'. / 已为客户 '{customer_name}' 更新付款信息。")
                except ValueError:
                    # Handle case where conversion to float fails
                    print("Error: Invalid payment or debt value. Update failed.")
                    print("错误：无效的付款或债务值。更新失败。")
                    return ("Error: Invalid payment or debt value. Update failed. / 错误：无效的付款或债务值。更新失败。")
        # Customer does not exist, add as new customer
        debt = max(payable - new_payment, 0)
        new_customer = Customer(customer_name, str(payable), str(new_payment), str(debt))
        self._customer_payment_history.append(new_customer)
        print(f"已添加新客户 '{customer_name}' / New customer '{customer_name}' added.")
        return (f"已添加新客户 '{customer_name}' / New customer '{customer_name}' added.")

    def get_customers_with_excess_payment(self):
        customers_with_excess_payment = []
        flag = False
        for customer in self._customer_payment_history:
            if str(customer.get_debt()) == customer.get_debt_chinese() or customer.get_debt() == '':
                continue
            customer._debt = float(customer.get_payable()) - float(customer.get_payment())
            print(f"customer get debt excess {customer.get_debt()}")
            if float(customer.get_debt()) < 0:
                customers_with_excess_payment.append(customer)
                flag = False
        
        return flag, customers_with_excess_payment

    def delete_customer(self, customer_name):
        # Find the customer in the list
        for i, customer in enumerate(self._customer_payment_history):
            if str(customer.get_customer()) == str(customer_name):
                # Remove the customer from the list
                del self._customer_payment_history[i]
                print(f"客户 '{customer_name}' 已被删除。 / Customer '{customer_name}' has been deleted.")
                # Optionally, save the updated customer list back to the CSV or database
                self.save_customers()
                return True, (f"客户 '{customer_name}' 已被删除。 / Customer '{customer_name}' has been deleted.")
        
        # Customer not found
        print(f"未找到客户 '{customer_name}'。 / Customer '{customer_name}' not found.")
        return False, (f"未找到客户 '{customer_name}'。 / Customer '{customer_name}' not found.")

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
    
    customer_manager.update_customer_payment("李四", 10, 0)
    customer_manager.update_customer_payment("张三", 0, 505)
    customer_manager.update_customer_payment("王八", 40, 0)
    
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
