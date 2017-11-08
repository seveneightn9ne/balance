#!/usr/bin/env python

from source import Source, Entry
from collections import defaultdict
import datetime

class Amex(Source):

	def filter(self, entry):
		if self.user and entry.data[3] != self.user:
			return False
		return entry.amount() > 0

	def __init__(self, user, data):
		self.user = user or None
		data = filter(self.filter, [AmexEntry(d) for d in data])
		self.by_date = defaultdict(list)
		self.by_keyword = defaultdict(list)
		self.by_amount = defaultdict(list)
		for entry in data:
			d = entry.data
			self.by_date[entry.date()].append(entry)
			self.by_amount[entry.amount()].append(entry)
			keywords = map(lambda k: k.lower(), entry.details().split(" "))
			for k in keywords:
				if k and k not in ("and", "the"):
					self.by_keyword[k].append(entry)
		super(Amex, self).__init__(data, Source.BANK)

class AmexEntry(Entry):
	def __init__(self, data):
		assert len(data) == 16
		self.data = data
		self.type = Source.BANK

	def amount(self):
		return self.amount_paid()

	def amount_paid(self):
		return float(self.data[7])

	def date(self):
		datestr = self.data[0].split(" ")[0] # TODO format
		return datetime.datetime.strptime(datestr, "%m/%d/%Y").date()

	def details(self):
		return self.data[2]

	def __str__(self):
		return "A(\"%s\", %s)" % (self.details(), str(self.amount()))