import numpy as np
import pandas as pd
import VA_PYTHON as va
import VD_KDB as vd
from collections import defaultdict
import datetime as dt
import types
import ipdb

def timeunitparse(timeunit):
    for i in timeunit:
        try:
            int(i)
        except ValueError:
            [value,unit] = timeunit.split(i)
            unit = i + unit
            return (int(value),unit)

class simulator():

    def __init__(self,timeunit = '1ms'):

        '''
        timeunit:in millisecond
        '''

        self.currentTime = None
        self.passedTime = None
        self.datalist=[]
        self.data = defaultdict()
        self.ready = False
        self.dataloader = vd.pyapi.dataloader()
        self.timeunit = None

        value,unit = timeunitparse(timeunit)
        if unit == 'ms':
            self.timeunit = dt.timedelta(0,0,value*1000)
        elif unit == 's':
            self.timeunit = dt.timedelta(0,value)
        elif unit == 'd':
            self.timeunit = dt.timedelta(value)

        self.currentTime = dt.datetime.now()

    def statuscheck(self):
        '''
        check whether the data and other parametes are ready for simulation
        '''
        self.ready = True

        if len(self.data) == 0:
            self.ready = False
            print 'data not ready'

    def setdatalist(self,datalist):
        '''
        fill datalist in a convenient way

        input:
            datalist: tuple of ('forex_quote-usdjpy','source-symbol')
        output:
            list of dict
            self.datalist:[{'name':symbol,'source':source},...]
        '''

        if type(datalist) is not types.TupleType:
            datalist = (datalist,)

        for SourceSymbol in datalist:
            try:
                [source,symbol] = SourceSymbol.split('-')
                temp = {}
                temp['name'] = symbol
                temp['source'] = source
                self.datalist.append(temp)
            except ValueError:
                source = SourceSymbol
                temp = {}
                temp['name'] = source
                temp['source'] = source
                self.datalist.append(temp)

    def emptydatalist(self):
        self.datalist = []

    def replaceData(self,date):
        '''
        replace 1 day data into simulator for dispatch
        '''
        for element in self.datalist:
            self.data[element['name']] = self.dataloader.tickerload(symbol = element['name'],source = element['source'],begindate = date)

    def dispatch(self):

        #self.combineandsort()

        for i in range(86400000):

            self.currentTime += self.timeunit
            print self.currentTime

    def simulate(self,begindate,enddate):
        self.statuscheck()
        if self.ready == False:
           return -1

        for date in range(4):
            self.replaceData(date)
            self.dispatch()


