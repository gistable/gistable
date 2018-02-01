#!/usr/bin/python
# -*- coding: utf-8 -*-
# utf-8 中文编码
import glob
import os,sys
import json
reload(sys)
sys.setdefaultencoding('utf-8')
import time, sys,iptc  # iptc 包通过 sudo pip install python-iptables 安装
from datetime import datetime
import csv



u"""
统计账号流量，限制每月流量。

会在 MY_LOG_DIR (/usr/local/ss-libev/flow_log/)  储存统计的流量信息，是 csv 格式 。
"""


PREFIX="/usr/local/ss-libev"

# ss-libev 配置目录
CONF_DIR='/usr/local/conf/'


# 配置目录
MY_CONF_DIR = PREFIX + '/flow/'
MY_LOG_DIR = PREFIX + '/flow_log/'
LAST_FLOW_FILE = MY_CONF_DIR + 'last_flow.json'


# 不受限制账号列表
NO_LIMIT = ['test.json','user2.json']
# 流量  1*1024*1024*1024 =1G
LIMIT_FLOW =  120 * 1024 * 1024 *1024
LIMIT_FLOW_TENMINUTES = 120 * 1024 * 1024 *1024
# 时区：上海
os.environ["TZ"] = "Asia/Shanghai"
 
file_type={
               'month_flow':"%Y-%m",
               'day_flow':"%Y-%m-%d",
               'hour_flow':"%Y-%m-%d-%H",
               'tenminutes_flow':"%Y-%m-%d-%H-%M",
               }


if not os.path.exists(MY_CONF_DIR):
    os.makedirs(MY_CONF_DIR)
if not os.path.exists(MY_LOG_DIR):
    os.makedirs(MY_LOG_DIR)



def get_account_dict():
    u"""获得账号列表"""

    files = glob.glob(os.path.join(CONF_DIR,'*.json'))

    ss_account_dict ={}

    for file_path in files:
        with open(file_path,'rb') as file:
            ss_config = json.load(file,encoding='utf8')
            ss_account_dict[os.path.basename(file_path)]=ss_config
    return ss_account_dict



def get_original_flow():
    u"""获得原始流量"""
    res={
            'flow_in':{},  # {u8001:3916788L}
            'flow_out':{},
            'status':'ok'
        }
    table = iptc.Table(iptc.Table.FILTER)

    chain_in = iptc.Chain(table, 'INPUT')
    chain_out = iptc.Chain(table, 'OUTPUT')

    table.refresh()

    for rule in chain_out.rules:
        try:
            if len(rule.matches)==1:
                sport = int(rule.matches[0].sport)
                res['flow_out'][sport] = rule.get_counters()[1]
        except Exception,inst:
            print (u'[警告]未知的 iptables 规则，如果是其他软件添加的可以忽略。')
            print(inst)
    for rule in chain_in.rules:
        try:
            if len(rule.matches)==1:
                dport = int(rule.matches[0].dport)
                res['flow_in'][dport] = rule.get_counters()[1]
        except Exception,inst:
            print (u'[警告]未知的 iptables 规则，如果是其他软件添加的可以忽略。')
            print(inst)
    return res

def get_last_flow():
    u'''获得上次的流量信息
    
    几十个用户很简单的json文件就搞定了。
{
    'last_time':最近的时间
    'account_dict':{
        用户标识:
                {
                    'port':
                    'in':
                    'out':
                }
    }
}

    '''
    if os.path.exists(LAST_FLOW_FILE):
        with open(LAST_FLOW_FILE,'rb') as file:
            return json.load(file,encoding='utf8')
    else:
        return { 'account_dict':{}}

def set_last_flow(data):
    u'''保存上次的流量信息
    
    '''
    with open(LAST_FLOW_FILE,'wb') as file:
         return json.dump(data,file,encoding='utf8')



    
def add_iptables(port):
    u""" 增加 iptables 规则"""
    os.system("iptables -I INPUT  -p tcp --dport %s" %port)
    os.system("iptables -I OUTPUT -p tcp --sport %s"%port)

def get_old_flow(_type,_time):
    u''' 获得保存的流量报表

    为了查看方便，使用 csv 格式保存，直接用 office 即可查看。
    
格式是
名称,本时段所有流量,本时段入站流量,本时段出站流量

    '''   
               
    res ={}
    t = _time.strftime(file_type[_type])
    if _type == 'tenminutes_flow':
        t = t[:-1]+'0'    
    filename = os.path.join(MY_LOG_DIR,t+'.csv')
    if os.path.exists(filename):
        with open(filename,'rb') as file:
            reader = csv.reader(file)
            for username, flow_all, flow_in, flow_out in reader:
                res[username] = [int(flow_all), int(flow_in), int(flow_out)]
    return res
    
def set_old_flow(flow_dict,_type,_time):
    t = _time.strftime(file_type[_type])
    if _type == 'tenminutes_flow':
        t = t[:-1]+'0'    
    filename = os.path.join(MY_LOG_DIR,t+'.csv')
    with open(filename,'wb') as file:
            writer = csv.writer(file)
            for username,flow in flow_dict.iteritems():
                writer.writerow((username,flow[0],flow[1],flow[2]))
    return True

    
    
