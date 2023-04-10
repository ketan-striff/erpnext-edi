from pydifact.segmentcollection import Interchange
from erpnext_edi.erpnext_edi.lib.edi import get_message_type, parse_date
import json

def process_edi_log():
    log_list = frappe.db.get_list(
        "EDI Log",
        filters={"status": "Pending"},
        fields=["content", "name"],
    )
    for edi_entry in log_list:
        # print(edi_entry)
        interchange = Interchange.from_str(edi_entry.content)
        # header_segments = interchange.get_header_segment()
        # print(header_segments)
        # print(interchange)
        # break

        message_type = get_message_type(interchange.get_segment("UNH"))

        if message_type == "ORDERS":
            process_po(interchange)
            # print("PO")

        # break

        # for message in interchange.get_messages():
        #     for segment in message.segments:
        #         print(
        #             "Segment tag: {}, content: {}".format(segment.tag, segment.elements)
        #         )


def process_po(interchange):
    items = []
    po_dict = {
        "naming_series": "SAL-ORD-.YYYY.-",
        "customer": "Appario Retail Private Limited",
        "customer_name": "Appario Retail Private Limited",
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
    for message in interchange.get_messages():
        for segment in message.segments:
            ele = segment.elements
            if segment.tag == "BGM":
                if int(ele[0]) == 220:  # means order or po number
                    po_dict["po_no"] = ele[1]
                else:
                    frappe.throw("invalid bgm " + ele[0])
            elif segment.tag == "DTM":
                ele = ele[0]
                if (
                    int(ele[0]) == 137
                ):  # means date and time when document is issues should be PO date
                    # print(ele, ele[1], ele[2])
                    date = parse_date(ele[1], ele[2])
                    po_dict["po_date"] = f"{date.year}-{date.month}-{date.day}"
                if (
                    int(ele[0]) == 63
                ):  # means date and time of delivery after goods can not be delivered
                    date = parse_date(ele[1], ele[2])
                    po_dict["delivery_date"] = f"{date.year}-{date.month}-{date.day}"
            elif segment.tag == "LIN":  # new line item starts
                current_line_item_index = int(ele[0]) - 1
                # print(current_line_item_index, "index")
                items.append(get_default_line_item())
                current_line_item = items[current_line_item_index]
            elif segment.tag == "PIA":  # product information
                if int(ele[0]) == 5:  # product itentification
                    item = ele[1][0]
                    print(item)
                    if not item:
                        frappe.throw("Item Code not found: " + item)
                    item_code = frappe.db.get_value(
                        "Item", {"item_code": item}, "item_code"
                    )
                    if not item_code:
                        item_code = frappe.db.get_value(
                            "Item", {"alias_1": item}, "item_code"
                        )
                    if not item_code:
                        frappe.throw("Item Code not found: " + item)
                    current_line_item["item_code"] = item_code
                    # current_line_item["item_name"] = item_code
            elif segment.tag == "QTY":  # line item qty
                ele = ele[0]
                if int(ele[0]) == 21:  # ordered qty
                    current_line_item["qty"] = int(ele[1])
            elif segment.tag == "PRI":  # line item price
                ele = ele[0]
                if ele[0] == "AAA":  # price
                    current_line_item["rate"] = float(ele[1])
            # print("Segment tag: {}, content: {}".format(segment.tag, segment.elements))
        po_dict["items"] = items
        # total_qty = 0
        # base_total = 0
        # for item in items:
        #     qty = item.get('qty')
        #     rate = item.get('rate')
        #     total = qty * rate
        #     total_qty = total_qty + qty
        #     base_total = base_total + total

        # po_dict.set("total_qty", total_qty)
        # po_dict.set("base_total", base_total)
        # po_dict.set("base_net_total", base_total)
        # po_dict.set("total", base_total)
        # po_dict.set("net_total", base_total)
        # po_dict.set("base_grand_total", base_total)
        # po_dict.set("base_rounded_total", base_total)
        # po_dict.set("grand_total", base_total)
        # po_dict.set("rounded_total", base_total)

        # print(json.dumps(po_dict))
        sales_order = frappe.get_doc(po_dict)
        sales_order.save()
        print(sales_order.as_json())
        frappe.db.commit()


def get_default_line_item():
    return {
        "doctype": "Sales Order Item",
    }
