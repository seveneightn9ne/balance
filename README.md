# balance
Helps resolve monthly expenses to make sure you didn't miss any in budgeting.

This is made for using with American Express credit card, Splitwise, and MoneyLover budgeting app, but can be expanded to support others.

# Set up
1. Create yourself a Splitwise app: https://secure.splitwise.com/apps Register your application, and get the Consumer Key and Consumer Secret. You only need to do this once, not every month.
2. Download your American Express transactions from just this month as a CSV.
3. Export your MoneyLover transactions from this month as a CSV.

# Use
```./balance.py 12/17 ~/balance-data/amex-2017-12.csv ~/balance-data/MoneyLover-2017-12-31.csv -P android splitwise_consumer_key splitwise_consumer_secret```
* Replace `12/17` with the month/year you are balancing. 
* Replace `-P android` with `-P ios` if your MoneyLover export came from the iOS app. 
* `splitwise_consumer_key` and `splitwise_consumer_secret` should be the values you got from the 

