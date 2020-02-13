# 规范变量、函数命名方式，改了函数get_group_info的bug（重复打印开始签到）
# 增强程序的自主性，在原来基础上能够每天自动开始签到、统计
# coding:utf-8
import threading
import datetime
import itchat
import time
import json
HEALTH_STATU = '健康'
CONTACK_STATU = '接触'

cnt = 0                      #计数器统计人数
group_name = '计163的新芽们'  #群名称
group_num = ''               #群编号，通过群编号来区分不同群的消息
group_user_name = ''         #群username,用来标记群,从而确定发消息对象
member_checked = {}          #已签到成员字典

def time_stat(stuInfo):
    '''定时统计线程执行体'''
    global cnt
    while True:
        cur_time = datetime.datetime.now().strftime('%H:%M')
        if cur_time == "13:00":
            if cnt >= 32:
                continue
            groups = itchat.get_chatrooms(update=True)
            l = unchecked_stat(stuInfo)
            if '张宇' in l:
                l.remove('张宇')
            ans = "还有%d人未签到，他们分别是"%len(l)
            for i in l:
                ans += i + '  '
            print('ans     : '+ans)
            for g in groups:
                if g['NickName'] == group_name:
                    to_group = g['UserName']
                    itchat.send(ans,to_group)
                    print ("send ok!")
        elif cur_time == "6:00":
            #重新开始，清空变量
            cnt = 0
            get_group_info() #更新groupNum
            member_checked.clear()
            strSign = str(datetime.datetime.now().month)+'-'+str(datetime.datetime.now().day)+"开始签到"
            print(strSign)          #打印日期
            itchat.send(strSign,group_user_name)
            
def update_group_num():
    '''两小时更新一次group_num'''
    while True:
        get_group_info()
        time.sleep(3600*2)  

def read_file_info():
    '''从文件读取缓存json数据'''
    with open('data.json', 'r') as f:
        tmpData = json.load(f)
        return tmpData

def get_group_info():
    '''查询好友列表/群信息，获取群的username，对群成员进行分析需要用到'''
    global groupNum
    global group_user_name
    groups = itchat.get_chatrooms(update=True)
    for g in groups:
        if g['NickName'] == group_name:
            group_user_name = g['UserName']
            RoomList = {}
            groupNum = ''
            if len(g['MemberList']) == 0:
                RoomList = read_file_info()
            else:
                RoomList = g
            groupNum = g['UserName']
            print('最新的groupID:  '+groupNum)
            return RoomList

def unchecked_stat(stuInfo):
    '''统计未签到成员名单'''
    unchecked_name = []
    for usr in stuInfo:
        if usr not in member_checked:
            unchecked_name.append(usr)
    return unchecked_name
    
@itchat.msg_register([itchat.content.TEXT], isGroupChat=True)    #群消息的处理
def print_content(msg):
    '''监听群消息记录，自动回复签到情况'''
    global cnt
    if msg['FromUserName'] == groupNum or msg['ToUserName'] == groupNum:
        if msg['Text'].find(HEALTH_STATU) != -1 or msg['Text'].find(CONTACK_STATU) != -1:
            cnt += 1
            print("该群发的消息为： "+msg['Text'])     #打印哪个群给你发了什么消息
            reply = msg['ActualNickName']+'签到成功，'+"目前已成功签到%d人\n"%cnt
            if msg['ActualNickName'] in member_checked.keys():
                reply = "请勿重复签到"
            if(cnt == 32):
                reply += "\n所有人已经签到完毕，收工"
            if(cnt > 32):
                return ""
            member_checked[msg['ActualNickName']]=1
            print("回复内容为: " + reply)
            print("当前已签到成员为：")
            for i in member_checked:
                print(i,end='   ')
            print('')#换行
            return reply
    else:           
        print("不是该群消息")
        pass

def init_group_member(group_info):
    '''预处理json数据初始化'''
    stu = []
    if len(group_info) == 1:
        group_info = group_info[0]
    for person in group_info['MemberList']:
        tmp = person['DisplayName']
        if tmp != '' and tmp != '彭小萍' and tmp != '禹皓晨' and tmp.find('老师')==-1:
            stu.append(person['DisplayName'])
    if '张宇' not in stu:
        stu.append('张宇')
    print(len(stu))
    print(stu)
    return stu

def tmp_init():
    '''临时断线调整'''
    global cnt
    strs = "张宇   王含艺"
    datas = strs.split("   ")
    for n in datas:
        member_checked[n] = 1
        cnt += 1
    print('初始化结果为%d人'%cnt)
    print(member_checked)

if __name__ == '__main__':
    #tmp_init()
    print('————————————————————自动回复程序启动——————————————————')
    itchat.auto_login()
    group_json_data = get_group_info()
    stu_info = init_group_member(group_json_data)
    thr_update = threading.Thread(target=update_group_num)
    thr_remind = threading.Thread(target=time_stat,args=(stu_info,))
    thr_update.start()
    thr_remind.start()
    itchat.run()
