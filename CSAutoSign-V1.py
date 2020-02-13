# coding:utf-8
import threading
import datetime
import itchat
import time
import json
import sys
import os
cnt = 0 #计数器统计人数
ans = ''
flag = 0
name = '计163的新芽们'
avoidRepeatDic = {} #已签到成员字典
groupNum = '@@8fd619a7d4ab99a2c0d46e6d2f2e8a4abbc7f2cdd0534ee84e1fdb79e031ebe2'     #计163的新芽们 --new

# 定义一个普通的action函数，该函数准备作为线程执行体
def action(stuInfo):
    global flag
    while True:
        if datetime.datetime.now().strftime('%H:%M')=="13:00":
            if cnt == 32:
                os._exit(0)
            groups = itchat.get_chatrooms(update=True)
            l = statistic(stuInfo)
            if '张宇' in l:
                l.remove('张宇')
            ans = "还有%d人未签到，他们分别是"%len(l)
            for i in l:
                ans += i + '  '
            print('ans     : '+ans)
            for g in groups:
                if g['NickName'] == name:
                    to_group = g['UserName']
                    itchat.send(ans,to_group)
                    print ("send ok!")
            break
        else:
            flag = 0
            
def action_update():
    while True:
        getGroupJson()
        time.sleep(3600*2)  #两小时更新一次

#从文件读取json数据
def readJsonInfo():
    with open('data.json', 'r') as f:
        tmpData = json.load(f)
        return tmpData

#查询好友列表/群信息
def getGroupJson():
    '''获取群的username，对群成员进行分析需要用到'''
    global groupNum
    groups = itchat.get_chatrooms(update=True)
    for g in groups:
        if g['NickName'] == name:
            to_group = g['UserName']
            strSign = str(datetime.datetime.now().month)+'-'+str(datetime.datetime.now().day)+"开始签到"
            itchat.send(strSign,to_group)
            RoomList = {}
            groupNum = ''
            if len(g['MemberList']) == 0:
                RoomList = readJsonInfo()
                #groupNum = RoomList['UserName']
            else:
                RoomList = g
            groupNum = g['UserName']
            print('最新的groupID:  '+groupNum)
            return RoomList

def statistic(stuInfo):
    unSignList = []
    for usr in stuInfo:
        if usr not in avoidRepeatDic:
            unSignList.append(usr)
    return unSignList
    
#监听群消息记录
@itchat.msg_register([itchat.content.TEXT], isGroupChat=True)    #群消息的处理
def print_content(msg):
    global cnt
    print("fromusr:  "+msg['FromUserName'])
    print("tousr;  "+msg['ToUserName'])
    if msg['FromUserName'] == groupNum or msg['ToUserName'] == groupNum:
        if msg['Text'].find('健康') != -1 or msg['Text'].find('接触') != -1:
            cnt += 1
            print("该群发的消息为： "+msg['Text'])     #打印哪个群给你发了什么消息
            reply = msg['ActualNickName']+'签到成功，'+"目前已成功签到%d人\n"%cnt
            if msg['ActualNickName'] in avoidRepeatDic.keys():
                reply = "请勿重复签到"
            if(cnt == 32):
                reply += "\n所有人已经签到完毕，收工"
            if(cnt > 32):
                os._exit(0)
            avoidRepeatDic[msg['ActualNickName']]=1
            print("回复内容为: " + reply)
            print("当前已签到成员为：")
            for i in avoidRepeatDic:
                print(i,end='   ')
            print('')#换行
            return reply
    else:           
        print("不是该群消息")#其他群聊直接忽略
        pass

#预处理json数据初始化
def initInfo(jsonData):
    stu = []
    if len(jsonData) == 1:
        jsonData = jsonData[0]
    for person in jsonData['MemberList']:
        tmp = person['DisplayName']
        if tmp != '' and tmp != '彭小萍' and tmp != '魏老师' and tmp != '禹皓晨':
            stu.append(person['DisplayName'])
    if '张宇' not in stu:
        stu.append('张宇')
    print(len(stu))
    print(stu)
    return stu

#临时断线调整
def tmpInit():
    global cnt
    strs = "张宇   王宝佳   葛天宇   刘佳黛   黄成   王含艺   胡名洋   吴翰霖   于纯核   朱楠"
    datas = strs.split("   ")
    for i in datas:
        avoidRepeatDic[i] = 1
        cnt += 1
    print('初始化结果为%d人'%cnt)
    print(avoidRepeatDic)

if __name__ == '__main__':
    #tmpInit()
    print('————————————————————自动回复程序启动——————————————————')
    itchat.auto_login()
    jsonData = getGroupJson()
    studentInfo = initInfo(jsonData)
    thr_update = threading.Thread(target=action_update)#自动更新id线程
    thr_update.start()
    thr_remind = threading.Thread(target=action,args=(studentInfo,))#中午提醒线程
    thr_remind.start()
    itchat.run()
