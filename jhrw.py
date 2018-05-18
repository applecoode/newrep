import pandas.io.sql as sql
from sqlalchemy import create_engine
#import os
import pandas as pd
from datetime import datetime

#os.environ['NLS_LANG']='CHINESE' #字符集问题 头疼

db=create_engine('baabaasba')
conn = db.connect()

#应销未销人员任务完成监管
rkzx_sy=sql.read_sql("select * from dzrkxt.zb_yxwxry where zxsj is null",conn)
rkzx_sy.to_excel('static\最新应销未销人员完成情况.xls') #pandas导出成excel
rkzx=sql.read_sql("select * from dzrkxt.zb_yxwxry",conn)
#rkzx.to_json('rkzx.json') #导入导出模块
rkzx_groupby = rkzx.groupby(['fxj','pcs']).count() #导出带二级索引的dataform就出错，头疼
rkzxct=rkzx_groupby[['zt','zxsj']]
rkzxct.to_pickle('file/rkzxct.pkl')#改用序列化格式

#应销未销人员任务完成概览
rkzx['zxsj']=rkzx['zxsj'].map(lambda x:str(x)[:8])#控制时间的精度在小时级别
rkzx.loc[rkzx['zxsj']<'20180426','zxsj'] = '20180426'
#rkzx[rkzx['zxsj']<'20180426']['zxsj'] = '20180426' 理解要避免链式赋值
rkzx_group_zxsj=rkzx.groupby(['zxsj','fxj','pcs']).count()
rkzx_pivot_zxsj=rkzx_group_zxsj.pivot_table(values='zt',columns='zxsj',index=['fxj','pcs'],aggfunc=sum)
rkzx_pivot_zxsj_xj=rkzx_pivot_zxsj.groupby(level=0).sum()
rkzx_pivot_zxsj_xj=rkzx_pivot_zxsj_xj.T
rkzx_pivot_zxsj_xjcopy = rkzx_pivot_zxsj_xj.copy()
for j in range(len(rkzx_pivot_zxsj_xj.index)):
        for i in range(len(rkzx_pivot_zxsj_xj.columns)):
            rkzx_pivot_zxsj_xjcopy.iloc[j,i] = rkzx_pivot_zxsj_xj.iloc[rkzx_pivot_zxsj_xj.index<=rkzx_pivot_zxsj_xj.index[j],i].sum()/rkzx_pivot_zxsj_xj.iloc[:,i].sum()
rkzx_pivot_zxsj_xjcopy.to_pickle('file/rkzx_pivot_zxsj_xjcopy.pkl')
conn.close()

#时间            
c_time=datetime.now()
c_timestr=c_time.strftime('%Y-%m-%d %H:%M')
with open('file/c_time.txt','w') as f:
	f.write(c_timestr)
