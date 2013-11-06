import numpy as np
import pandas as pd
import VA_PYTHON as va
import VD_KDB as vd
from VA_PYTHON.datamanage.datahandler import Sender
from collections import defaultdict
import datetime as dt
from time import strptime
from dateutil import rrule
from dateutil.parser import parse
import types
import ipdb

class orderMatcherLibrary():
    '''
    Used to store and return appropirate order matcher for simulator
    unique matcher for each data source
    '''
    def __init__(self):
        self.orderMatcherLibrary = set()

        #save matcher for each data source
        #key of dict is the name of data source
        self.orderMatcherLibrary.add('forex_quote')

    def orderMatcherLoader(self,matcher):
        if matcher in self.orderMatcherLibrary:
            return forex_quote_matcher()
        else:
            print 'No ' + matcher + ' name in the filter library'
            return -1

class forex_quote_matcher():
    '''
    used to match transactions in forex_quote database
    '''

    def __init__(self):

        #delay in milliseconds
        self.delay = dt.timedelta(0,0,0)

    def marketmatch(self,order,hdb):
        transactTime = order['time'] + self.delay

        #extract the data of the symbol
        symbolhdb = hdb[hdb['symbol']==order['symbol'].upper()]
        state = symbolhdb[:transactTime].ix[-1]
        if order['direction'] == 'long':
            transactPrice = state['ask']
        elif order['direction'] == 'short':
            transactPrice = state['bid']

        trade = {'time':transactTime,
                 'price':transactPrice,
                 'direction':order['direction'],
                 'symbol':order['symbol'],
                 'number':order['number'],
                 'open':order['open']}

        return trade

    def match(self,order,hdb):
        if order['type'] == 'MARKET':
            self.marketmatch(order,hdb)
        elif order['type'] == 'LIMIT':
            pass
