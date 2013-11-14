import VA_PYTHON as va
import VD_KDB as vd
import ipdb

def demo():
    print 'demonstrating event system'

    #1. create simulator
    sim = va.simulator.simulator.simulator()

    ####Initialization####

    #2. set data list
    sim.setdatalist(('forex_quote-usdjpy','forex_quote-eurusd'))

    #3. set market list
    #set the first 2 element in datalist as market list
    sim.setMarketList(2)

    #4. set order matcher for each market data
    sim.setOrderMatcher(['forex_quote','forex_quote'])

    #5. set delay time for each order matcher
    sim.setDelayTime((2000,2000))

    #6. match trade symbol and market data index
    sim.matchSymbol(['usdjpy-0','eurusd-1'])

    #7. set cycles
    sim.setCycle('2013.08.01','18:00:00','2013.08.05','05:00:00')
    ####CHECK CYCLE AND REPLACE DATA

    #8. set daily stop time delta(in seconds)
    sim.setDailyStopDelta(300)

    #9. set sim timer increment (in microseconds)
    sim.setSimTimerIncrement(500)


    parameters = {'theta':[0.5,0.5,0.1,0.6,0.6,0.1,1.0,1.0],
                  'number':100,
                  'k':3,
                  'exitdelta':5}

    sim.setTraderParams(parameters)

    #9. config portfolio
    sim.setcapital(1000000.0)

    #10. set trader
    sim.setTrader('hawkes')

    #10.1 set trader name
    sim.trader.setname('brandon')

    #10.2 set symbol list
    #the index of each symbol corresponds to the symbol index used by the trader
    sim.trader.setsymbols(['usdjpy','eurusd'])

    #set trader sender
    sim.trader.setsender([sim.simOrderProcessor,sim.simOrderProcessor])

    #set filter
    sim.trader.setfilter(['forex_quote-single_price','forex_quote-single_price'])

    return sim

