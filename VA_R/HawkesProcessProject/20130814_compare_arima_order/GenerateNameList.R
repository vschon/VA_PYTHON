#compare 5 step ahead performance
namelist=c()
i=1
for(arorder in 8:8){
    for(maorder in 6:6){
        for(step in 1:5){
        filename=paste('ARIMA',arorder,maorder,step,'.txt',sep='')
        if(file.exists(filename)==TRUE){
             namelist[i]=filename
        i=i+1
        }
        }
    }
}
print(i)
write.table(namelist,'arma86_file.csv',row.names=FALSE,col.names=FALSE,sep=',')
            
        
