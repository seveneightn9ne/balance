#!/usr/bin/env python
import datetime
from collections import defaultdict
from source import Source, Entry
from pprint import pprint
import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth

class Splitwise(Source):
	def __init__(self, key, secret):
		client = BackendApplicationClient(client_id=key)
		self.oauth = OAuth2Session(client=client)
		# token = oauth.fetch_token(token_url='https://secure.splitwise.com/oauth/token', auth=auth)
		token = self.oauth.fetch_token(token_url='https://secure.splitwise.com/oauth/token', client_id=key,
			client_secret=secret)

		self.user_info = self.oauth.get("https://secure.splitwise.com/api/v3.0/get_current_user").json()
		# data.next() # skip the header row
		# data = [MoneyLoverEntry(d) for d in data if d[7] == "No" and float(d[2]) < 0]
		# self.by_date = defaultdict(list)
		# self.by_keyword = defaultdict(list)
		# self.by_amount = defaultdict(list)
		# for entry in data:
		# 	d = entry.data
		# 	self.by_date[entry.date()].append(entry)
		# 	self.by_amount[entry.amount_owed()].append(entry)
		# 	keywords = map(lambda k: k.lower(), entry.details().split(" "))
		# 	for k in keywords:
		# 		if k and k not in MoneyLoverEntry.method_hints and k not in ("and", "the"):
		# 			self.by_keyword[k].append(entry)
			
		self.loaded = None
		super(Splitwise, self).__init__([], Source.IOU)
		# super(MoneyLover, self).__init__(data, Source.BUDGET)

	def load_expenses(self, startdate, enddate):
		if self.loaded == startdate:
			return
		#print "load", startdate, " to ", enddate
		params = {
			'dated_after':  startdate - datetime.timedelta(days=1),
			'dated_before': enddate + datetime.timedelta(days=1),
			'limit': 0,
		}
		#pprint(params)
		r = self.oauth.get("https://secure.splitwise.com/api/v3.0/get_expenses", params=params)
		u = self.user_info["user"]["id"]
		#print r
		#pprint(r.json())

		relevant = lambda e: any([user["user_id"] == u for user in e["users"]]) and e["creation_method"] not in ("debt_consolidation", "payment")
		self.data = [SplitwiseEntry(e, u) for e in r.json()["expenses"] if relevant(e) and e["deleted_at"] == None]
		self.by_date = defaultdict(list)
		self.by_keyword = defaultdict(list)
		self.by_amount_owed = defaultdict(list)
		self.by_amount_paid = defaultdict(list)
		for entry in self.data:
			#print
			#print entry.details()
			#pprint(entry.data)
			d = entry.data
			self.by_date[entry.date()].append(entry)
			self.by_amount_owed[entry.amount_owed()].append(entry)
			self.by_amount_paid[entry.amount_paid()].append(entry)
			keywords = map(lambda k: k.lower(), entry.details().split(" "))
			for k in keywords:
				if k and k not in ("and", "the"):
					self.by_keyword[k].append(entry)
		self.loaded = startdate

	def iterate_debts(self):
		assert self.loaded		
		return [e for e in self.data if e.amount_paid() < e.amount_owed()]


class SplitwiseEntry(Entry):

	def __init__(self, data, user_id):
		self.user_id = user_id
		self.data = data
		for user in data["users"]:
			if user["user_id"] == user_id:
				self.paid = float(user["paid_share"])
				self.owed = abs(float(user["owed_share"]))
				break
		else:
			pprint(data)
			raise ValueError("The user is not in the transaction")
		self.type = Source.IOU

	def amount_owed(self):
		return self.owed

	def amount_paid(self):
		return self.paid

	def date(self):
		return datetime.datetime.strptime(self.data["date"], "%Y-%m-%dT%H:%M:%SZ").date()

	def details(self):
		return self.data["description"]

	def __str__(self):
		return "S(\"%s\", %s, %s/%s)" % (self.details(), self.data["cost"], str(self.amount_owed()), str(self.amount_paid()))
