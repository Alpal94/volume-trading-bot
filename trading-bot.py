import time
import sys
import random
import json
import numpy as np
import math
import threading
from decimal import Decimal

from exchange.ExchangeClient import ExchangeClient
import config

client = ExchangeClient(config.apiid, config.secret)

minTrade = -1
maxTrade = -1
minWaitTimeMS = -1
maxWaitTimeMS = -1
pair = "SKYM/USDT"

upwardDownward = 1
tradeNumber = 0

def defaultParameters():
    global minTrade
    global maxTrade
    global minWaitTimeMS
    global maxWaitTimeMS
    global deleteOrders
    global active
    
    minTrade = 50
    maxTrade = 1000
    minWaitTimeMS = 0
    maxWaitTimeMS = 0
    deleteOrders = "off"
    active = "on"

def updateParameters():
    global minTrade
    global maxTrade
    global minWaitTimeMS
    global maxWaitTimeMS
    global deleteOrders
    global active

    parameterFile = open ('/var/www/volume-trading-bot/parameters.json', 'r')
    data=parameterFile.read()

    #Get parameters
    parameters = json.loads(data)
    minTrade = int(parameters['minTrade'])
    maxTrade = int(parameters['maxTrade'])
    minWaitTimeMS = int(parameters['minWaitTimeMS'])
    maxWaitTimeMS = int(parameters['maxWaitTimeMS'])
    deleteOrders = parameters['delete']
    active = parameters['active']

    #Update parameters
    parameters['delete'] = "off"

    if tradeNumber % 20 == 0:
        USDT = client.account_one("USDT")
        SKYM = client.account_one("SKYM")
        parameters['USDT'] = USDT['data']['totalBalance']
        parameters['SKYM'] = SKYM['data']['totalBalance']


    parameterFile.close()
    if deleteOrders == "on" or tradeNumber % 20 == 0:
        parameterFile = open ('/var/www/volume-trading-bot/parameters.json', 'w')
        parameterFile.write(json.dumps(parameters))
        parameterFile.close()

def order(pair, direction, price, exchangeAmount, limitOrder):
    try:
        thread = threading.Thread( target=client.order_place, args=(pair, direction, price, exchangeAmount, limitOrder, None, None) )
        thread.start()
    except:
        print("Error: Unable to start thread")
    

def sellAndBuyOrders(bids, asks, exchangeAmount):
    global tradeNumber
    global upwardDownward
    lastPrice = client.market_trades(pair)['data'][0][1]
    bidPrice = float(bids[0][0])
    askPrice = float(asks[0][0])

    print("Last price: " + str(lastPrice))
    print("Bid price: " + str(bidPrice))
    print("Ask price: "  + str(askPrice))

    askPrice = min(float(lastPrice) * 1.49, askPrice)

    priceDiff = askPrice-bidPrice
    amplitude = priceDiff
    if priceDiff < 0.000004:
        print("Price diff too small.  Exiting.")
        return False
    price = bidPrice + priceDiff/2 + (0.90*amplitude/2) * math.sin(300 + tradeNumber / 200)
    price = round(price, 6)
    if priceDiff < 0.00001:
        print("Turning to random due to price difference")
        range = 100000
        price = round(bidPrice + float(random.randint(1000, range-1000)) * (askPrice - bidPrice) / float(range), 6)

    buy = 1
    sell = 2
    limitOrder = 1
    print("ORDER: ")
    print("Price: " + str(price))
    print("Exchange amount: " + str(exchangeAmount))
    # Sell first then buy
    order(pair, sell, price, exchangeAmount, limitOrder)
    order(pair, buy, price, exchangeAmount, limitOrder)

    tradeNumber = tradeNumber + 1

    return False

def successfulTrade(orderbook):
    bids = orderbook['bids']
    asks = orderbook['asks']

    amountDiff = maxTrade-minTrade
    amplitude = amountDiff
    period = 1000
    exchangeAmount = round(minTrade + amountDiff/2 + (amplitude/2) * math.sin(1.5*period + tradeNumber / period), 2)
    didTrade = sellAndBuyOrders(bids, asks, exchangeAmount)

    return didTrade

def closeTenOrders(botsOpenOrders):
    orderIds = []
    for i in range(len(botsOpenOrders)):
        orderIds.append(botsOpenOrders[i]['orderId'])
        if len(orderIds) == 10:
            print(client.batch_cancel(orderIds))
            orderIds = []

    if(len(orderIds)):
        print(client.batch_cancel(orderIds))

def closeBotsOrders():
    botsOpenOrders = client.open_orders(pair, None)['data']
    closeTenOrders(botsOpenOrders)

    botsOpenOrders = client.open_orders(pair, None)['data']
    while len(botsOpenOrders) > 5:
        closeTenOrders(botsOpenOrders)
        botsOpenOrders = client.open_orders(pair, None)['data']

def runTrades():
    while(True):
        #defaultParameters()
        updateParameters()

        print(time.asctime( time.localtime(time.time()) ))
        if deleteOrders == "on":
            print("Delete orders")
            closeBotsOrders()
        if active != "off":
            print("Execute trades")
            orderBook = client.order_book(pair, 5)['data']
            successfulTrade(orderBook)
            time.sleep(random.randint(minWaitTimeMS, maxWaitTimeMS) / 1000)
        else:
            print("Hibernating")
            time.sleep(1)


runTrades()
