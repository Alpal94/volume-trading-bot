import time
import sys
import random
import json
import numpy as np
from decimal import Decimal

from exchange.ExchangeClient import ExchangeClient
import config

client = ExchangeClient(config.apiid, config.secret)

minTrade = -1
maxTrade = -1
minWaitTimeMS = -1
maxWaitTimeMS = -1
pair = "SKYM/USDT"


def updateParameters():
    global minTrade
    global maxTrade
    global minWaitTimeMS
    global maxWaitTimeMS

    with open ('parameters.json', 'r') as parameterFile:
        data=parameterFile.read()

    parameters = json.loads(data)
    minTrade = int(parameters['minTrade'])
    maxTrade = int(parameters['maxTrade'])
    minWaitTimeMS = int(parameters['minWaitTimeMS'])
    maxWaitTimeMS = int(parameters['maxWaitTimeMS'])

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
    upwardsScale = 1.01
    downwardsScale = 0.99
    if float(lastPrice) * upwardsScale < askPrice and float(lastPrice) * upwardsScale > bidPrice:
        print("Using adjusted price (upward)")
        price = float(lastPrice) * upwardsScale
    elif float(lastPrice) * downwardsScale > bidPrice and float(lastPrice) * downwardsScale < askPrice:
        print("Using adjusted price (downward)")
        price = float(lastPrice) * downwardsScale
    else:
        price = round(bidPrice + float(random.randint(1, range-1)) * (askPrice - bidPrice) / float(range), 6)

    price = round(price, 6)
    buy = 1
    sell = 2
    limitOrder = 1
    print("ORDER: ")
    print(price)
    # Sell first then buy
    print( client.order_place(pair, sell, price, exchangeAmount, limitOrder, None, None) )
    print( client.order_place(pair, buy, price, exchangeAmount, limitOrder, None, None) )

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
        updateParameters()
        orderBook = client.order_book(pair, 5)['data']
        successfulTrade(orderBook)
        time.sleep(random.randint(minWaitTimeMS, maxWaitTimeMS) / 1000)

runTrades()
def closeBotsOrders():
    botsOpenOrders = client.open_orders(None, None)['data']
    orderIds = []
    for i in range(len(botsOpenOrders)):
        orderIds.append(botsOpenOrders[i]['orderId'])
        if len(orderIds) == 10:
            print(client.batch_cancel(orderIds))
            orderIds = []

#closeBotsOrders()
