# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import rounded


class Plan(Document):
	def validate(self):
		if not self.period:
			frappe.throw("Period must be greater than 0")

	def get_price_per_day(self, currency):
		price = self.price_inr if currency == "INR" else self.price_usd
		price_per_day = rounded(price / self.period, 2)
		return price_per_day

	def get_price_for_interval(self, interval, currency):
		price_per_day = self.get_price_per_day(currency)

		if interval == "Daily":
			return price_per_day

		if interval == "Monthly":
			return rounded(price_per_day * 30)


def get_plan_config(name):
	cpu_time = frappe.db.get_value("Plan", name, "cpu_time_per_day")
	return {"rate_limit": {"limit": cpu_time * 3600, "window": 86400}}
