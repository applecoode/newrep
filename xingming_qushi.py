#coding = 'utf-8'
import pandas.io.sql as sql
from sqlalchemy import create_engine
#import os
import pandas as pd
db=create_engine('aaaaaa')
conn = db.connect()
names1=sql.read_sql("select substr(xm,3,5),xb,csrq,count(*) from dzrkxt.czrk_jbxx b where substr(b.xm,0,2) in  \
                    (select xing from dzsjhz.ls_xing c where c.flag = '2') group by substr(xm,3,5),xb,csrq", \
                    conn,columns=['name','sex','year','birth'])

names2=sql.read_sql("select substr(xm,2,5),xb,csrq,count(*) from dzrkxt.czrk_jbxx b where substr(b.xm,0,2) not in  \
                    (select xing from dzsjhz.ls_xing c where c.flag = '2') and b.gmsfhm not in (select gmsfhm from dzrkxt.zb_xmlpz )  \
                    group by substr(xm,2,5),xb,csrq", \
                    conn,columns=['name','sex','year','birth'])#只能先把冷僻字过滤掉
conn.close()

names1.columns = ['name','sex','year','birth']
names2.columns = ['name','sex','year','birth']
names=pd.concat([names1,names2],ignore_index=True)#合并
def add_prop(group):
    birth = group.birth.astype(float)
    group['prop']=birth/birth.sum()
    return group
names['year']=names['year'].map(lambda x:str(x)[:4])
names=names.groupby(['year','sex']).apply(add_prop)
total_birthsqs = names.pivot_table('birth',index='year',columns='name',aggfunc=sum)
total_birthsqs.to_pickle('file/xingming_qushi.pkl')