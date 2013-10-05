import numpy as np
import pandas as pd
import VA_PYTHON as va
import VD_KDB as vd
from collections import defaultdict
import datetime as dt
from time import strptime
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

        #Store symbol to be sent out ['source-symbol']
        self.datalist=[]

        #store data {'name':data,'name':data}
        self.data = defaultdict()

        #store data that is in daily frequency
        #it is a subset of self.datalist
        self.dayfreqdatalist = []

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
        self.beginTimeDelta = dt.timedelta(0,0,0)
        self.endTimeDelta = dt.timedelta(0,0,0)
        self.begintime = None
        self.endtime = None

    def statuscheck(self):
        '''
        check whether the data and other parametes are ready for simulation
        '''
        self.ready = True

        if len(self.data) == 0:
            self.ready = False
            print 'data not ready'

    def setActiveTimeDelta(self,begintime,endtime):
        '''
        set the active time range of each day.
        simulation will begin from the begintime and finish at the endtime
        '''
        begintime = strptime(begintime)
        endtime = strptime(endtime)

        self.beginTimeDelta = dt.timedelta(hours= begintime.tm_hour,minutes = begintime.tm_min, seconds = begintime.tm_sec)
        self.endTimeDelta = dt.timedelta(hours= endtime.tm_hour,minutes = endtime.tm_min, seconds = endtime.tm_sec)

    def updateActiveTime(self,date):

        '''
        auxiliary function for updating the begin and end time of active time of the simlation
        '''

        self.begintime = date + self.beginTimeDelta
        self.endtime = date + self.endTimeDelta

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

    def setDayFreqDataList(self,namelist = []):
        '''
        Mark the data with daily or lower frequency for further processing
        namelist: list of name to be marked as day freq data
        '''
        if len(self.datalist) == 0:
            print 'Please set datalist first\n'
            return -1

        legalname = set()
        for element in self.datalist:
            set.add(element['name'])

        for name in set(namelist):
            if name in legalname:
                self.dayfreqdataliset.append(name)
            else:
                print name + ' does not belong to datalist, empty dayfreqdatalist'
                self.dayfreqdatalist = []
                break

    def emptydatalist(self):
        self.datalist = []

    def replaceData(self,date):
        '''
        replace 1 day data into simulator for dispatch
        '''
        for element in self.datalist:
            self.data[element['name']] = self.dataloader.tickerload(symbol = element['name'],source = element['source'],begindate = date)

    def processDayFreqData(self):
        '''
        adjust the time index of day freq data so that it can be sent out at the begining/ending of the active hour
        '''
        for daydata in self.dayfreqdatalist:
            self.data[daydata][:self.begintime].index = self.begintime
            self.data[daydata][self.endtime].index = self.endtime


    def dispatch(self):

        #self.combineandsort()

        while self.currentTime <= self.endtime:

            self.currentTime += self.timeunit
            print self.currentTime

    def simulate(self,begindate,enddate,begintime,endtime):

        '''
        for each day from begindate to enddate,
        load the data and dispatch it to registered strategies

        the begintime and endtime specify the range of time of each day to send out data

        if the data loaded include timestamps outside of the tima range,
        to be modified
        '''

        self.statuscheck()
        if self.ready == False:
            return -1

        for date in range(4):
            self.replaceData(date)
            self.updateActiveTime(date)
            self.processDayFreqData()
            self.dispatch()


