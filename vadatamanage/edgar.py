from ftplib import FTP
import os
import urllib2
DATA_ADD = os.getenv('DATA')

def getindex(beginyear, beginqtr, endyear, endqtr):
    '''Download master file from edgar'''
    print 'login to edgar ftp'
    ftp = FTP('ftp.sec.gov')
    print ftp.login()
    for year in range(beginyear, (endyear + 1)):
        if year == endyear:
            maxqtr = endqtr + 1
        else:
            maxqtr = 5
        if year == beginyear:
            minqtr = beginqtr
        else:
            minqtr = 1
        for qtr in range(minqtr, maxqtr):
            remotefile = 'RETR /edgar/full-index/' + str(year) + \
                    '/QTR' + str(qtr) + '/master.gz'
            localfile = DATA_ADD + '/Edgar/MasterFile/' + \
                    str(year) + 'QTR' + str(qtr) + 'master.gz'
            ftp.retrbinary(remotefile, open(localfile, 'wb').write)
            print 'download '+ str(year) + 'QTR' + str(qtr) + \
                    'master.gz'
    ftp.quit()


def ticker2CIK(ticker):
    '''Given a ticker, return corresponding CIK code'''
    string_match = 'rel="alternate"'
    url = 'http://www.sec.gov/cgi-bin/browse-edgar?company=&match=&CIK=%s&owner=exclude&Find=Find+Companies&action=getcompany' % ticker
    response = urllib2.urlopen(url)
    cik = ''
    for line in response:
        if string_match in line:
            for element in line.split(';'):
                if 'CIK' in element:
                    cik = element.replace('&amp', '')
    cik = cik[4:]
    return cik


def genCIKtable():
    '''generate a txt file that map ticker to cik'''
    tickers = set()
    nysepath = DATA_ADD + '/tickerlist/20130829/nyse20130829.txt'
    nasdaqpath = DATA_ADD + '/tickerlist/20130829/nasdaq20130829.txt'
    tablepath = DATA_ADD + '/Edgar/cik2ticker.txt'

    def addticker(listpath):
        with open(listpath, 'rb') as f:
            for line in f:
                tickers.add(line.split('\t')[0])

    addticker(nysepath)
    addticker(nasdaqpath)
    with open(tablepath, 'wb') as fout:
        for ticker in tickers:
            line = ticker + ',' + ticker2CIK(ticker) + '\n'
            print line,
            fout.write(line)
    return tickers



