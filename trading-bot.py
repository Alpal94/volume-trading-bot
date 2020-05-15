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
    bidPrice = float(bids[0][0])
    askPrice = float(asks[0][0])
    print(bidPrice)
    print("VS")
    print(askPrice)

    possibleSellPrices = np.linspace(bidPrice+inc, bidPrice+inc+(inc*numBids), numBids, endpoint = False)

    range = 10
    price = bidPrice + float(random.randint(1, range-1)) * (bidPrice - askPrice) / float(range)

    buy = 1
    sell = 2
    limitOrder = 1
    if client.order_place(symbol, buy, price, amount, limitOrder):
        if client.order_place(symbol, sell, price, amount, limitOrder):
            return True
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

    waitTime = random.randint(5, 25)
    time.sleep(waitTime)

symbol = "SKYM/USDT"
runTrades(symbol, 1000)
