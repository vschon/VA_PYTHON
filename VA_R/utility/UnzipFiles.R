for(i in c(15:30))
{
  
  frompath=paste("/media/OS/Database/TAQdata_trade/",tolower(a$ticker[i]),"_2010_12.zip",sep="")
  topath=paste("/media/OS/Database/TAQdata_trade/",a$ticker[i],sep="")
  unzip(zipfile=frompath,exdir=topath)
}