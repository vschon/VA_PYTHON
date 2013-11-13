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


class hawkesTrader(va.strategy.tradermanage.trader):

    '''
    object to implement hawkes trading strategy
    '''

    def __init__(self):

        va.strategy.tradermanage.trader.__init__()

        #initialize the state
        self.currentState = {'time':None,
                      'price':None,
                      'pos':None,
                      'neg':None,
                      'rate':None}
        self.stateUpdated = False

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
        self.number = 0

        #store the pending exit
        self.PendingExit = []


    def setparams(self,params):
        '''
        settthe parameters of hawkes process
        otherwise, use default
        '''

        #set theta
        theta = params['theta']

        self.mu = np.array(theta[:2]).reshape(2,1)
        self.alpha = np.array(theta[2:6]).reshape(2,2)
        self.beta = np.array(theta[6:8]).reshape(2,1)

        #set the number of units to trade
        self.number = params['number']

        #set the threshold for trigerring trades
        self.threshold = params['k']

        #set time in seconds to exit an opened positions
        self.exitdelta = dt.timedelta(0, params['exitdelta'])


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
            temp_order = self.PendingExit[0]['direction']
            self.sender.SendOrder(direction=temp_order['direction'],open=False,symbol=self.symbol[0],number=self.number)
            self.PendingExit.pop(0)


        #Enter new positions
        if self.now < self.DailyStopTime:
            if self.stateUpdated == True:
                if self.currentState['rate'] > self.threshold:
                    self.PendingExit.append({'time':self.now + self.exitdelta,'direction': 'short'})
                    self.sender[0].SendOrder(direction = 'long', open = True, symbol = self.symbols[0], number = self.number)
                elif self.currentState['rate'] < 1/self.thresold:
                    self.PendingExit.append({'time':self.now + self.exitdelta,'direction':'long'})
                    self.sender[0].SendOrder(direction = 'short', open = True, symbol = self.symbols[0], number = self.number)
                self.stateUpdated = False

    ############CORE-END############

