# -*- coding: utf-8 -*-
# Copyright (c) 2015, Caitlah Technology and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, json
from frappe.utils import cstr, flt, fmt_money, formatdate
from frappe import msgprint, _, scrub
from frappe.model.document import Document
from erpnext.controllers.accounts_controller import AccountsController
from erpnext.accounts.party import get_party_account

class ReceivedMoney(Document):

	def validate(self):
		if not self.title:
			self.title = self.get_title()
		if not self.withdraw_date:
			self.withdraw_date = self.posting_date
		if not self.received_transaction_status:
			self.received_transaction_status = 'Withdraw'
		self.validate_Denomination()
		self.validate_agent()
		if not self.mctn:
			self.mctn = self.title

	def validate_agent(self):
		if self.docstatus == 0:
			if self.received_agent == self.sender_user_id:
				msgprint(_("You are not Authorise to Withdraw this transaction").format(self.mctn),
					raise_exception=1)

	def validate_Denomination(self):
		teller = frappe.get_doc("Agents", self.receiver_agents)
		if teller.teller_function == "Teller & Till" and self.purpose != "Shopping":
			if self.amount_received != self.total_denomination:
				msgprint(_("Please make sure that your Amount Received = Total").format(self.total_denomination),
						raise_exception=1)

	def get_title(self):
		return self.mctn

	def on_submit(self):
		self.make_gl_entries()
		self.make_trxn_entries()
		self.update_tabSend_Received_Status()
		self.update_customer_info()


	def update_customer_info(self):
		frappe.db.sql("""Update `tabCustomer` set customer_details = %s, customer_id_type =%s, customer_id_no = %s where customer_name = %s""", (self.receiver_details, self.receiver_id_type, self.receiver_id_no, self.receiver_name))


	def make_gl_entries(self, cancel=0, adv_adj=0):
		from erpnext.accounts.general_ledger import make_gl_entries

		gl_map = []
		gl_map.append(
            frappe._dict({
				"posting_date": self.posting_date,
				"transaction_date": self.withdraw_date,
                "account": self.receiver_agents_account,
				"account_currency": self.received_currency,
				"credit": self.amount_received,
				"voucher_type": self.doctype,
				"voucher_no": self.name,
				"against": "Cash in Till - T&T",
				"remarks": "Withdraw Money Transaction"
            }))
		gl_map.append(
            frappe._dict({
                "account": "Cash in Till - T&T",
				"against": self.receiver_agents_account,
				"posting_date": self.posting_date,
				"transaction_date": self.withdraw_date,
				"debit": self.amount_received,
				"voucher_type": self.doctype,
				"voucher_no": self.name,
                "remarks": "Withdraw Money Transaction"
            }))

		if gl_map:
			make_gl_entries(gl_map, cancel=cancel, adv_adj=adv_adj)

	def make_trxn_entries(self):
		doc = frappe.new_doc("Transactions Details")
		doc.update({
					"user_id": self.received_agent,
					"posting_date": self.withdraw_date,
					"description": self.doctype,
					"currency": self.received_currency,
					"outflow": self.amount_received,
					"mctn": self.mctn
				})
		doc.insert()
		doc.submit()

	def update_tabSend_Received_Status(self):
		frappe.db.sql("""Update `tabSend Money` set withdraw_status="1" where name=%s""",self.mctn)

	def get_shopping_list(self):
		condition = ""
		product_table = frappe.db.sql("""select item_code, description, rate, qty, amount, parent
			from `tabMoney Transfer Product`
			where parent = %s {0}""".format(condition), (self.mctn), as_dict=1)

		entries = sorted(list(product_table),
			key=lambda k: k['parent'])

		self.set('product_table', [])
		self.total_denomination = 0.0

		for d in entries:
			row = self.append('product_table', {})
			row.update(d)
			self.total_denomination += flt(d.amount)
