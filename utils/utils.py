import numpy as np
import pandas as pd

import types


def formlist(element):
    '''
    form a list if input is not a list
    '''
    if type(element) is not types.TupleType and type(element) is not list:
        return [element,]
    else:
        return element
