negativeRush=0
positiveRush=0
positive_fall=0
positive_rise=0
positive_flat=0
negative_fall=0
negative_rise=0
negative_flat=0


for (i in 3:length(dprice)){
  if(dprice[i-2]<0&&dprice[i-1]<0){
    negativeRush=negativeRush+1
    if(dprice[i]>0) negative_rise=negative_rise+1
    if(dprice[i]==0) negative_flat=negative_flat+1
    if(dprice[i]<0) negative_fall=negative_fall+1
  }
  if(dprice[i-2]>0&&dprice[i-1]>0){
    positiveRush=positiveRush+1
    if(dprice[i]>0) positive_rise=positive_rise+1
    if(dprice[i]==0) positive_flat=positive_flat+1
    if(dprice[i]<0) positive_fall=positive_fall+1
  } 
}

print(negative_rise/negativeRush)
print(negative_flat/negativeRush)
print(positive_fall/positiveRush)
print(positive_flat/positiveRush)
