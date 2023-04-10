// Copyright (c) 2023, ketan and contributors
// For license information, please see license.txt

frappe.ui.form.on('EDI Connection', {
  refresh: function(frm) {
    frm.add_custom_button(__('Get Vendor Central POs'), function() {
      console.log(arguments, frm.doc);
      frappe.call('erpnext_edi.erpnext_edi.doctype.edi_connection.api.get_edi_purchase_orders', {
        connection: frm.doc.name
      }).then(r => {
        console.log(r.message)
      })
      frappe.msgprint(frm.doc.email);
    });
  }
});
