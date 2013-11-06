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
    '''
    def __init__(self):
        self.orderMatcherLibrary = {}

    def orderMatcherLoader(self,matcher):
        if matcher in self.orderMatcherLoader.keys():
            return self.orderMatcherLibrary[matcher]
        else:
            print 'No ' + matcher + ' name in the filter library'
            return -1

class forex_quote_market_matcher():
    '''
    used to match transactions in forex_quote database
    '''

    def __init__(self):

        #delay in milliseconds
        self.delay = dt.timedelta(0,0,0)

    def match(self,order,hdb):
        pass
