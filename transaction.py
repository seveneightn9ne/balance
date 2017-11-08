#!/usr/bin/env python
from source import Source

class Transaction(object):
	def __init__(self):
		self.bank = self.budget = self.iou = None

	def add(self, entry):
		if entry.type == Source.BANK:
			self.bank = entry
		elif entry.type == Source.BUDGET:
			self.budget = entry
		elif entry.type == Source.IOU:
			self.iou = entry
		else:
			raise ValueError("entry type " + str(entry.type) + " is unrecognized")
		return self

	def charge(self):
		if self.bank:
			return self.bank.amount()
		if self.iou and self.iou.amount_paid():
			return self.iou.amount_paid()
		return None

	def amount(self):
		if self.budget:
			return self.budget.amount()
		if self.iou and self.iou.amount_owed():
			return self.iou.amount_owed()
		if self.bank:
			return self.bank.amount()
		return None

	def date(self):
		if self.bank:
			return self.bank.date()
		elif self.budget:
			return self.budget.date()
		elif self.iou:
			return self.iou.date()
		return None

	def guess_budget_amount(self):
		if self.budget:
			raise ValueError("No need to guess budget amount when budget is set")
		if self.iou:
			return self.iou.amount_owed()
		if self.bank:
			return self.bank.amount()
		return None

	def method(self):
		if self.budget and budget.method_hint:
			return budget.method_hint
		if self.bank:
			return "amex"
		if self.iou and self.iou.amount_paid() == 0:
			return "splitwise"
		return None

	def only(self):
		if self.bank and not self.budget and not self.iou:
			return self.bank
		if not self.bank and self.budget and not self.iou:
			return self.budget
		if not self.bank and not self.budget and self.iou:
			return self.iou

	def __str__(self):
		if self.only():
			return "T(%s, %s)" % (str(self.date()), str(self.only()))
		return "T(%s, %s, %s, %s)" % (str(self.date()), str(self.bank), str(self.iou), str(self.budget))

	def resolved(self):
		return not self.needs_budget()
		# if not self.budget:
		# 	return False
		# if self.splitwise and self.splitwise.amount_owed() == self.budget.amount():
		# 	return True
		# if self.bank and self.bank.amount() == self.budget.amount():
		# 	return True
		# return False

	def needs_budget(self):
		return self.budget == None

	def keywords(self):
		kk = []
		if self.bank:
			kk.extend(self.bank.keywords())
		if self.budget:
			kk.extend(self.budget.keywords())
		if self.iou:
			kk.extend(self.iou.keywords())
		print kk
		return kk