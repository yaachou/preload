from django.shortcuts import render
from socket import *
import time
import json

from . import spider

CARDS = []
TIMES = {}

def index(request):

    
    return render(request, 'index.html')

def process(request):

    ### 获取前端登录信息 ###
    card = request.POST.get('card')
    hotel = request.POST.get('hotel')
    room = request.POST.get('room')
    city = hotel[:-3]
    
    ### 检查输入的模拟身份证号码格式 ###
    errors = []
    number = ['0','1','2','3','4','5','6','7','8','9']
    for i in card:
        if i not in number:
            errors.append('【字符】只能为数字，请检查后重试！')
            errors = {'error': errors}
            return render(request, 'error.html', errors)
    if len(card) != 10:
        errors.append('【位数】采用10位数字进行模拟，请检查后重试！')
        if len(card) < 10:
            errors = {'error': errors}
            return render(request, 'error.html', errors)
    if int(card[0])<1 or int(card[0])>7:
        errors.append('【第1位】为地理区划，取值为1-7，请检查后重新输入！')
    if int(card[1:5]) > 2020 or int(card[5:7]) > 12 or int(card[7:9]) > 31:
        errors.append('【第2-9位】为出生年月日，请检查后重新输入！')
    if int(card[9])<1 or int(card[9])>2:
        errors.append('【第10位】为性别，1为男性、2为女性，请检查后重新输入！')
    if errors != []:
        errors = {'error': errors}
        return render(request, 'error.html', errors)

    ### 利用爬虫获取日期、温度、湿度信息 ###
    date, temp, humi = spider.weather(city)

    ### 与机器学习服务器进行第一次通信 ###
    data = {"type":"check_in","msg":{"location":hotel,"ID":card,"room":room,"temperature":temp,"humidity":humi}}
    try:
        feedback = transfer(data)
        if feedback['type'] == 'error':
            error = ['【账号】当前身份证号码已被登录，请检查后重新输入！']
            error = {'error': error}
            return render(request, 'error.html', error)
    
    ### 机器学习服务器未开启 ###
    except ConnectionRefusedError:
        error = ['【服务器】当前机器学习服务器未开启，请稍后再试！']
        error = {'error': error}
        return render(request, 'error.html', error)

    ### 对从服务器得到的数据进行提取 ###
    times = feedback['msg']['times']
    mode = feedback['msg']['mode']
    apmv = feedback['msg']['apmv']
    apmv = float(format(apmv, '.2f'))
    pmv = feedback['msg']['pmv']
    pmv = float(format(pmv, '.2f'))
    p_t = feedback['msg']['temperature']
    p_v = feedback['msg']['velocity']
    p_d = feedback['msg']['direction']

    ### 利用session向预载页面传值 ###
    request.session['card'] = card
    request.session['city'] = city
    request.session['mode'] = mode
    request.session['date'] = date
    request.session['temp'] = temp
    request.session['times'] = times
    request.session['pmv'] = pmv
    request.session['apmv'] = apmv
    request.session['t'] = p_t
    request.session['v'] = p_v
    request.session['d'] = p_d

    return render(request, 'process.html')

