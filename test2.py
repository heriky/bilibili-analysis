import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import pymongo
import random
from collections import deque
from multiprocessing import Pool


class Spider(object):

  def __init__(self):
    # 初始化数据库
    client = pymongo.MongoClient('localhost', 27017)
    db = client['bilibili']
    self.user_table = db['user']
    self.proxy_list = []

  def get_proxy_list(self):
    proxy_src = 'http://api.xicidaili.com/free2016.txt'
    res = requests.get(proxy_src)
    return res.text.split('\r\n')

  def get_user_info(self, user_id):
    '''
    通过ajax请求获取特定用户信息
    '''
    request_url = 'http://space.bilibili.com/ajax/member/GetInfo'
    data = {
      "_": int(datetime.timestamp(datetime.now())*1000),
      "mid": user_id
    }

    # 变换user-agent和proxy， 防止爬虫被网站屏蔽
    user_agent = random.choice([
      'Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0',\
      'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',\
      'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/534.55.3 (KHTML, like Gecko) Version/5.1.5 Safari/534.55.3',\
      'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)',\
      'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/533.21.1 (KHTML, like Gecko) Version/5.0.5 Safari/533.21.1',\
      'Mozilla/5.0 (Windows; U; Windows NT 5.1; ) AppleWebKit/534.12 (KHTML, like Gecko) Maxthon/3.0 Safari/534.12',\
      'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727; TheWorld)'
      ])
    headers ={
      'User-Agent': user_agent,
      'Referer': 'http://space.bilibili.com',
      'X-Requested-With': 'XMLHttpRequest'
    }

    if len(self.proxy_list) == 0:
      self.proxy_list = self.get_proxy_list()

    rs = None
    while rs == None:
      print('当前代理个数 :', len(self.proxy_list))
      try:
        current_proxy = random.choice(self.proxy_list)
        print('尝试新代理: {}'.format(current_proxy))
        proxies = {'http': 'http://'+ current_proxy}
        res = requests.post(request_url, data=data, headers=headers, proxies=proxies, timeout=3)
        rs = json.loads(res.text)
        print('有效代理: {}\n'.format(current_proxy))
      except BaseException: # Exception 不是异常的基类
        if len(self.proxy_list) <= 0:
          print('数据即可为空，重新获取代理集合。')
          self.proxy_list = self.get_proxy_list()
        else:
          print('无效的代理: {}, 剔除。\n'.format(current_proxy))
          self.proxy_list.remove(current_proxy)
    return rs


  def parse_user_info(self, info):
    '''
    解析用户信息, info是rs['data']
    '''
    mid = info.get('mid')
    name = info.get('name')
    sex = info.get('sex') # 男，女，保密
    regtime = info.get('regtime') # datetime.fromtimestamp(1452170229)
    place = info.get('place') # 未填写的时候为""
    birthday = info.get('birthday') # 未填写年份的时候的时候为0000-10-19， 未填写时为0000-01-01
    article = info.get('article') # 投稿数目
    level = info.get('level_info').get('current_level') # 等级
    attention = info.get('attention') # 关注数
    fans = info.get('fans')  # 粉丝数目
    attentions = info.get('attentions') # 被关注人的id列表

    # 合理筛选数据
    return {
      'mid': int(mid),
      'name': name,
      'sex': sex,
      'regtime': regtime,
      'place': place,
      'birthday': birthday,
      'article': article,
      'level': level,
      'attention': attention,
      'fans': fans,
      'attentions': attentions
    }


  def data2db(self, data):
    '''
    数据库存储
    '''
    self.user_table.save(data)


  def looper_gen(self):
    '''
    信息提取过程，使用生成器generator
    '''
    # 可以在中断爬取后接上一次继续
    last_item = self.user_table.find({}).sort([('mid', pymongo.DESCENDING)]).limit(1)
    last_item = list(last_item) # curosr类型转换为list类型
    if len(last_item) == 0:
      uid = 0
    else:
      uid = last_item[0]['mid'] + 1

    print('起始mid为:', uid)
    while True:
      rs = self.get_user_info(uid)
      if rs['status'] == False:
        yield uid
      else:
        data = self.parse_user_info(rs['data'])
        self.data2db(data)
        print('------------->uid {} is fetched successfully!\n'.format(uid))
      uid += 1


  def looper(self):
    '''
    生成器的执行过程，处理无效的id
    '''
    prev_fail = 0 # 前一个失败的序号, 如果发现连续两个失败，则认定为封顶
    gen = self.looper_gen()
    fails = deque()
    while True:
      fail_id = next(gen)
      # if len(fails) == 10: # 容量为10的列表
      #   fails.popleft()
      # fails.append(fail_id)

      # # 连续10个id失败则，则表示抓取完毕
      # base = fails[0]
      # if sum(list(map(lambda x: x-base, fails))) == 10:
      #   break;
    print('抓取完毕!')


if __name__ == '__main__':
  spider = Spider()
  spider.looper()
  pool = Pool(4)
  pool.apply_async()


# 改进
# 1. IP代理
# 2. 多进程爬取