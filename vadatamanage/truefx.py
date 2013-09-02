import urllib
import csv
from datetime import datetime,date,time
from dateutil.relativedelta import relativedelta
import os
HOMEADDRESS="/nv/hcoc1/ryang40/data"

def GetData(url,address):
    urllib.urlretrieve(url,address)

####TrueFX Data####

def GetTrueFX_MilliQuote(dt,ticker):
    HOMEADDRESS="/nv/hcoc1/ryang40/data"
    url="https://www.truefx.com/dev/data/"+dt.strftime("%Y")+"/"+dt.strftime("%B").upper()+"-"+dt.strftime("%Y")+"/"+ticker.upper()+"-"+dt.strftime("%Y")+"-"+dt.strftime("%m")+".zip"
    address=HOMEADDRESS+"/Vdata/Milli_Quote_FX/temp/"+ticker.upper()+dt.strftime("%Y")+dt.strftime("%m")+".zip"
    GetData(url,address)
    print address

def GetTrueFX_Batch(startYear,startMonth,endYear,endMonth):
    HOMEADDRESS="/nv/hcoc1/ryang40/data"
    startDate=datetime(startYear,startMonth,1)
    endDate=datetime(endYear,endMonth,1)

    reader=csv.reader(open(HOMEADDRESS+"/Vdata/Milli_Quote_FX/Milli_Quote_FX_List.csv","rb"))
    downloadList=list(reader)
    listLength=len(downloadList)

    for i in range(0,listLength):
        ticker=downloadList[i][0]
        currentDate=startDate
        while(currentDate<=endDate):
            GetTrueFX_MilliQuote(currentDate,ticker)
            currentDate=currentDate+relativedelta(months=1)

def RemoveBadZip_TrueFx(startYear,startMonth,endYear,endMonth):

    startDate=datetime(startYear,startMonth,1)
    endDate=datetime(endYear,endMonth,1)
    reader=csv.reader(open(HOMEADDRESS+"/Vdata/Milli_Quote_FX/Milli_Quote_FX_List.csv","rb"))
    downloadList=list(reader)
    listLength=len(downloadList)
    for i in range(0,listLength):
        ticker=downloadList[i][0]
        currentDate=startDate
        while(currentDate<=endDate):
            address=HOMEADDRESS+"/Vdata/Milli_Quote_FX/temp/"+ticker.upper()+currentDate.strftime("%Y")+currentDate.strftime("%m")+".zip"
            if(os.path.isfile(address)==True):
                os.remove(address)
            currentDate=currentDate+relativedelta(months=1)


