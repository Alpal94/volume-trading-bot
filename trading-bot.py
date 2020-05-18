import time
import sys
import random
import json
import numpy as np
from decimal import Decimal

from exchange.ExchangeClient import ExchangeClient
import config

client = ExchangeClient(config.apiid, config.secret)

def sellAndBuyOrders(bids, asks, symbol, amount):
    lastPrice = client.market_trades(symbol)['data'][0][1]
    bidPrice = float(bids[0][0])
    askPrice = float(asks[0][0])
    askPrice = min(float(lastPrice) * 1.49, askPrice)

    print("Last price: " + str(lastPrice))
    print("Bid price: " + str(bidPrice))
    print("Ask price: "  + str(askPrice))


    range = 10
    price = round(bidPrice + float(random.randint(1, range-1)) * (askPrice - bidPrice) / float(range), 6)

    buy = 1
    sell = 2
    limitOrder = 1
    print("ORDER: ")
    print(price)
    amount = 50
    print( client.order_place(symbol, buy, price, amount, limitOrder, None, None) )
    print( client.order_place(symbol, sell, price, amount, limitOrder, None, None) )
    return False

def successfulTrade(orderbook, symbol, limit):
    bids = orderbook['bids']
    asks = orderbook['asks']

    exchangeAmount = min(random.randint(50, 1000), int(limit))
    didTrade = sellAndBuyOrders(bids, asks, symbol, exchangeAmount)

    return didTrade

def runTrades(symbol, limit):
    orderBook = client.order_book(symbol, 5)['data']
    successfulTrade(orderBook, symbol, limit)

    waitTime = random.randint(1, 3)
    time.sleep(waitTime)

symbol = "SKYM/USDT"
runTrades(symbol, 1000)
