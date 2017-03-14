frappe.listview_settings['Received Money'] = {
	add_fields: ["title", "docstatus","posting_date","purpose"],
	get_indicator: function(doc) {
        if(doc.docstatus==0){
        	return [__("Pending"), "orange", "docstatus,=,0"]
		}else if(doc.docstatus==1){
        	return [__("Withdraw"), "green", "docstatus,=,1"]
		}
	}
}