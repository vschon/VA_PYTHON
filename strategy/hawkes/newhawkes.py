import numpy as np
import pandas as pd
import VA_PYTHON as va
import VD_KDB as vd
import datetime as dt
from collections import defaultdict
import math
import types
from dateutil.parser import parse

import ipdb


class hawkesTrader():

    '''
    object to implement hawkes trading strategy
    '''

    def __init__(self):

        self.name = 'hawkes_trader'

        #initialize the state
        self.currentState = {'time':None,
                      'price':None,
                      'pos':None,
                      'neg':None,
                      'rate':None}
        self.stateUpdated = False

        #stored the symbols to be sent out by trader
        self.symbols=[]

        self.filter = []

        #timer: function to get current time
        self.timer = None

        #now: object to store current time
        self.now = None

        #store order senders
        self.sender = []

        self.simIncrementTime = None

        #parameters
        self.a11 = 0.1
        self.a22 = 0.6
        self.a21 = 0.6
        self.a22 = 0.1
        self.mu1 = 0.5
        self.mu2 = 0.5
        self.beta1 = 1.0
        self.beta2 = 1.0
        self.threshold = 3.0
        self.exitdelta = dt.timedelta(0,5)
        #trader will not enter into new positions after DailyStopTime
        self.DailyStopTime = None

        #store the pending exit
        self.PendingExit = []

    def setname(self,tradername):
        self.name = tradername

    def setsymbols(self,symbols):
        '''
        set symbols to be sent out by trader
        '''
        if type(symbols) is not types.TupleType and type(symbols) is not list:
            self.symbols = [symbols,]
        else:
            self.symbols = symbols

    def setsimtimer(self,initialtime,increment):
        '''
        timer used to update time for simulation mode

        beginTime: str,the beginning time of simulation timer
        increment: int,the smallest increment(in micro-second) of the timer
        '''
        self.timer = self.simtimer()
        self.now = parse(initialtime)
        self.simIncrementTime = dt.timedelta(0,0,increment)

    def simtimer(self):
        '''
        simulation timer
        '''
        self.now += self.simIncrementTime

    def realtimer(self):
        '''
        real timer
        '''
        self.now = dt.datetime.now()

    def setsender(self,senders):
        '''
        set the senders for each arm of the trader
        '''

        senders = va.utils.utils.formlist(senders)

        for sender in senders:
            temp = None
            if sender == 'sim':
                temp = simOrderSender()
            self.sender.append(temp)

    def setfilter(self,filters):
        '''
        set the filter for each arm of trader
        filter name is the name of the table in DB
        '''
        if type(filters) is not types.TupleType and type(filters) is not list:
            filters = [filters,]

        for filter in filters:
            temp = None
            if filter == 'forex_quote':
                temp = va.strategy.filter.forex_quoteFilter()
            else:
                pass
            self.filter.append(temp)

    def link_filter_trader(self):
        '''
        send trader object to each filter of the trader
        '''

        for item in self.filter:
            item.linkTrader(self)

    def linkimdb(self,imdblist):
        '''
        pass imdb to the trader filer
        input [imdb0,imdb1]
        imdb1,imdb2 matches self.filter[0] self.filter[1]
        '''

        imdblist = va.utils.utils.formlist(imdblist)

        for i in range(len(imdblist)):
            self.filter[i].setDataSource(imdblist[i])


    def setparams(self,theta):
        '''
        settthe parameters of hawkes process
        otherwise, use default
        '''

        self.mu = np.array(theta[:2]).reshape(2,1)
        self.alpha = np.array(theta[2:6]).reshape(2,2)
        self.beta = np.array(theta[6:8]).reshape(2,1)

    def setthreshold(self, k):
        '''
        set the threshold for trigerring trades
        '''
        if k > 1:
            self.threshold = k
        else:
            print 'K should be larger than 1'

    def setStopTime(self, DailyStopTime):
        '''
        set daily stop time
        trader will not open new positions afte stop time
        '''

        self.DailyStopTime = parse(DailyStopTime)

    def setExitDelta(self, delta):
        '''
        set time in seconds to exit an opened positions
        '''
        self.exitdelta = dt.timedelta(0, delta)

    ############CORE-BEGIN############

    def updatestate(self):
        '''
        get data from imdb
        update state
        '''

        point = self.filter[0].fetch()

        #Only price change is processed
        if point['price'] != self.currentState['price']:
            delta = (point['time'] - self.currentState['time']).total_seconds()
            mark = point['price'] - self.currentState['price']

            if mark > 0:
                self.currentState['pos'] = (self.currentState['pos'] - self.mu1)/math.exp(self.beta1*delta) + self.mu1 + self.a11
                self.currentState['neg'] = (self.currentState['neg'] - self.mu2)/math.exp(self.beta2*delta) + self.mu2 + self.a21
            else:
                self.currentState['pos'] = (self.currentState['pos'] - self.mu1)/math.exp(self.beta1*delta) + self.mu1 + self.a12
                self.currentState['neg'] = (self.currentState['neg'] - self.mu2)/math.exp(self.beta2*delta) + self.mu2 + self.a22

            self.currentState['rate'] = self.currentState['pos']/self.currentState['neg']
            self.currentState['time'] = point['time']
            self.currentState['price'] = point['price']

            self.stateUpdated = True


    def logic(self):

        #Exit existing positions
        while self.now >= self.PendingExit[0]['time']:
            #Order(self.PendingExit)
            print 'close positions'
            self.PendingExit.pop(0)


        #Enter new positions
        if self.now < self.DailyStopTime:
            if self.stateUpdated == True:
                if self.currentState['rate'] > self.threshold:
                    self.PendingExit.append({'time':self.now + self.exitdelta,'type': -1})
                    self.sender.SendOrder()
                    print 'long open'
                elif self.currentState['rate'] < 1/self.thresold:
                    self.PendingExit.append({'time':self.now + self.exitdelta,'type': 1})
                    print 'short open'
                self.stateUpdated = False

    def run(self):
        '''
        every call filter to fetch data from db
        if new tick arrive, then update state

        incoming point data structure
        {'time':2013.11.08T09:00:00,
        'price':99.9}

        '''
        while True:
            #update time
            self.timer()

            #update state
            self.updatestate()

            #trade based on current state
            self.logic()


    ############CORE-END############


##############SENDER#############
#Order manager for hawkes trader
#Order manager is the interface between trader and broker/simulator

class simOrderSender(va.strategy.SimOrderSender.SimOrderSender):

    def SendOrder(self,direction,open,symbol,orderType,number):
        self.time = self.trader.now
        order = va.simulator.simulator.generateSimOrder(id = self.idcounter,
                                                        time = self.time,
                                                        direction = direction,
                                                        open = open,
                                                        orderType = 'MARKET',
                                                        number = number)
        self.simulator.OrderProcessor(order)




