import requests
from datetime import datetime
import random


res = requests.get('http://api.xicidaili.com/free2016.txt')
proxy_list = res.text.split('\r\n')

def get(url):
  headers = {}
  proxies = {}
  res = requests.get(url, proxies=proxies)
  print(res.text)

def post(user_id):
  data = {
    "_": int(datetime.timestamp(datetime.now())*1000),
    "mid": user_id
  }
  headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/534.55.3 (KHTML, like Gecko) Version/5.1.5 Safari/534.55.3',
    'Referer': 'http://space.bilibili.com',
    'X-Requested-With': 'XMLHttpRequest'
  }
  url = 'http://space.bilibili.com/ajax/member/GetInfo'
  rs = None
  while rs == None:
    try:
      print('正在尝试代理: {}'.format(current_proxy))
      current_proxy = random.choice(proxy_list)
      proxies = {'http': 'http://'+ current_proxy}
      res = requests.post(url, data=data, headers=headers, proxies=proxies)
      rs = res.text
    except Exception as e:
      print('无效的代理: {}'.format(current_proxy))
      proxy_list.remove(current_proxy)
  return rs

if __name__ == '__main__':
  rs = post(1)
  if rs!=None:
    print(rs)
  #get('http://www.baidu.com')
