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

        self.initialcapital = 1000000.0

        #store symbol traded in the portfolio
        self.portfolioSymbol = set()

        self.portfolio = pd.DataFrame(
            dict(time=dt.datetime(1990,1,1),symbol='VSCHON',price=np.zeros(100000),
                 number=np.zeros(100000),direction='long',
                 open = True,
                 cash=np.zeros(100000),value=np.zeros(100000)),
            columns = ['time','symbol','price','number','direction','open','cash','value'])
        self.tradeIndex = 0


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
        set the delay time of each order mathcer (unit:millisecond)

        input: list of index in datalist
        '''

        if type(marketlist) is not types.TupleType and type(marketlist) is not list:
            marketlist = (marketlist,)

        self.marketlist = [self.datalist[i] for i in marketlist]

        #set the corresponding order matcher
        for marketdata in self.marketlist:
            self.matcherlist[marketdata['name']] = self.orderMatchLibrary.orderMatcherLoader(marketdata['source'])

    def setDelayTime(self,delayList):
        '''
        set the delay time for each mather

        input:
            ['usdjpy-3','eurusd-2']
        '''

        if type(delayList) is not types.TupleType and type(delayList) is not list:
            delayList = (delayList,)

        for element in delayList:
            [name, delay] = element.split('-')
            self.matcherlist[name].delay = int(delay)



    def matchSymbol(self,pairs):
        '''
        match the symbol sent from trader and the symbol in the market data

        input:
            symbol: list of symbol pair
                    ['ABC-0','DEF-1']
        '''
        #ipdb.set_trace()

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

    def setcapital(self,value):
        '''
        set the initial value of simulation value
        defaul to be 1 million
        '''
        self.initialcapital = value


    def setTrader(self,trader):
        '''
        set the trader for simulation
        '''
        if trader in self.traderLoader.traderlib.keys():
            self.trader = self.traderLoader.load(trader)
        else:
            print 'trader name not in trader library!'


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

    def updatePortfolio(self,trade):
        '''
        update portfolio based on new trades
        '''
        ipdb.set_trace()

        time = trade['time']
        symbol = trade['symbol']
        price = trade['price']
        direction = trade['direction']
        number = trade['number']
        open = trade['open']

        mark = 0.0
        if direction == 'long':
            mark = 1.0
        elif direction == 'short':
            mark = -1.0

        #if symbol not in portfolio, add threee cols - long,short,price
        if symbol not in self.portfolioSymbol:
            self.portfolio[symbol + '-long'] = np.zeros(100000)
            self.portfolio[symbol + '-short'] = np.zeros(100000)
            self.portfolio[symbol + '-price'] = np.zeros(100000)
            self.portfolioSymbol.add(symbol)

        if self.tradeIndex == 0:
            #special case for first trade
            #update cash
            self.portfolio['cash'][self.tradeIndex] = self.initialcapital - mark*number*price

            #update traded symbol number
            if open == True:
                if direction == 'long':
                    self.portfolio[symbol + '-long'][self.tradeIndex] = number
                elif direction == 'short':
                    self.portfolio[symbol + '-short'][self.tradeIndex] = number
            elif open == False:
                if direction == 'short':
                    self.portfolio[symbol + '-long'][self.tradeIndex] = -number
                elif direction == 'long':
                    self.portfolio[symbol + '-short'][self.tradeIndex] = -number
        else:
            #for 2nd and after trades
            #update cash
            self.portfolio.iloc[self.tradeIndex] = self.portfolio.ix[self.tradeIndex-1]
            #copy the data of last trade into current line
            self.portfolio['cash'][self.tradeIndex] = self.portfolio['cash'][self.tradeIndex-1] - mark*number*price

            #update traded symbol number
            if open == True:
                if direction == 'long':
                    self.portfolio[symbol + '-long'][self.tradeIndex] = number + self.portfolio.ix[self.tradeIndex][symbol + '-long']
                elif direction == 'short':
                    self.portfolio[symbol + '-short'][self.tradeIndex] = number + self.portfolio.ix[self.tradeIndex][symbol + '-short']
            elif open == False:
                if direction == 'short':
                    self.portfolio[symbol + '-long'][self.tradeIndex] = -number + self.portfolio.ix[self.tradeIndex][symbol + '-long']
                elif direction == 'long':
                    self.portfolio[symbol + '-short'][self.tradeIndex] = -number + self.portfolio.ix[self.tradeIndex][symbol + '-short']

        #update traded symbol price
        self.portfolio[symbol + '-price'][self.tradeIndex] = price

        #update non-traded symbol price
        #get all symbols that are not traded
        tempset = set()
        tempset.add(symbol)
        tempsym = self.portfolioSymbol.difference(tempset)

        for sym in tempsym:
            tempprice =  self.matcherlist[sym].singleprice(time,sym,self.market[sym])
            self.portfolio[sym + '-price'][self.tradeIndex] = tempprice

        #update portfolio value
        sum = 0.0
        for sym in self.portfolioSymbol:
            symnumber = self.portfolio[sym + '-long'][self.tradeIndex] - self.portfolio[sym + '-short'][self.tradeIndex]
            sum += symnumber * self.portfolio[sym + '-price'][self.tradeIndex]
        self.portfolio['value'][self.tradeIndex] = sum + self.portfolio['cash'][self.tradeIndex]

        #update transaction time, symbol,price, number, direction and open
        self.portfolio['time'][self.tradeIndex] = time
        self.portfolio['symbol'][self.tradeIndex] = symbol
        self.portfolio['price'][self.tradeIndex] = price
        self.portfolio['number'][self.tradeIndex] = number
        self.portfolio['direction'][self.tradeIndex] = direction
        self.portfolio['open'][self.tradeIndex] = open

        self.tradeIndex += 1


    def OrderProcessor(self, order):

        '''
        callback function to receive order from trader
        '''
        ipdb.set_trace()

        #translate order symbol into market symbol
        order['symbol'] = self.symbolpair[order['symbol']]

        temp = order['symbol']

        #match trade
        trade =  self.matcherlist[temp].match(order,self.market[temp])

        if trade != 'NA':
            self.updatePortfolio(trade)


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

    #5. set delay time for each order matcher
    sim.setDelayTime(('usdjpy-2','eurusd-2'))

    #6. match trade symbol and market symbol
    sim.matchSymbol(['usdjpy-0','eurusd-1'])

    #7. set cycles
    sim.setCycle('2013.08.01','03:00:00','2013.08.31','10:00:00')

    #8. config portfolio
    sim.setcapital(1000000.0)

    #9. set traders
    hawkesTrader = va.strategy.hawkes.newhawkes.hawkesTrader()
    #9.1 set trader name
    hawkesTrader.setname('hawkes_trader')
    hawkesTrader.setsimtimer('2013.08.01 02:59:00')
    #sim.setTrader('hawkes')

    #5. check status
    #sim.statuscheck()

    #6. example strategy
    trader = va.strategy.hawkes.hawkes.hawkesTrader()
    trader.setMode('sim','forexquote')
    trader.setthreshold(3)
    sim.subscribe(hooks = [trader.filter,])

    sim.simulate()

