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

        #record the time within each day
        self.currentTime = dt.datetime.now()
        self.beginTimeDelta = dt.timedelta(0,0,0)
        self.endTimeDelta = dt.timedelta(0,0,0)
        self.begintime = None
        self.endtime = None

        #The date range for simulation
        self.begindatetime = None
        self.enddatetime = None

        #Data handler to disptach data
        self.sender = Sender()

    def statuscheck(self):
        '''
        check whether the data and other parametes are ready for simulation
        '''
        self.ready = True

        if len(self.datalist) == 0:
            self.ready = False
            print 'Data list  not specified'
        elif self.begindatetime == None or self.enddatetime == None:
            self.ready = False
            print 'Simulation date range not set'
        else:
            print self.datalist
            print 'Simulation starts on ' + self.begindatetime.strftime('%Y.%m.%d %H:%M:%S') + ' to ' + self.enddatetime.strftime('%Y.%m.%d %H:%M:%S')
            print 'initialization successful'

    def setActiveTimeDelta(self,begintime,endtime):
        '''
        set the active time range of each day.
        simulation will begin from the begintime and finish at the endtime
        begintime,endtime are string
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
            legalname.add(element['name'])

        for name in set(namelist):
            if name in legalname:
                self.dayfreqdataliset.append(name)
            else:
                print name + ' does not belong to datalist, empty dayfreqdatalist'
                self.dayfreqdatalist = []
                break

    def setdaterange(self,begindatetime,enddatetime):
        '''
        the begindatetime and enddatetime specify the range of time of each day to send out data
        if only date given for begindatetime and enddatetime,
        the defaul start and end time would be 00:00:00 on the specified data
        '''
        self.begindatetime = parse(begindatetime)
        self.enddatetime = parse(enddatetime)

    def emptydatalist(self):
        self.datalist = []

    def replaceData(self,date):
        '''
        replace 1 day data into simulator for dispatch
        if input date in a datetime instance, it should be converted to string
        '''
        if isinstance(date,dt.datetime):
            date = date.strftime("%Y.%m.%d")

        for element in self.datalist:
            self.data[element['name']] = self.dataloader.tickerload(symbol = element['name'],source = element['source'],begindate = date)

    def processDayFreqData(self):
        '''
        adjust the time index of day freq data so that it can be sent out at the begining/ending of the active hour
        '''
        for daydata in self.dayfreqdatalist:
            self.data[daydata][:self.begintime].index = self.begintime
            self.data[daydata][self.endtime].index = self.endtime

    def subscribe(self,hooks = []):
        '''
        hook is the list of listen method of listeners
        Sender will call the hook method to send out message
        '''

        if len(hooks) != 0:
            for hook in hooks:
                self.sender.register(hook)


    def broadcast(self):

        while self.currentTime <= self.endtime:
            for data in self.data:
                slice = data[self.currentTime]
                for i,row in slice:
                    self.sender.dispatch(msg = row)

            self.currentTime += self.timeunit
            print self.currentTime

    def simulate(self):

        '''
        for each day from begindate to enddate,
        load the data and dispatch it to registered strategies
        if the data loaded include timestamps outside of the tima range,
        to be modified
        '''

        self.statuscheck()
        if self.ready == False:
            return -1

        daterange = [rrule.rrule(rrule.DAILY,dtstart = self.begindatetime,until = self.enddatetime)]

        for date in daterange:
            self.replaceData(date)
            self.updateActiveTime(date)
            self.processDayFreqData()
            self.dispatch()


if __name__ == '__main__':
    print 'demonstrating event system'

    sim = simulator()

    ####Initialization####

    #1. set data list
    sim.setdatalist(('forex_quote-usdjpy',))

    #2. set day frequency data
    sim.setDayFreqDataList()

    #3. set simulation date range
    sim.setdaterange('2013.08.01','2013.08.03')

    #3. check status
    sim.statuscheck()

    #3. example strategy
