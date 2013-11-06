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

class simDataLoader():

    def __init__(self):
        self.conn = vd.pyapi.kdblogin()

    def load(self,command):
        '''
        the base function
        load data from kdb into pd time series
        '''

        result = vd.pyapi.qtable2df(self.conn.k(command))
        if 'time' in result.columns:
            result.index = result['time']

        return result

    def tickerload(self,source,symbol,begindate,enddate = None):
        '''
        load data as df
        '''

        if enddate == None:
            enddate = begindate

        daterange = '(' + begindate + ';' + enddate + ')'

        if source != symbol:
            command = 'select from ' + source + ' where date within ' + \
                    daterange + ',symbol=`' + symbol.upper()
        else:
            command = 'select from ' + source + ' where date within ' +  daterange

        return self.load(command)


def generateSimOrder(id,time,direction,open,
                     symbol,orderType,number,
                     limit_price=0):
    '''
    id:             order ID
    time:           dt.datetime
    direction:      'long'/'short'
    symbol:         string
    open:           True/False
    orderType:      'MARKET'/'LIMIT'
    number:         int
    limit_price:    float
    '''
    return {'orderID':      id,
            'time':         time,
            'direction':    direction,
            'open':         open,
            'symbol':       symbol,
            'type':         orderType,
            'number':       number,
            'limit_price':  limit_price}