def preload(request):
     
    # 获取当地时间并格式化
    TIME = time.strftime("%Y-%m-%d %H:%M", time.localtime())
    
    ### 加载天气插件 ###
    city = request.session.get('city')
    src = "https://i.tianqi.com?c=code&id=1&color=%23FFC000&icon=1&py=" +city+ "&wind=1&num=1&site=14"

    ### 获取需要在前端显示的数据 ###
    card = request.session.get('card')
    mode = request.session.get('mode')
    temp = request.session.get('temp')
    date = request.session.get('date')
    times = request.session.get('times')
    pmv = request.session.get('pmv')
    apmv = request.session.get('apmv')

    Mode = {'shutdown':'关闭','cold':'制冷','hot':'制热'}
    mode = Mode[mode]

    times = str(times)
    temp = str(temp)
    pmv = str(pmv)
    apmv = str(apmv)

    ### 展示默认的温度、风量、风向值 ###
    t = request.session.get('t')
    v = request.session.get('v')
    d = request.session.get('d')

    ### 判断空调是否需要提前开启 ###
    if mode == '关闭':
        tip1 = '客户 ' +card+ ' 第 ' +times+ ' 次在本系统登记入住，房间此前室温' +temp+ '℃ (随机爬取日期' +date+ '的温度)，为适宜温度(23-27℃)，空调默认关闭，如有需要可自行调节。'
        tip2 = ''
        t = 25
        v = 3
        d = 3
    else:
        tip1 = '客户 ' +card+ ' 第 ' +times+ ' 次在本系统登记入住，房间此前室温' +temp+ '℃ (随机爬取日期' +date+ '的温度)，' +mode+  '模式开启，空调最佳参数预载完毕！'
        tip2 = '（当前aPMV=' +apmv+ '，PMV=' +pmv+ '）'

    ### 获得调整后的空调参数 ###
    if request.method == 'POST':
        temp = request.POST.get('temperature')
        velo = request.POST.get('velocity')
        velo_value = str(int(velo) * 0.05)
        dire = request.POST.get('direction')

        ### 与机器学习服务器进行第二次通信 ###
        data = {"type":"feedback","msg":{"ID":card,"times":times,"temperature":temp,"velocity":velo_value,"direction":dire}}
        try:
            feedback = transfer(data)
            if feedback['type'] == 'error':
                if feedback['msg'] == 'ID':
                    error = ['【账号】当前身份证号码未正常登出，请换个号码重新输入！']
                if feedback['msg'] == 'feedback':
                    error = ['【反馈】数据与之前相同，默认为无效修改，请检查后重新输入！']
                else:
                    error = ['【账号】还未登录，无法进行此操作，请重新登录！']
                error = {'error': error}
                return render(request, 'error.html', error)
    
        ### 机器学习服务器未开启 ###
        except ConnectionRefusedError:
            error = ['【服务器】当前机器学习服务器未开启，请稍后再试！']
            error = {'error': error}
            return render(request, 'error.html', error)

        ### 机器学习服务器状态正常则继续 ###    
        mode = feedback['msg']['mode']
        apmv = feedback['msg']['apmv']
        apmv = float(format(apmv, '.2f'))
        pmv = feedback['msg']['pmv']
        pmv = float(format(pmv, '.2f'))

        mode = Mode[mode]
        pmv = str(pmv)
        apmv = str(apmv)

        ### 将手动修改后的温度、风量、风向展示出来 ###
        t = temp
        v = velo
        d = dire

        tip1 = '客户 ' +card+ ' 第 ' +times+ ' 次在本系统登记入住，根据你的手动调节，相关数据已更新！'
        tip2 = '（当前aPMV=' +apmv+ '，PMV=' +pmv+ '）'

    result = {'time': TIME, 'src': src, 'tip1': tip1, 'tip2': tip2, 't': t, 'v': v, 'd': d}
    return render(request, 'preload.html', result)

def exit(request):
    ID = request.session.get('card')
    times = request.session.get('times')
    data = {"type":"check_out","msg":{"ID":ID,"times":times}}
    feedback = transfer(data)
    if feedback['type'] == 'error':
        error = ['【账号】还未登录，无法进行此操作，请重新登录！']
        error = {'error': error}
        return render(request, 'error.html', error)
    if feedback['type'] == 'check_out_ack':
        tip = '退出成功，即将跳转...'
        tip = {'tip':tip}
    return render(request, "exit.html" ,tip)

def team(request):
    return render(request, 'team.html')

### 参数为字符串，返回值为字典类型 ###
def transfer( data ):
    host = '127.0.0.1'
    port = 10240
    size = 1024
    addr = (host, port)

    data = str(data)
    data = data.replace(' ','')
    data = data.replace("'",'"')

    client = socket(AF_INET, SOCK_STREAM)
    client.connect(addr)
    
    client.send(data.encode())
    client.send('\n'.encode())
    print('已发送：', data)

    feedback = client.recv(size).decode()
    print('已接受：', feedback)
    feedback = eval(feedback)
    client.close()

    return feedback

