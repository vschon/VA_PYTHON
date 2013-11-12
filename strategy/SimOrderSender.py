import numpy as np
import pandas as pd
import VA_PYTHON as va
import VD_KDB as vd
import datetime as dt
import types


class SimOrderSender(object):
    '''
    base class of simulation sender of traders
    please override SendOrder function
    '''

    def __init__(self):
        self.idcounter = 0
        self.time = None
        self.trader = None
        self.simualtor = None

    def linkTrader(self,trader):
        self.trader = trader

    def linkSimulator(self,simulator):
        self.simualtor = simulator

    def SendOrder(self):
        '''
        to be overriden by sub-class
        '''
        pass

