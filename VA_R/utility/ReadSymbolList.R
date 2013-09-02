ReadSymbolList<-function(listName,databasepath="/media/OS/Database"){
  
  #Returns ticker symbol list
  
  completeSymbolList=switch(listName,
                            "completeNYSE"=read.csv(paste(databasepath,"/NYSE_20130520.txt",sep=""),sep="\t"),
                            "Dow30"=read.csv(paste(databasepath,"/Dow30_20130520.csv",sep=""),sep="\t")
  )
  
    
  ticker=completeSymbolList[,1]
  return (list("ticker"=as.character(ticker),"completeSymbolList"=completeSymbolList));
}