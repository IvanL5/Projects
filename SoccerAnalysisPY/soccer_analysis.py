
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# Loading the Data
print("\n*Loading the Data*")

df = pd.read_csv('Data.csv')

print("\nData Shape:", df.shape)

#Set Display Options
pd.options.display.max_rows = 660
pd.options.display.max_columns = 15

print("\n*Head of Data*\n\n", df.head())

print("\n*Tail of Data*\n\n", df.tail())

print("\n*Summary of Data*\n\n",df.describe())

print("\nHighest Occuring Values in each Column\n", df.mode())

print("\nFrequency of Highest Occuring Value in each Column\n",pd.concat([df.eq(x) for _, x in df.mode().iterrows()]).sum())

# Data Cleaning
print("\n*Data Cleaning*")

print("\nCheck for Missing Values\n\n")
print(df.info(),"\n")

print("Check for Duplicates in Dataset:")
duplicate = 0
for result in df.duplicated():
    if result:
        duplicate += 1
if duplicate != 0:
    print('There are duplicated cells in the dataset.')
else:
    print('There are no duplicates in the dataset')

# Reformatting the dataset 

#Keep only records where Country is England, Brazil, Italy, Germany or Spain (only the most and equally represented countries)
England = df.loc[df['Country'] == 'England']
Brazil = df.loc[df['Country'] == 'Brazil']
Italy = df.loc[df['Country'] == 'Italy']
Germany = df.loc[df['Country'] == 'Germany']
Spain = df.loc[df['Country'] == 'Spain']

#Merge records from selected countries
New_Data = pd.concat([England, Brazil, Germany, Spain, Italy])
New_Data = New_Data.reset_index(drop=True)
df = New_Data


# Removing White space
df.rename(columns={'Player Names': 'Player_Names'}, inplace=True)
pd.unique(df.Player_Names)

# Replace incorect names in League column (Brazilian League spelling correction)
import re
df = df.replace(regex = r'^Campeonato.*', value='Campeonato Brasileiro Serie A' )
df.loc[df.Country == 'Brazil']

# Analysis Questions

##### 1. Is there any correlation between the number of goal scored and the precision of the players' shot?

#Precision Calculation
df['Precision'] = df['OnTarget']/df['Shots']

#Graphing
m,b = np.polyfit(df['Precision'],df['Goals'],1)
plt.scatter(df['Precision'],df['Goals'],c='g')
plt.plot(df['Precision'], m*df['Precision']+b, c='y')
plt.title('1.Correlation between precision and goals')
plt.xlabel('Precision of shoot')
plt.ylabel('# of goals scored in a season')
plt.show()

##### 2. How many goals would a player score on average during a year given their expected goals?

#Graphing
m,b = np.polyfit(df['xG'],df['Goals'],1)
plt.scatter(df['xG'],df['Goals'],c='b')
plt.plot(df['xG'], m*df['xG']+b, c='k')
plt.title('2.Correlation between expected goals and goals scored')
plt.xlabel('# of goals scored in a season')
plt.ylabel('# of goals expected')
plt.show()

##### 3. Will more shots in a match lead to scoring more goals?

#Graphing
m,b = np.polyfit(df['Shots Per Avg Match'],df['Goals'],1)
plt.scatter(df['Shots Per Avg Match'],df['Goals'],c='b')
plt.plot(df['Shots Per Avg Match'], m*df['Shots Per Avg Match']+b, c='k')
plt.title('3.Correlation between Shots Per Avg Match and goals scored')
plt.xlabel('# of goals scored in a season')
plt.ylabel('# of Shots Per Avg Match')
plt.show()
