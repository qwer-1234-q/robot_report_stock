from datetime import datetime, time as datetime_time

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
                return False, (f"{shipping_date} - 提供的日期无效或格式不正确。")
    else:
        # If no shipping_date is provided, use the current date
        date_obj = datetime.now()
        return date_obj.strftime('%Y%m%d'), date_obj.strftime('%d/%m/%Y')

def get_time():
    # Use the current time if no time is provided
    time_obj = datetime.now()
    return time_obj.strftime('%H%M%S')

def is_number(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def handle_data(value):
    if value == '' or value == ' ' or value is None or len(str(value)) == 0:
        return 0
    return value  

