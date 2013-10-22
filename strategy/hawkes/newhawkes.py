import numpy as np
import pandas as pd
import VA_PYTHON as va
import VD_KDB as vd
import datetime as dt
from collections import defaultdict
import math

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

        self.filterLoader = FilterLibrary()
        self.filter = None

        #timer: function to get current time
        self.timer = None

        #now: object to store current time
        self.now = None

        self.OrderManagerLoader = OrderManagerLibrary()
        self.orderManager = None

        self.a11 = 0.1
        self.a22 = 0.6
        self.a21 = 0.6
        self.a22 = 0.1
        self.mu1 = 0.5
        self.mu2 = 0.5
        self.beta1 = 1.0
        self.beta2 = 1.0
        self.threshold = 3.0

        #store the pending exit
        self.PendingExit = []
        self.exitdelta = dt.timedelta(0,5)

        #trader will not enter into new positions after DailyStopTime
        self.DailyStopTime = None


    def setname(self,tradername):
        self.name = tradername

    def setfilter(self,filtername):
        '''
        set the filter of trader
        filter name is the name of the table in KDB
        '''
        self.filter = self.filterLoader.filterLoader[filtername]

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


    def setStopTime(self,DailyStopTime):
        '''
        set daily stop time
        trader will open new positions afte stop time
        '''

        self.DailyStopTime = DailyStopTime

    def setOrderManager(self,orderManager):
        '''
        set the object to send orders
        '''
        self.orderManager = self.OrderManagerLoader.OrderManagerLoader(orderManager)


    def updatestate(self, point):
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

    def exitPositions(self):
        '''
        exit previous entered positions
        '''
        while self.now >= self.PendingExit[0]['time']:
            #Order(self.PendingExit)
            print 'close positions'
            self.PendingExit.pop(0)
            pass


    def logic(self):

        #Exit existing positions
        self.exitPositions()

        #Enter new positions
        if self.now < self.DailyStopTime:
            if self.stateUpdated == True:
                if self.currentState['rate'] > self.threshold:
                    self.PendingExit.append({'time':self.now + self.exitdelta,'type': -1})
                    self.orderManager.SendOrder()
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
            point = self.filter.fetch()
            self.now = self.timer()

            if point != -1:
                self.updatestate(point)
            self.logic()




### Filters for Hawkes Trader####
### Filter is the interface between trader and database
class FilterLibrary():
    def __init__(self):
        self.filterlibrary = {}
        self.filterlibrary['forex_quote'] = forex_quoteFilter()

    def filterLoader(self,filter):
        if filter in self.filterlibrary.keys():
            return self.filterlibrary[filter]
        else:
            return -1
            print 'No filter name in the filter library'

class forex_quoteFilter():
    '''
    forex filter for hawkes trader
    linking to the in memory database
    '''

    def __init__(self):
        self.datasource = None
        self.counter = 0

    def setDataSource(self,datasource):
        self.datasource = datasource

    def fetch(self):
        '''
        fetch data from database

        incoming data structure:

        tuple
        0:time/
        1:date/
        2:symbol/
        3:time/
        4:bid/
        5:ask
        '''

        point = self.datasource[self.counter]
        if point[4] != 0:
            self.counter += 1
            return {'time':point[0].to_datetime(),'price':(point[4]+point[5])/2.0}
        else:
            return -1


#Order manager for hawkes trader
#Order manager is the interface between trader and broker/simulator

class OrderManagerLibrary():
    def __init__(self):
        self.OrderManagerLibrary = {}
        self.OrderManagerLibrary['sim'] = simOrderManager()

    def OrderManagerLoader(self,orderManager):
        if orderManager in self.OrderManagerLibrary.keys():
            return self.OrderManagerLibrary[orderManager]
        else:
            return -1
            print 'No order manager' + orderManager + 'in the filter library'


class simOrderManager():

    def __init__(self):
        self.idcounter = 0
        self.time = None
        self.simReceiver = None

    def getTraderTime(self,trader):
        self.time = trader.now

    def setSimulator(self,simulatorReceiver):
        '''
        Set the function of simulator to receive order
        '''
        self.simReceiver = simulatorReceiver

    def SendOrder(self,direction,open,symbol,orderType,number):
        self.getTraderTime()
        order = va.simulator.simulator.generateSimOrder(id = self.idcounter,
                                                        time = self.time,
                                                        direction = direction,
                                                        open = open,
                                                        orderType = 'MARKET',
                                                        number = number)
        self.simReceiver(order)




