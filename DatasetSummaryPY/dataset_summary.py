import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv('Bank_Customers.csv')

def minimum(values):
    Number = values[0]
    for n in values:
        if n < Number:
            Number = n  
    return round(Number,2)

def maximum(values):
    Number = values[0]
    for n in values:
        if n > Number:
            Number = n
    return round(Number,2)

def average(values):
    SumNum = 0
    for n in values:
        SumNum += n
    Number = SumNum/len(values)
    return round(Number,2)

def stddev(values):
    sqdifflist = []
    sumofsqdiff = 0
    mu = average(values)
    for n in values:
        diff = n - mu
        sqdiff = diff * diff
        sqdifflist.append(str(sqdiff))
    for i in sqdifflist:
        sumofsqdiff += float(i)
    beforesqroot = sumofsqdiff/len(values)
    aftersqroot = beforesqroot ** 0.5
    return round(aftersqroot,2)
   
        
ColName = []    
MinimumList = []
MaximumList = []
AverageList = []
CommonCount = []
CommonItem = []
StdDevList = []


for column in df:
    NumberOfTrue = 0
    NumericValues = []
    Values = df.loc[:,column].values.tolist()
    for i in Values:
        Checkvalue = str(i)
        Checkvalue = Checkvalue.replace(".","")
        if Checkvalue.isnumeric() == True:
            NumberOfTrue += 1
            NumericValues.append(i)
    ColName.append(column)
    MostCommon = df[column].value_counts().to_frame().reset_index().rename(columns={'index':column, column:'Count'})
    CommonCount.append(MostCommon.loc[0,'Count'])
    CommonItem.append(MostCommon.loc[0,column])
    Histogram = plt.bar(MostCommon[column],MostCommon['Count'])
    plt.title('Histogram')
    plt.xlabel(column)
    plt.ylabel('Counts')
    plt.legend([column])
    plt.show()
    if NumberOfTrue > 2 or NumberOfTrue == len(df.loc[:,column]):
        StdDevList.append(str(stddev(NumericValues)))
        if NumberOfTrue == len(df.loc[:,column]):
            MinimumList.append(str(minimum(Values)))
            MaximumList.append(str(maximum(Values)))
            AverageList.append(str(average(Values)))
    else:
        MinimumList.append("NA")
        MaximumList.append("NA")
        AverageList.append("NA")
        StdDevList.append("NA")

combineddata = list(zip(ColName, MinimumList, MaximumList, CommonItem, AverageList, StdDevList))
Summary = pd.DataFrame(combineddata, columns = ['Column Name','Minimum','Maximum','Most Common','Average','Standard Deviation'])
print(Summary)
