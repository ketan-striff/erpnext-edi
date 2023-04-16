import frappe
from pydifact.segmentcollection import Message, Interchange
from pydifact.segments import Segment
from erpnext_edi.erpnext_edi.lib.edi import get_message_type, parse_date
import json
import paramiko
import io


def exec():
    frappe.enqueue(process_edi_log, queue="long")
    pass


def process_edi_log():
    log_list = frappe.db.get_list(
        "EDI Log",
        filters={"status": "Pending"},
        fields=["content", "name", "customer", "edi_connection"],
    )
    for edi_message in log_list:
        interchange = Interchange.from_str(edi_message.content)
        message_type = get_message_type(interchange.get_segment("UNH"))

        if message_type == "ORDERS":
            process_po(interchange, edi_message)


def process_po(interchange, edi_message):
    edi_connection_doc = frappe.get_doc("EDI Connection", edi_message.edi_connection)
    customer = frappe.get_doc("Customer", edi_message.customer)
    items = []
    po_dict = {
        "naming_series": "SAL-ORD-.YYYY.-",
        "customer": edi_message.customer,
        "customer_name": edi_message.customer,
        "selling_price_list": customer.default_price_list,
        "order_type": "Sales",
        "doctype": "Sales Order",
        "items": [],
    }
    # Segment tag: UNH, content: ['1', ['ORDERS', 'D', '96A', 'UN', 'EAN008']]
    # Segment tag: BGM, content: ['220', '6PR8BO7G', '9']
    # Segment tag: DTM, content: [['137', '20230404', '102']]
    # Segment tag: DTM, content: [['63', '20230518', '102']]
    # Segment tag: DTM, content: [['64', '20230417', '102']]
    # Segment tag: RFF, content: [['CR', 'SNURW']]
    # Segment tag: NAD, content: ['BY', ['8900000004195', '', '9']]
    # Segment tag: NAD, content: ['SU', ['8900000004195', '', '9']]
    # Segment tag: NAD, content: ['DP', ['8900000006809', '', '9'], '', '', '', '', '', '', 'IN']
    # Segment tag: NAD, content: ['WH', 'CCU1']
    # Segment tag: NAD, content: ['IV', ['8900000004195', '', '9'], '', [' Appario Retail Pvt Ltd', 'India'], ' 1st Floor, UB Plaza, Vittal Mallya', 'BANGALORE', '', '560001', 'IN']
    # Segment tag: RFF, content: [['VA', '29AALCA0171E1ZV']]
    # Segment tag: CUX, content: [['2', 'INR', '9']]
    # Segment tag: LIN, content: ['1']
    # Segment tag: PIA, content: ['5', ['B0B5X89RGP', 'BP']]
    # Segment tag: QTY, content: [['21', '106']]
    # Segment tag: PRI, content: [['AAA', '135']]
    # Segment tag: LIN, content: ['2']
    # Segment tag: PIA, content: ['5', ['B0B5X89RGP', 'BP']]
    # Segment tag: QTY, content: [['21', '100']]
    # Segment tag: PRI, content: [['AAA', '140']]
    # Segment tag: UNS, content: ['S']
    # Segment tag: CNT, content: [['2', '1']]
    # Segment tag: UNT, content: ['20', '1']

    current_line_item_index = 0
    current_line_item = {}
    is_po_ref_added = False
    is_nad_added = False
    for message in interchange.get_messages():
        outgoing = Interchange(
            [edi_connection_doc.edi_supplier_id, "14"],
            [edi_connection_doc.edi_customer_id, "14"],
            "14",
            ["UNOA", "3"],
        )
        unh_message = Message("1", ["ORDRSP", "D", "96A", "UN", "EAN008"])
        po_no = None
        for segment in message.segments:
            ele = segment.elements
            if segment.tag == "BGM":
                if int(ele[0]) == 220:  # means order or po number
                    po_dict["po_no"] = ele[1]
                    po_no = ele[1]
                    unh_message.add_segment(Segment("BGM", "231", [po_no, "4"]))
                else:
                    frappe.log_error(
                        "Invalid BGM",
                        frappe.get_traceback(),
                    )
                    return False
                    # frappe.throw("invalid bgm " + ele[0])
            elif segment.tag == "RFF":
                # RFF+ON:TZGTMRBN'
                # RFF+CR:SNURW'
                if not is_po_ref_added:
                    is_po_ref_added = True
                    unh_message.add_segment(Segment("RFF", ["ON", po_no]))
                unh_message.add_segment(Segment(segment.tag, *ele))
            elif segment.tag == "CUX" or segment.tag == "UNS":
                unh_message.add_segment(Segment(segment.tag, *ele))
            elif segment.tag == "DTM":
                ele = ele[0]
                if (
                    int(ele[0]) == 137
                ):  # means date and time when document is issues should be PO date
                    # print(ele, ele[1], ele[2])
                    date = parse_date(ele[1], ele[2])
                    unh_message.add_segment(Segment("DTM", ["137", ele[1], ele[2]]))
                    unh_message.add_segment(Segment("DTM", ["171", ele[1], ele[2]]))
                    po_dict["po_date"] = f"{date.year}-{date.month}-{date.day}"
                if (
                    int(ele[0]) == 63
                ):  # means date and time of delivery after goods can not be delivered
                    date = parse_date(ele[1], ele[2])
                    po_dict["delivery_date"] = f"{date.year}-{date.month}-{date.day}"
            elif segment.tag == "NAD":
                if not is_nad_added:
                    is_nad_added = True
                    # unh_message.add_segment(Segment(segment.tag, *ele))
                if ele[0] == "WH":
                    try:
                        address = frappe.get_doc("Address", {"address_code": ele[1]})
                        po_dict["customer_address"] = address.name
                        po_dict["shipping_address_name"] = address.name
                    except:
                        pass
            elif segment.tag == "LIN":  # new line item starts
                unh_message.add_segment(Segment(segment.tag, ele))
                current_line_item_index = int(ele[0]) - 1
                # print(current_line_item_index, "index")
                items.append(get_default_line_item())
                current_line_item = items[current_line_item_index]
            elif segment.tag == "PIA":  # product information
                # PIA+5+B09VZBGL1N:BP'
                unh_message.add_segment(Segment(segment.tag, *ele))
                if int(ele[0]) == 5:  # product itentification
                    item = ele[1][0]
                    print(item)
                    if not item:
                        frappe.log_error(
                            "Could not get Item from EDI message",
                            frappe.get_traceback(),
                        )
                        return False
                        # frappe.throw("Item Code not found: " + item)
                    # item_code = frappe.db.get_value(
                    #     "Item", {"item_code": item}, "item_code"
                    # )
                    item_code = None
                    if not item_code:
                        item_code = frappe.get_all(
                            "Item",
                            or_filters={
                                "item_code": item,
                                "alias_1": item,
                                "alias_2": item,
                                "alias_3": item,
                                "alias_4": item,
                                "alias_5": item,
                                "alias_6": item,
                                "alias_7": item,
                                "alias_8": item,
                                "alias_9": item,
                                "alias_10": item,
                            },
                            limit=1,
                        )
                        if len(item_code) > 0:
                            item_code = item_code[0].name
                    if not item_code:
                        frappe.log_error(
                            "Could not get Item from EDI message: " + item,
                            frappe.get_traceback(),
                        )
                        return False
                        # frappe.throw("Item Code not found: " + item)
                    current_line_item["item_code"] = item_code
                    # current_line_item["item_name"] = item_code
            elif segment.tag == "QTY":  # line item qty
                ele = ele[0]
                if int(ele[0]) == 21:  # ordered qty
                    unh_message.add_segment(Segment(segment.tag, ["12", ele[1]]))
                    current_line_item["qty"] = int(ele[1])
            elif segment.tag == "PRI":  # line item price
                unh_message.add_segment(Segment(segment.tag, *ele))
                ele = ele[0]
                if ele[0] == "AAA":  # price
                    current_line_item["rate"] = float(ele[1])
        po_dict["items"] = items

        outgoing.add_message(unh_message)

        acknoledge_edi = outgoing.serialize(True)
        print(acknoledge_edi)

        # print(json.dumps(po_dict))
        sales_order = frappe.get_doc(po_dict)
        sales_order.save()
        print(sales_order.as_json())
        edi_log_doc = frappe.get_doc("EDI Log", edi_message.name)
        edi_log_doc.type = "PO"
        edi_log_doc.status = "Done"
        edi_log_doc.acknoledgement_edi = acknoledge_edi
        edi_log_doc.save()
        frappe.db.commit()

        str_key = io.StringIO(edi_connection_doc.outgoing_private_key)
        mykey = paramiko.RSAKey.from_private_key(str_key)
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.load_system_host_keys()
        ssh_client.connect(
            hostname=edi_connection_doc.outgoing_host,
            username=edi_connection_doc.outgoing_username,
            allow_agent=True,
            pkey=mykey,
        )
        ftp_client = ssh_client.open_sftp()
        file = ftp_client.file("/upload/855-" + edi_message.name, "a", -1)
        print(file)
        file.write(acknoledge_edi)
        file.flush()
        ftp_client.close()
        ssh_client.close()


def get_default_line_item():
    return {
        "doctype": "Sales Order Item",
    }
