

import pandas as pd
import numpy as np

df=pd.DataFrame({})
l=1
for i in range(5):
    for j in range(5):
        df.loc[i,j]=l
        l+=1
        
print(df.iloc[[1,2,3],[1,2,3]])
df.drop([0,4,1],inplace=True)
df.drop([0,1,4],axis=1,inplace=True)
print(df)
