from collections import defaultdict
import VA_PYTHON as va
import VD_KDB as vd


class featprocessor():
    '''
    hold all available operators and generate features
    '''

    def __init__(self):
        self.operations = defaultdict()
        print 'Initializing operators...'
        self.operations['hawkes'] = va.models.hawkes.hawkesfeat

    def getoperator(self,opname):
        return self.operations[opname]

    def getfeature(self,operationlist,timeseries):
        '''
        Generate a feature time series
        operations: list of dict
        operations = [
                {'name':'hawkes',
                    'par1':2},
                {'name':'normalize',
                    'par1':(1,2,3),
                    'par2':3}
                ]
        '''
        for ops in operationlist:
            opname = ops['name']
            operator = self.getoperator(opname)
            timeseries = operator(timeseries,args = ops)

        return timeseries




