import numpy as np
import pandas as pd
import VA_PYTHON as va
import VD_KDB as vd
from collections import defaultdict
import datetime as dt
from dateutil.parser import parse

import ipdb

class trader(object):
    '''
    virtual class for trader
    It should be overriden by real trader functions
    '''

    def __init__(self):

        self.name = ''
        self.currentStat = None
        self.stateUpdate = False

        self.symbols = []
        self.filter = []
        self.timer = None
        self.now = None
        self.sender = []

        self.simIncrementTime = None

    def setname(self,name):
        self.name = name

    def setsymbols(self,symbols):
        '''
        set symbols to be sent out by trader
        '''

        self.symbols = va.utils.utils.formlist(symbols)

    def setsimtimer(self,initialtime,increment):
        '''
        time used to update time for simulatiorn mode
        beginTime:str,the beginning time of simulation timer
        increment:int, the smallest increment(in micro-seconds) of the timer
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
        set sender for each symbol in the trader.symbols
        TO BE IMPROVED
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

        filters = va.utils.utils.formlist(filters)
        for filter in filters:
            temp = None
            if filter == 'forex_quote':
                temp = va.strategy.filter.forex_quoteFilter()
            else:
                pass
            self.filter.append(temp)

    def link_filter_trader(self):
        '''
        send trader object to filter
        '''
        for item in self.filter:
            item.linkTrader(self)

    def linkimdb(self,imdblist):
        '''
        pass imdb to the trader filter
        input:[imdb0,imdb1]
        imdb0,1 matches self.filter[0] self.filter[1]
        '''

        imdblist = va.utils.utils.formlist(imdblist)
        for i in range(len(imdblist)):
            self.filter[i].setDataSource(imdblist[i])

    def setparams(self,params):
        '''
        set the parameters of trader
        '''
        pass


    ####CORE-BEGIN####
    def updatestate(self):
        '''
        update state value at current time
        '''
        pass

    def logic(self):
        '''
        make trading decisions based on current state
        '''
        pass

    def run(self):
        '''
        working flow of updatestate() and logic()
        '''
        while True:
            self.timer()

            self.updatestate()

            self.logic

    ####CORE-END####

class simOrderSender():
    pass

class TraderLoader():
    '''
    Save and Initialzie all traders
    return a trader object when called
    '''
    def __init__(self):
        '''
        Initializng traders
        '''
        self.traderlib = {}
        self.traderlib['hawkes'] = va.strategy.hawkes.newhawkes.hawkesTrader()

    def load(self,trader):
        if trader in self.traderlib.keys():
            return self.traderlib[trader]
        else:
            print 'trader name not in trader library'
            return -1
