// Copyright (c) 2016, Caitlah Technology and contributors
// For license information, please see license.txt

frappe.ui.form.on('Transfer from Vault', {
	refresh: function(frm) {

	},
	
	onload: function(frm) {
	if (frm.doc.docstatus != 1){
	  var today = get_today()
	  frm.set_value("transfer_date", today);
	  
	  frm.set_query("transfer_from_vault", function() {
			return {
				"filters": { "docstatus": ["=", 1],
							 "teller_function": "Vault"}
			};
		});
	  
	  var Current_User = user;
	  if (Current_User != "Administrator"){
		  cur_frm.set_value("transfer_from_vault", "");
					frappe.call({
							"method": "frappe.client.get",
							args: {
								doctype: "Agents",
								filters: {'agent_user': Current_User},
								name: frm.doc.sender_from
							},
							callback: function (data) {
								cur_frm.set_value("transfer_from_vault", data.message["name"]);
					}
				});
//			frappe.call({
//							"method": "frappe.client.get",
//							args: {
//								doctype: "Account",
//								filters: {'account_name': " Cash in Vault - T&T"},
								
//							},
//							callback: function (data) {
//								total_debit = sum((data.message["debit"]));
//								total_credit = sum((data.message["credit"]));
//								cur_frm.set_value("vault_balance", flt(total_credit - total_debit));
//					}
//					});
	  }
	 } 
	}
});