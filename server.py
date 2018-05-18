import pandas as pd
from pyecharts import Bar,Line
from flask import Flask, render_template,session,redirect,url_for,flash
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField,StringField
from wtforms.validators import data_required,Regexp
from flask_bootstrap import Bootstrap
#from flask_moment import Moment


app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
app.config['DEBUG'] = True
bootstrap = Bootstrap(app)
#moment = Moment(app)
REMOTE_HOST = "static/js"

#提取数据相关函数，不知道哪里放？
def get_data():
    rkzxct=pd.read_pickle('file/rkzxct.pkl')
    rkzx_pivot_zxsj_xjcopy=pd.read_pickle('file/rkzx_pivot_zxsj_xjcopy.pkl')
    with open('file/c_time.txt','r') as f:
    	c_timestr=f.read()
    return rkzxct,rkzx_pivot_zxsj_xjcopy,c_timestr

def raise_data(ssxq):
    if ssxq=='山东省德州市':
        index = [i for i in zxrk_group_ssxq.sort_values(['zt','zxsj'],ascending=False).index]
        total = [i for i in zxrk_group_ssxq.sort_values(['zt','zxsj'],ascending=False).iloc[:,0].values]
        finish = [i for i in zxrk_group_ssxq.sort_values(['zt','zxsj'],ascending=False).iloc[:,1].values]
    else:
        zxrk_zl=rkzxct.loc[ssxq].sort_values(['zt','zxsj'],ascending=False)
        index = [i for i in zxrk_zl.index]
        total = [i for i in zxrk_zl.iloc[:,0].values]
        finish = [i for i in zxrk_zl.iloc[:,1].values]
    return index,total,finish

rkzxct_ls=get_data()[0]
zxrk_group_ssxq_ls=rkzxct_ls.groupby(level=0).sum()    

#定义表单
class NameForm(FlaskForm):
    choices = [(i,i) for i in zxrk_group_ssxq_ls.index]
    choices.append(('山东省德州市','山东省德州市'))
    name = SelectField('选择县市区',choices=choices)
    submit = SubmitField('绘制所选县市图形')
    
class NamestrForm(FlaskForm):
    name1 = StringField('请输入名字，不含姓氏',validators=[data_required(),Regexp('^[\u4e00-\u9fa5]{0,4}$',message='请输入1到4个汉字')])
    name2 = StringField('请输入进行比较的名字，不含姓氏',validators=[Regexp('^[\u4e00-\u9fa5]{0,4}$',message='请输入1到4个汉字')])
    submit = SubmitField('确认')

    
#定义pyecharts函数
def bar(ssxq):
    index = raise_data(ssxq)[0]    
    total = raise_data(ssxq)[1]
    finish = raise_data(ssxq)[2]
    bar = Bar(ssxq+'应销未销人员完成数','数据生成时间:'+c_timestr,width = 900,height = 450)
    bar.add('总数',index,total,xaxis_rotate = 20,is_xaxislabel_align = True,xaxis_interval=0,is_more_utils = True)
    bar.add('完成数',index,finish,xaxis_rotate = 20,is_xaxislabel_align = True,mark_point=['min'],xaxis_interval=0,is_more_utils = True)
    return bar
    
def line():
    line = Line('任务完成曲线','数据生成时间:'+c_timestr,width = 900,height = 450)
    lineindex = [m for m in rkzx_pivot_zxsj_xjcopy.index]
    for j in rkzx_pivot_zxsj_xjcopy.columns:
        linecolumn = [i*100 for i in rkzx_pivot_zxsj_xjcopy[j]]
        line.add(j,lineindex,linecolumn,xaxis_name='日期',yaxis_name='完成任务百分比',yaxis_name_pos='middle',legend_orient='vertical',legend_pos='right',is_toolbox_show=1)
    return line

def mingzi_qushi(str,str2=None):
    line3 = Line('命名趋势')
    x = [i for i in total_birthsqs.index]
    if str and str in total_birthsqs.columns:#如果不在字典的列中，会报错
        y = [i for i in total_birthsqs[str]]
        line3.add(str,x,y)
    if str2 and str2 in total_birthsqs.columns:
        y2 = [i for i in total_birthsqs[str2]]
        line3.add(str2,x,y2)
    return line3    

    
#定义路由
@app.route("/", methods=['GET', 'POST'])
def hello():
    global rkzxct,rkzx_pivot_zxsj_xjcopy,c_timestr,zxrk_group_ssxq
    rkzxct,rkzx_pivot_zxsj_xjcopy,c_timestr=get_data()
    zxrk_group_ssxq=rkzxct.groupby(level=0).sum()
    form = NameForm()
    if session.get('ssxq'):
        ssxq = session.get('ssxq')
    else:
        ssxq = '山东省德州市'
        session['ssxq'] = '山东省德州市'
    if form.validate_on_submit():
        session['ssxq'] = form.name.data #这里有点问题，form.name.data = session['ssxq']这句放在前面执行好像选取就不起作用
        return redirect(url_for('hello'))
    b = bar(ssxq)
    l = line()
    form.name.data = session['ssxq']
    return render_template('pyecharts.html',
                           myechart=b.render_embed(),
                           myechart2=l.render_embed(),
                           host=REMOTE_HOST,
                           script_list=b.get_js_dependencies()+l.get_js_dependencies(),
                           form = form)

@app.route("/xingming", methods=['GET', 'POST'])
def xingming():
    global total_birthsqs
    total_birthsqs=pd.read_pickle('file/xingming_qushi.pkl')
    form = NamestrForm()
    if form.validate_on_submit():
        session['str'] = form.name1.data
        session['str2'] = form.name2.data
        return redirect(url_for('xingming'))
    if session.get('str'):
        str = session['str']
    else:
        str = None
    if session.get('str2'):
        str2 = session['str2']
    else:
        str2 = None
    if str and str not in total_birthsqs.columns:
        flash('名字是%s的人很少'%str)
    if str2 and str2 not in total_birthsqs.columns:
        flash('名字是%s的人很少'%str2)
    l3 = mingzi_qushi(str,str2)
    if session.get('str'):
        form.name1.data = session['str']
    if session.get('str2'):
        form.name2.data = session['str2']
    return render_template('xingming.html',
                       myechart=l3.render_embed(),
                       host=REMOTE_HOST,
                       script_list=l3.get_js_dependencies(),
                       form = form)

