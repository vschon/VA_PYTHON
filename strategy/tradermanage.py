import numpy as np
import pandas as pd
import VA_PYTHON as va
import VD_KDB as vd
from collections import defaultdict
import datetime as dt

import ipdb

class trader(object):
    '''
    virtual class for trader
    It should be overriden by real trader functions
    '''

    def __init__(self):
        self.state = {}
        self.filterlib = {}

    def initializeFilterlib(self):
        pass

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

    def core(self):
        '''
        working flow of updatestate() and logic()
        '''
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
