from fredapi import Fred
import pandas as pd
import openpyxl
import requests
import numpy as np

api = ''
url = 'https://fred.stlouisfed.org/graph/fredgraph.xls?&id=KORCPIALLMINMEI'

cpi_code = 'KORCPIALLMINMEI'
export_code = 'XTEXVA01KRM667N'

def zscore(x, window):
    r = x.rolling(window=window)
    m = r.mean().shift(12)
    s = r.std(ddof=0).shift(12)
    z = (x-m)/s
    return z

def get_zscore_df(datacode) :
    response = requests.get('https://fred.stlouisfed.org/graph/fredgraph.xls?&id={datacode}'.format(datacode=datacode))
    df = pd.read_excel(response.content)
    df= df[10:len(df)].reset_index(drop=True)
    df.columns = ['일자', 'tgt']
    df['YoY'] = (df['tgt'] / df['tgt'].shift(12)).fillna(0)
    df['Zscore'] = ''
    df['Zscore'] = zscore(df['YoY'], 48)
    return df

# df.to_excel('C:/Users/ysj/Desktop/ssasaas.xlsx')

df_cpi = get_zscore_df(cpi_code).dropna().reset_index(drop=True).rename(columns = {'Zscore' : 'CPI_Z'})
df_xport = get_zscore_df(export_code).dropna().reset_index(drop=True).rename(columns = {'Zscore' : 'XPORT_Z'})


df_condition = pd.merge(df_cpi[['일자','CPI_Z']],df_xport[['일자','XPORT_Z']], on = '일자', how = 'inner')
df_condition['con'] = np.where((df_condition['CPI_Z']>0)&(df_condition['XPORT_Z']>0),"Expansion",np.where((df_condition['CPI_Z']>0)&(df_condition['XPORT_Z']<0),"Slowdown",np.where((df_condition['CPI_Z']<0)&(df_condition['XPORT_Z']>0),"Recovery","Contraction")))


df_condition.to_excel('C:/Users/ysj/Desktop/sss.xlsx')