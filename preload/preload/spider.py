import requests
from random import randint
from lxml import etree

def weather(city):

    ### 获取温度   
    # 随机取7-8月某个日期并拼接成要爬取的url
    m = str(randint(7, 8))
    month = '0' + m
    d = str(randint(1, 31))
    if len(d) == 1:
        day = '0' + d
    else:
        day = d
    date = '2020' + month + day
    d = '2020.'+ m +'.'+ d
    url = 'http://www.tianqihoubao.com/lishi/' + city +'/'+ date +'.html'

    # 模拟浏览器访问，并获取网页源码
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0"
    }
    response = requests.get(url, headers = headers)
    html = response.content.decode('utf-8', 'ignore')

    # 对网页源码进行解析，提取并格式化温度数据
    tree = etree.HTML(html)
    try:
        t_max = tree.xpath("//td[@style='color:#E54600']/b/text()")[0]
        t_min = tree.xpath("//td[@style='color:#000065']/b/text()")[0]
        t = (int(t_max) + int(t_min)) / 2
        t = int(t)
        
    # 温度提取错误时则使用默认数据避免程序崩溃
    except:
        temperature = {'beijing':26, 'foshan':30, 'shanghai':28, 'zhengzhou':26, 'chengdu':26, 'changchun':22, 'xian':25}
        t = temperature[city]

    ### 获取湿度
    # 根据城市取对应的7、8月平均湿度
    humidity = {'beijing':68, 'foshan':75, 'shanghai':73, 'zhengzhou':70, 'chengdu':78, 'changchun':74, 'xian':72}
    h = humidity[city]
    
    return d, str(t), str(h)