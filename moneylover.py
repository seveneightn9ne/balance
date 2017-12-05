#!/usr/bin/env python
import datetime
from collections import defaultdict
from source import Source, Entry
from pprint import pprint

class MoneyLover(Source):
	def __init__(self, data):
		headers = data.next() # skip the header row
		entries = [MoneyLoverEntry(headers, d) for d in data]
                entries = [e for e in entries if not (e.exclude_report() and e.amount() >= 0)]
		self.by_date = defaultdict(list)
		self.by_keyword = defaultdict(list)
		self.by_amount = defaultdict(list)
		for entry in entries:
			self.by_date[entry.date()].append(entry)
			self.by_amount[entry.amount_owed()].append(entry)
			keywords = map(lambda k: k.lower(), entry.details().split(" "))
			for k in keywords:
				if k and k not in Source.method_hints and k not in ("and", "the"):
					self.by_keyword[k].append(entry)
			
		super(MoneyLover, self).__init__(entries, Source.BUDGET)

# android: ID;Note;Amount;Category;Account;Currency;Date;Event;Exclude Report
# ios    : Id;Date;Category;Amount;Currency;Note;Wallet
platform = "ios"

class MoneyLoverEntry(Entry):
	def __init__(self, headers, row):
		self.row = row
                self.m = {h.lower(): d for (h,d) in zip(headers, row)}

		method_hint = self.m["note"].split(" ")[-1]
		if method_hint.lower() in Source.method_hints:
			self.method_hint = method_hint.lower()
		else:
			self.method_hint = None
		#else:
		#	print "No method hint given for", row[3], ">" if row[1] else "", row[1] 
		self.type = Source.BUDGET

	def amount(self):
		return self.amount_owed()

	def amount_owed(self):
		return abs(float(self.m["amount"]))

	def date(self):
		if platform == "android":
			return datetime.datetime.strptime(self.m["date"], "%d/%m/%Y").date()
		elif platform == "ios":
			return datetime.datetime.strptime(self.m["date"], "%Y-%m-%d").date()
		else:
			assert false # android of ios?

	def details(self):
		if "note" in self.m:
			return self.m["note"]
		return self.m["category"]

	def exclude_report(self):
		return self.m.get("exclude report", "No") != "No"

	def __str__(self):
		return "B(%s, \"%s\", %s)" % (str(self.date()), self.details(), str(self.amount()))
