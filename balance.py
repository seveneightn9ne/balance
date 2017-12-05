#!/usr/bin/env python
from amex import Amex
from moneylover import MoneyLover
from splitwise import Splitwise
from transaction import Transaction
import csv
from datetime import date, timedelta
import codecs

class Balancer(object):
	def __init__(self, month, year, bank, budget, splitwise):
		self.month = month
		self.year = year
		self.bank = bank
		self.budget = budget
		self.splitwise = splitwise

		self.startdate = date(year, month, 1)
		self.enddate = self.startdate.replace(month=(month%12)+1) - timedelta(days=1)
		splitwise.load_expenses(self.startdate, self.enddate)
		self.transactions = [Transaction().add(e) 
			for e in bank.iterate(self.startdate) + splitwise.iterate_debts()]
		self.unreconciled_budget = set(self.budget.data[:])

	def fill_in_splitwise_payer(self):
		for transaction in self.transactions:
			amount = transaction.charge()
			possible_splitwise_entries = self.splitwise.by_amount_paid[amount]
			if len(possible_splitwise_entries) == 1:
				transaction.add(possible_splitwise_entries[0])
				#print "Matched", possible_splitwise_entries[0], " to ", transaction
			elif len(possible_splitwise_entries) > 1:
				for splitwise_entry  in possible_splitwise_entries:
					if splitwise_entry.date() == transaction.date():
						transaction.add(splitwise_entry)
						#print "Matched", splitwise_entry, " to ", transaction
						break
				else:
					print "Can't tell which Splitwise entry matches this transaction:"
					print "\t", ",".join(map(str, possible_splitwise_entries))
					print "\t", transaction

	def fill_in_budget_source(self):
		done = set([])
		for entry in self.unreconciled_budget:
			if entry.method_hint in ("cash", "bitcoin"):
				self.transactions.append(Transaction().add(entry))
				done.add(entry)
		self.unreconciled_budget -= done

	def fit(self, transaction, budget_entries, heuristic):
		matches = [b for b in budget_entries if heuristic(transaction, b)]
		if len(matches) != 1:
			return False
		transaction.add(matches[0])
		self.unreconciled_budget.remove(matches[0])
		return True

	# heuristics
	def hint(self, t, b):
		if not b.method_hint:
			return True
		if not t.method():
			return True
		return b.method_hint == t.method()
	def amount(self, t, b):
		return t.guess_budget_amount() == b.amount()
	def near_amount(self, t, b):
		return abs(t.guess_budget_amount() - b.amount()) < 1
	def date(self, t, b):
		return t.date() == b.date()
	def near_date(self, t, b):
		return abs(t.date() - b.date()) < timedelta(days=2)
	def keywords(self, t, b):
		return len(set(t.keywords()) & set(b.keywords())) > 0

	def resolve(self):
		# Transaction <-> Moneylover where date and amount match
		for transaction in self.transactions:
			if not transaction.needs_budget():
				continue
			# best resolvers first.
			resolvers = [
				lambda t, b: self.amount(t,b),
				lambda t, b: self.hint(t,b) and self.amount(t,b),
				lambda t, b: self.hint(t,b) and self.amount(t,b) and self.date(t,b),
				lambda t, b: self.hint(t,b) and self.amount(t,b) and self.near_date(t,b),
				lambda t, b: self.hint(t,b) and self.amount(t,b) and self.keywords(t,b),
				lambda t, b: self.hint(t,b) and self.near_amount(t,b) and self.date(t,b),
				# TODO - near_amount
			]
			for r in resolvers:
				if self.fit(transaction, self.unreconciled_budget, r):
					break
			else:
				matches_last = [b for b in self.unreconciled_budget if resolvers[-1](transaction, b)]
				if len(matches_last) > 1:
					print "Many budget entries match the transaction:", transaction
					for b in matches_last:
						print "\t", str(b)
				

	def reflect(self):
		def by_date(t):
			return t.date()
		transactions_resolved = sorted([t for t in self.transactions if t.resolved()],
			key=by_date)
		transactions_unresolved = sorted([t for t in self.transactions if not t.resolved()],
			key=by_date)
		print "%d resolved transactions." % len(transactions_resolved)
		if len(transactions_unresolved):
			print "%d unresolved transactions:" % len(transactions_unresolved)
			for t in transactions_unresolved:
				print "\t", str(t) 
		if len(self.unreconciled_budget):
			print "%d unreconciled budget entries:" % len(self.unreconciled_budget)
			for b in sorted(self.unreconciled_budget, key=by_date):
				print "\t", str(b.date()), str(b)


def main(month, year, inputs):
	"""
	inputs: {
		"amex": {
			"user": "Jessica Kenney",
			"amex.csv",
		},
		"moneylover": "moneylover.csv",
		"splitwise": {
			"key": "2343abc323434boeuboeu",
			"secret": "23094eu4eutnh4ibui55",
		}
	}
	"""
	sources = []
	with open(inputs["amex"]["file"], "rb") as f:
		amex_data = csv.reader(f)
		amex = Amex(inputs["amex"]["user"], amex_data)
	with codecs.open(inputs["moneylover"], "rb", "utf-16") as f:
		moneylover_data =  csv.reader(f, delimiter=";")
		moneylover = MoneyLover(moneylover_data)
	splitwise = Splitwise(inputs["splitwise"]["key"], inputs["splitwise"]["secret"])
	b = Balancer(month, year, amex,  moneylover, splitwise)

	b.fill_in_splitwise_payer()
	b.fill_in_budget_source()
	b.resolve()
	print
	b.reflect()

if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser(description='balance your budget across accounts')
	parser.add_argument('MM/YY', help='month to reconcile')
	parser.add_argument('amex', 
                   	help='American Express transaction export CSV')
	parser.add_argument('--user', '-U',
                   	help='American Express User to filter for')
	parser.add_argument('moneylover',
                   	help='MoneyLover transaction export CSV')
	parser.add_argument('skey',
                   	help='Splitwise API Consumer Key')
	parser.add_argument('ssecret',
                   	help='Splitwise API Consumer Secret')
	args = parser.parse_args()

	month, year = map(int, vars(args)['MM/YY'].split('/'))
	if year < 2000:
		year += 2000
	main(month, year, {
		"amex": {
			"file": args.amex,
			"user": args.user,
		},
		"moneylover": args.moneylover,
		"splitwise": {
			"key": args.skey,
			"secret": args.ssecret,
		},
		})
