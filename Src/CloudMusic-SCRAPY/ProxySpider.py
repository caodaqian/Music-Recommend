#!/bin/python3

# 爬取西刺网上面的代理生成一个 ip：port 的文件
# CDQ

import os
import random
import re
import time
import urllib.error
import urllib.parse
import urllib.request

os.chdir('g:\Coding Project\Music Recommendation System\Src')
filepath = '../Data/EnableProxy.txt'

url = 'https://www.xicidaili.com/nn/'
number = int(input('输入要爬取多少页：'))
# finish = int(input('输入需要爬取多少有效代理：'))
finish = 20
header = [{'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36'}, {
    'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'}, {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)'}]

# 爬取对应的IP地址和port写入到iplist.txt
proxylist = []
start = random.randint(1, 7)
for i in range(start, start + number):
    cururl = url + str(i)
    request = urllib.request.Request(cururl, headers=random.choice(header))
    time.sleep(random.randrange(1, 4))
    response = urllib.request.urlopen(request)
    # print(response.read().decode())
    html = response.read().decode()
    iplist = re.findall(
        r'(?:(?:2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(?:2[0-4]\d|25[0-5]|[01]?\d\d?)', html)
    portlist = re.findall(r'<td>(\d+)<\/td>', html)
    print("查找当前第%d页，正则匹配到ip%d个，匹配到端口%d个" % (i, len(iplist), len(portlist)))
    for i in range(0, len(portlist)):
        proxylist.append(iplist[i] + ":" + portlist[i] + "\n")

# 测试爬取的代理是否能够使用，可以使用的话写入文件保存
test_url = 'http://httpbin.org/ip'
if os.path.isfile(filepath):
    os.remove(filepath)
fp = open(filepath, 'w')
current = 0
start = 0
total = len(proxylist)
for proxy in proxylist:
    try:
        start += 1
        print('构建代理：', proxy[:-1], start/total, "%")
        handler = urllib.request.ProxyHandler(
            {"http": r"http://" + proxy[:-1]})
        opener = urllib.request.build_opener(handler)
        response = opener.open(test_url, timeout=2)
        html = response.read().decode('utf-8')
        ip = proxy.split(':')[0]
        if ip in html:
            # 写入到文件之中
            fp.write(proxy)
            fp.flush()
            print('此代理可用, 已成功保存', proxy[:-1])
            current += 1
            if current >= finish:
                break
        else:
            print('ProxyError   无法连接网络，error ip_port=%s' % proxy[:-1])
    except urllib.error.HTTPError as eh:
        print("HTTPError    error reason=%s, error code=%d, error ip_port=%s" %
              (eh.reason, eh.code, proxy[:-1]))
    except urllib.error.URLError as eu:
        print("URLError error reason=%s, error ip_port=%s" %
              (eu.reason, proxy[:-1]))
    except Exception as e:
        print('UnknownError error ip_port=%s' % proxy[:-1])
fp.close()
