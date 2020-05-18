import time
import sys
import random
import json
import numpy as np
from decimal import Decimal

from exchange.ExchangeClient import ExchangeClient
import config

client = ExchangeClient(config.apiid, config.secret)

with open ('parameters.json', 'r') as parameterFile:
    data=parameterFile.read()

parameters = json.loads(data)
minTrade = int(parameters['minTrade'])
maxTrade = int(parameters['maxTrade'])
minWaitTimeMS = int(parameters['minWaitTimeMS'])
maxWaitTimeMS = int(parameters['maxWaitTimeMS'])
pair = "SKYM/USDT"

tradeNumber = 0
def sellAndBuyOrders(bids, asks, exchangeAmount):
    global tradeNumber
    lastPrice = client.market_trades(pair)['data'][0][1]
    bidPrice = float(bids[0][0])
    askPrice = float(asks[0][0])

    print("Last price: " + str(lastPrice))
    print("Bid price: " + str(bidPrice))
    print("Ask price: "  + str(askPrice))

    askPrice = min(float(lastPrice) * 1.49, askPrice)
    range = 10
    price = round(bidPrice + float(random.randint(1, range-1)) * (askPrice - bidPrice) / float(range), 6)

    buy = 1
    sell = 2
    limitOrder = 1
    print("ORDER: ")
    print(price)
    if tradeNumber % 2 is 0:
        # Sell first then buy
        print( client.order_place(pair, sell, price, exchangeAmount, limitOrder, None, None) )
        print( client.order_place(pair, buy, price, exchangeAmount, limitOrder, None, None) )
    else:
        # Buy first then sell
        print( client.order_place(pair, buy, price, exchangeAmount, limitOrder, None, None) )
        print( client.order_place(pair, sell, price, exchangeAmount, limitOrder, None, None) )

    tradeNumber = tradeNumber + 1

    return False

def successfulTrade(orderbook):
    bids = orderbook['bids']
    asks = orderbook['asks']

    exchangeAmount = random.randint(minTrade, maxTrade)
    didTrade = sellAndBuyOrders(bids, asks, exchangeAmount)

    return didTrade

def runTrades():
    while(True):
        orderBook = client.order_book(pair, 5)['data']
        successfulTrade(orderBook)
        time.sleep(random.randint(minWaitTimeMS, maxWaitTimeMS) / 1000)

runTrades()
