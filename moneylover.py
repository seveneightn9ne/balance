#!/usr/bin/env python
import datetime
from collections import defaultdict
from source import Source, Entry
from pprint import pprint

class MoneyLover(Source):
	def __init__(self, data):
		data.next() # skip the header row
		data = [MoneyLoverEntry(d) for d in data if d[7] == "No" and float(d[2]) < 0]
		self.by_date = defaultdict(list)
		self.by_keyword = defaultdict(list)
		self.by_amount = defaultdict(list)
		for entry in data:
			d = entry.data
			self.by_date[entry.date()].append(entry)
			self.by_amount[entry.amount_owed()].append(entry)
			keywords = map(lambda k: k.lower(), entry.details().split(" "))
			for k in keywords:
				if k and k not in Source.method_hints and k not in ("and", "the"):
					self.by_keyword[k].append(entry)
			
		super(MoneyLover, self).__init__(data, Source.BUDGET)

class MoneyLoverEntry(Entry):
	def __init__(self, data):
		assert len(data) == 8
		method_hint = data[1].split(" ")[-1]
		if method_hint.lower() in Source.method_hints:
			self.method_hint = method_hint.lower()
		else:
			self.method_hint = None
		#else:
		#	print "No method hint given for", data[3], ">" if data[1] else "", data[1] 
		self.data = data
		self.type = Source.BUDGET

	def amount(self):
		return self.amount_owed()

	def amount_owed(self):
		return abs(float(self.data[2]))

	def date(self):
		return datetime.datetime.strptime(self.data[6], "%d/%m/%Y").date()

	def details(self):
		if self.data[1]:
			return self.data[1]
		return self.data[3]

	def __str__(self):
		return "B(%s, \"%s\", %s)" % (str(self.date()), self.details(), str(self.amount()))