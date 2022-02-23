import os
import pandas as pd

df = pd.read_excel("./data/ref2014results.xlsx", skiprows=7, header=0)

df = df[df['Profile'] == 'Impact']

df = df.replace('-', 0)

df['4*'] = pd.to_numeric(df['4*'])
df['3*'] = pd.to_numeric(df['3*'])
df['2*'] = pd.to_numeric(df['2*'])
df['1*'] = pd.to_numeric(df['1*'])
df['unclassified'] = pd.to_numeric(df['unclassified'])

df['unclassified'] = df['unclassified'] / 100
df['1*'] = df['1*'] / 100
df['2*'] = df['2*'] / 100
df['3*'] = df['3*'] / 100
df['4*'] = df['4*'] / 100

df['weighted'] = (df['FTE Category A staff submitted'] * df['unclassified']) + \
                 (df['FTE Category A staff submitted'] * df['1*']) + \
                 (df['FTE Category A staff submitted'] * df['2*']) + \
                 (df['FTE Category A staff submitted'] * df['3*']) + \
                 (df['FTE Category A staff submitted'] * df['4*'])

score_df = df[['Institution name', 'Institution code (UKPRN)', 'Unit of assessment number', 'unclassified', '1*', '2*', '3*', '4*', 'weighted']]

score_df.to_csv('./data/ref_impact_results.csv', index=False)