class simulator():

    def __init__(self):

        #used to load data from kdb
        self.dataloader = simDataLoader()

        #used to get the order matcher from order matcher library
        self.orderMatchLibrary = va.simulator.ordermatcher.orderMatcherLibrary()

        #hdb: holds data from different datasource in df type
        #hdb = {'name':data,'name':data}
        self.hdb = defaultdict()

        #IMDB is the in memory database to be sent to trader
        self.IMDB = defaultdict()

        #market: hold data in pd dataframe type, used for transaction matching
        self.market = defaultdict()

        #Store HDB data list
        self.datalist = []

        #Store market data list
        self.marketlist = []

        #store the match between trader symbol and market symbol
        #key:symbol value:int - index of market data
        self.symbolpair = defaultdict()

        #store the order matcher for each market data
        self.matcherlist = defaultdict()

        #testing cycle config
        self.cycleBeginDate = None
        self.cycleEndDate = None
        self.cycleBeginTimeDelta = None
        self.cycleEndTimeDelta = None

        #if the each cycle go through time 00:00:00
        self.crossMidNight = False

        #cycles: store the begin and end datetime of each cycle
        #cycles = [cycle1,cycle2,...]
        self.cycles = []

        self.traderLoader = va.strategy.tradermanage.TraderLoader()
        self.trader = None

        self.portfolioManager = None
        self.portfolio = None


    def setdatalist(self, datalist):
        '''
        fill datalist in a convenient way

        input:
            datalist: tuple of ('forex_quote-usdjpy','source-symbol')

        output:
            list of dict
            self.datalist:[{'name':symbol,'source':source},...]
        '''

        if type(datalist) is not types.TupleType and type(datalist) is not list:
            datalist = (datalist, )

        for SourceSymbol in datalist:
            try:
                [source, symbol] = SourceSymbol.split('-')
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

    def setMarketList(self,marketlist):
        '''
        choose the data used for transaction matching
        set the order matched based on market data source

        input: list of index in datalist
        '''

        if type(marketlist) is not types.TupleType and type(marketlist) is not list:
            marketlist = (marketlist,)

        self.marketlist = [self.datalist[i] for i in marketlist]

        #set the corresponding order matcher
        for marketdata in self.marketlist:
            self.matcherlist[marketdata['name']] = self.orderMatchLibrary.orderMatcherLoader(marketdata['source'])




    def matchSymbol(self,pairs):
        '''
        match the symbol sent from trader and the symbol in the market data

        input:
            symbol: list of symbol pair
                    ['ABC-0','DEF-1']
        '''

        if type(pairs) is not types.TupleType and type(pairs) is not list:
            pairs = (pairs,)
        for pair in pairs:
            [symbol,index] = pair.split('-')
            self.symbolpair[symbol] = self.datalist[int(index)]['name']


    def setCycle(self, begindate, begintime, enddate, endtime):
        '''
        parse the begin datetime and end datetime
        generate self.cycle based on input
        '''

        begintime = strptime(begintime, '%H:%M:%S')
        endtime = strptime(endtime, '%H:%M:%S')

        OneDayDelta = dt.timedelta(0)


        if endtime > begintime:
            self.crossMidNight = False
        elif endtime < begintime:
            self.crossMidNight = True
            OneDayDelta = dt.timedelta(1)
        else:
            #begintime = endtime not allowed
            print 'begintime cannot be the same as endtime'

        self.cycleBeginTimeDelta = dt.timedelta(hours= begintime.tm_hour,minutes = begintime.tm_min, seconds = begintime.tm_sec)
        self.cycleEndTimeDelta = dt.timedelta(hours= endtime.tm_hour,minutes = endtime.tm_min, seconds = endtime.tm_sec)
        self.cycleBeginDate = parse(begindate)
        self.cycleEndDate = parse(enddate)

        beginDateRange = list(rrule.rrule(rrule.DAILY, dtstart = self.cycleBeginDate, until = self.cycleEndDate))

        for beginDate in beginDateRange:
            element = {'beginDate':beginDate,
                       'endDate':beginDate + OneDayDelta,
                       'beginTime':beginDate + self.cycleBeginTimeDelta,
                       'endTime':beginDate + OneDayDelta + self.cycleEndTimeDelta}
            self.cycles.append(element)

        #Initializing


    def replaceData(self,cycle):

        '''
        replace 1 cycle data into simulator for dispatch
        '''

        #updating hdb and imdb
        for element in self.datalist:
            beginDate = cycle['beginDate'].strftime('%Y.%m.%d')
            endDate = cycle['endDate'].strftime('%Y.%m.%d')

            temp = self.dataloader.tickerload(symbol= element['name'], source = element['source'],begindate = beginDate, enddate = endDate)
            temp = temp[cycle['beginTime']:cycle['endTime']]

            self.hdb[element['name']] = temp
            #transfer into list of tuples
            self.IMDB[element['name']] = list(temp.itertuples())

        #updating market data
        for element in self.marketlist:
            self.market[element['name']] = self.hdb[element['name']]

    def setTrader(self,trader):
        '''
        set the trader for simulation
        '''
        if trader in self.traderLoader.traderlib.keys():
            self.trader = self.traderLoader.load(trader)
        else:
            print 'trader name not in trader library!'

    def OrderProcessor(self, order):

        '''
        callback function to receive order from trader
        '''

        #translate order symbol into market symbol
        order['symbol'] = self.symbolpair[order['symbol']]

        temp = order['symbol']

        #match trade
        trade =  self.matcherlist[temp].match(order,self.market[temp])



    def simulate(self):

        '''
        for each day from begindate to enddate,
        load the data and dispatch it to registered strategies
        if the data loaded include timestamps outside of the tima range,
        to be modified
        '''

        #self.statuscheck()
        #if self.ready == False:
        #    return -1

        for cycle in self.cycles:
            '''
            simulate for each cycle in cycles
            '''

            #load new data into simulator
            self.replaceData(cycle)

            #set active time, include detailed date for active time
            #self.updateActiveTime(date)

            #process lower frequency data for simulation
            #self.processDayFreqData()

            #send out messages
            #self.broadcast()

if __name__ == '__main__':
    print 'demonstrating event system'

    #1. create simulator
    sim = simulator()

    ####Initialization####

    #2. set data list
    sim.setdatalist(('forex_quote-usdjpy','forex_quote-eurusd'))

    #3. set market list
    #4. set order matcher for each market data
    #set the 1,2 element in datalist as market list
    sim.setMarketList((0,1))

    #5. Set order matcher for each market data
    sim.matchSymbol('usdjpy-0','uerusd-1')

    #4. set cycles
    sim.setCycle('2013.08.01','18:00:00','2013.08.31','02:00:00')

    #3. set traders
    sim.setTrader('hawkes')

    #5. check status
    #sim.statuscheck()

    #6. example strategy
    trader = va.strategy.hawkes.hawkes.hawkesTrader()
    trader.setMode('sim','forexquote')
    trader.setthreshold(3)
    sim.subscribe(hooks = [trader.filter,])

    sim.simulate()

