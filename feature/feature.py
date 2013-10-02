import VA_PYTHON as va
import VD_KDB as vd
from collections import defaultdict
from featoperator import featprocessor

class fbase():
    '''
    fbase loads and holds all requried features for analysis
    '''

    def __init__(self):
        self.features = {} #store features
        self.featlist = list()
        self.fprocessor = featprocessor() #for generating feature
        self.dloader = vd.pyapi.dataloader() #for loading data
        self.data = defaultdict() #store data for generating feature

    def addData(self,name,command):
        self.data[name] = self.dloader(command)

    def addFeat(name,):
        '''
        load feature into fbase
        '''
        pass

