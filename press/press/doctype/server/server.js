// Copyright (c) 2019, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on('Server', {
	refresh: function(frm) {
		frm.add_custom_button(__('Ping'), () => {
			frm.call({method: "ping", doc: frm.doc, callback: result => frappe.msgprint(result.message)});
		});
	}
});
