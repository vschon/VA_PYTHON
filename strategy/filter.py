import numpy as np
import pandas as pd
import VA_PYTHON as va
import VD_KDB as vd
import datetime as dt
from collections import defaultdict

import ipdb

class filter(object):
    '''
    virtual class to fetch date from database
    '''

    def __init__(self):
        pass

        #establish connection with database
        self.conn = vd.pyapi.kdblogin()

    def fetch():
        '''
        fetch data from database
        '''
        pass

