import frappe
from frappe.utils import getdate

def get_message_type(segment):
    unh_data = get_index(segment, 1)
    return get_index(unh_data, 0)

def get_index(source, index):
    try:
        return source[index]
    except Exception as e:
        raise e

def parse_date(date, format):
    try:
        if format == "102":
            return getdate(date)
        frappe.throw("Invalid Date")
    except Exception as e:
        frappe.throw(e)

