# -*- coding:utf-8 _*-
#  数据导入mysql
import sqlalchemy
import pandas as pd

filename = 'data.csv'
data = pd.read_csv(filename, low_memory=False)
df = pd.DataFrame(data)
df.replace(r'\[(.*)\]', r'\1', regex=True, inplace=True)
df.replace("'", "", regex=True, inplace=True)
# 创建连接
conn = sqlalchemy.create_engine("mysql+pymysql://root:123@localhost:3306/movie")
df.to_sql(name='movies', con=conn, if_exists='append', index=False, chunksize=6000)
