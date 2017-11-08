#!/usr/bin/env python

class Source(object):
	# Source types
	BANK = 1
	BUDGET = 2
	IOU = 3
	types = (BANK, BUDGET, IOU)
	method_hints = ("amex", "cash", "bitcoin", "splitwise")
	def __init__(self, data, typ):
		self.data = data
		if typ not in Source.types:
			raise ValueError("type " + str(typ) + " is invalid")
		self.type = typ

	def by_date(self, date):
		return self.by_date[date]

	def by_keyword(self, keyword):
		return self.by_keyword[keyword.lower()]

	def by_amount(self, amount):
		return self.by_amount[amount]

	def iterate(self, startdate):
		for i, entry in enumerate(self.data):
			if entry.date() >= startdate:
				return self.data[i:]
		return []

class Entry(object):

	def date(self):
		raise NotImplementedError()

	def amount_owed(self):
		raise NotImplementedError()

	def amount_paid(self):
		raise NotImplementedError()

	def details(self):
		raise NotImplementedError()

	def keywords(self):
		k = filter(lambda k: k and k not in Source.method_hints,
			map(lambda k: k.lower(), self.details().split(" ")))
		print k
		return k

	def __repr__(self):
		return str(self.date()) + " : " + str(self.amount()) + " : " + str(self.details())