def run():
    u""" 获得流量信息
    
每隔一段时间执行一次
    """
    now = datetime.now()
    account_dict = get_account_dict()
    original_flow_dict = get_original_flow()
    
    last_flow_dict = get_last_flow()
    month_flow_dict = get_old_flow('month_flow',now)
    day_flow_dict = get_old_flow('day_flow',now)
    hour_flow_dict = get_old_flow('hour_flow',now)
    tenminutes_flow_dict = get_old_flow('tenminutes_flow',now)
    
    for account_name , account in  account_dict.iteritems():
        print u'开始处理账号 %s 端口 %s' %(account_name,account['server_port'])
    
        # 本次统计新增流量
        in_flow = 0
        out_flow =0
        
        original_flow_in = original_flow_dict['flow_in'].get(account['server_port'],None)
        original_flow_out = original_flow_dict['flow_out'].get(account['server_port'],None)
        if original_flow_in == None or original_flow_out == None:
            print u'用户 %s 端口 %s 未配置 iptables 统计流量信息，开始配置 iptables 。' % (account_name,account['server_port'])
            add_iptables(account['server_port'])
            #TODO: 无流量信息处理。
            original_flow_in = 0
            original_flow_out = 0
        
        flow  = last_flow_dict['account_dict'].get(account_name,{'in':0,'out':0,'port':None})
        if original_flow_in >= flow['in'] and original_flow_out>=flow['out'] and (flow['port'] == None or flow['port'] == account['server_port'] ):
            # 仔细点，防止把删掉账号的流量算到新账号上面。
            in_flow = original_flow_in - flow['in']
            out_flow = original_flow_out - flow['out']            
        else:
            print u'[错误][流量统计] 账号 %s 端口 %s 统计流量错误，可能最近重启服务器过造成 iptables 流量记录重置了，已经纠正了错误。' % (account_name,account['server_port'])
        
        print u'用户 %s 端口 %s 上次统计，入站流量:%s 出站流量:%s 本次统计入站流量:%s 出站流量:%s 本次新增入站流量:%s 出站流量:%s ' %(account_name,account['server_port'],flow['in'],flow['out'],original_flow_in,original_flow_out,in_flow,out_flow)

        # 设置新的原始流量
        flow['in'] = original_flow_in
        flow['out'] = original_flow_out
        flow['port'] = account['server_port']
        last_flow_dict['account_dict'][account_name] = flow 
        
        month_flow = month_flow_dict.get(account_name,[0,0,0])         
        month_flow[1] += in_flow 
        month_flow[2] += out_flow 
        month_flow[0] = month_flow[1] +month_flow[2]
        month_flow_dict[account_name] = month_flow
        
        
        if month_flow[0] > LIMIT_FLOW:
            # 1024*1024*1024 = 1G
            # TODO : 停用账号
            if account_name in NO_LIMIT:
#                print u'账号 %s 端口 %s 当月已用流量 %s ，超出限制，但是属于无限制账号，不处理。'%(account_name,account['server_port'],month_flow[0])
                pass
            else:
                print u'账号 %s 端口 %s 当月已用流量 %s ，超出限制，停用账号。' %(account_name,account['server_port'],month_flow[0])
                os.system('service ss-libev stop %s'%account_name)
        
        
        day_flow = day_flow_dict.get(account_name,[0,0,0])         
        day_flow[1] += in_flow 
        day_flow[2] += out_flow 
        day_flow[0] = day_flow[1] +day_flow[2]
        day_flow_dict[account_name] = day_flow
        
        
        
        hour_flow = hour_flow_dict.get(account_name,[0,0,0])         
        hour_flow[1] += in_flow 
        hour_flow[2] += out_flow 
        hour_flow[0] = hour_flow[1] +hour_flow[2]
        hour_flow_dict[account_name] = hour_flow
        
        
        
        tenminutes_flow = tenminutes_flow_dict.get(account_name,[0,0,0])         
        tenminutes_flow[1] += in_flow 
        tenminutes_flow[2] += out_flow 
        tenminutes_flow[0] = tenminutes_flow[1] +tenminutes_flow[2]
        tenminutes_flow_dict[account_name] = tenminutes_flow

        if tenminutes_flow[0] > LIMIT_FLOW_TENMINUTES:
            # 1024*1024*1024 = 1G
            # TODO : 停用账号
            if account_name in NO_LIMIT:
#                print u'账号 %s 端口 %s 最近十分钟已用流量 %s ，超出限制，但是属于无限制账号，不处理。'%(account_name,account['server_port'],tenminutes_flow[0])
                pass
            else:
                print u'账号 %s 端口 %s 最近十分钟已用流量 %s ，超出限制，停用账号。' %(account_name,account['server_port'],tenminutes_flow[0])
                os.system('service ss-libev stop %s'%account_name)

        print u'用户 %s 端口 %s ，本月流量:%s 本天流量:%s 本小时流量:%s 十分钟流量:%s' % (account_name,account['server_port'],month_flow[0],day_flow[0],hour_flow[0],tenminutes_flow[0])
        
        
        
    set_last_flow(last_flow_dict)
    set_old_flow(month_flow_dict,'month_flow',now)
    set_old_flow(day_flow_dict,'day_flow',now)
    set_old_flow(hour_flow_dict,'hour_flow',now)
    set_old_flow(tenminutes_flow_dict,'tenminutes_flow',now)
        
        
    print u'流量统计完毕，统计信息已保存到 %s 目录' % MY_LOG_DIR
        

run()
