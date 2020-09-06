from pyrh import Robinhood
from datetime import datetime
import numpy as np
import tulipy as ti
import sched
import time
#A Simple Robinhood Python Trading Bot using RSI (buy <=30 and sell >=70 RSI) and with support and resistance.
#Youtube : Jacob Amaral
# Log in to Robinhood app (will prompt for two-factor)
rh = Robinhood()
rh.login(username="jayomayan", password="R0adtrip$$")
#Setup our variables, we haven't entered a trade yet and our RSI period
enteredTradeq = input("Have you entered trade [y/n]?\n")
if enteredTradeq == "y" or enteredTradeq == "Y":
    enteredTrade = True
else:
    enteredTrade = False
rsiPeriod = 5
#Initiate our scheduler so we can keep checking every minute for new price changes
s = sched.scheduler(time.time, time.sleep)
def run(sc):
    global enteredTrade
    global rsiPeriod
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("---------------------------------------")
    print("Getting historical quotes")
    print("---------------------------------------")
    print("Current Time          : ", current_time)

    # Get 5 minute bar data for Starbucks stock
    historical_quotes = rh.get_historical_quotes("SBUX", "5minute", "day")
    closePrices = []
    #format close prices for RSI
    currentIndex = 0
    currentSupport  = 0
    currentResistance = 0
    for key in historical_quotes["results"][0]["historicals"]:
        if (currentIndex >= len(historical_quotes["results"][0]["historicals"]) - (rsiPeriod + 1)):
            if (currentIndex >= (rsiPeriod-1) and datetime.strptime(key['begins_at'], '%Y-%m-%dT%H:%M:%SZ').minute == 0):
                currentSupport = 0
                currentResistance = 0
                print("Resetting support and resistance")
            if(float(key['close_price']) < currentSupport or currentSupport == 0):
               currentSupport = float(key['close_price'])
               print("Current Support is    : ", currentSupport)
               # print(currentSupport)
            if(float(key['close_price']) > currentResistance):
               currentResistance = float(key['close_price'])
               print("Current Resistance is : ", currentResistance)
               # print(currentResistance)
            closePrices.append(float(key['close_price']))
        currentIndex += 1
    DATA = np.array(closePrices)
    if (len(closePrices) > (rsiPeriod)):
        #Calculate RSI
        rsi = ti.rsi(DATA, period=rsiPeriod)
        instrument = rh.instruments("SBUX")[0]
        #If rsi is less than or equal to 30 buy
        if rsi[len(rsi) - 1] <= 30 and float(key['close_price']) <= currentSupport and not enteredTrade:
            print("Buying RSI is below 30!")
            rh.place_buy_order(instrument, 1)
            enteredTrade = True
        #Sell when RSI reaches 70
        if rsi[len(rsi) - 1] >= 70 and float(key['close_price']) >= currentResistance and currentResistance > 0 and enteredTrade:
            print("Selling RSI is above 70!")
            rh.place_sell_order(instrument, 1)
            enteredTrade = False
        print("RSI                   : ", rsi)
        print("---------------------------------------")
    #call this method again every 5 minutes for new price changes
    s.enter(300, 1, run, (sc,))
s.enter(1, 1, run, (s,))
s.run()
