import time
import requests
from bs4 import BeautifulSoup
import lxml

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

base_url = 'http://space.bilibili.com/21155'
info_url = base_url+'/#!/index'


def fetch_valid_src(url, required):
  '''
  获取js执行过后的网页内容，required 为指定元素的xpath值
  '''
  driver = webdriver.PhantomJS(executable_path=r'F:\Program Files\phantomjs\bin\phantomjs.exe')
  driver.get(url)

  try:
    dr = WebDriverWait(driver, 5)
    # dr.until(lambda the_driver: the_driver.find_element_by_xpath('//div[@class="item uid"]').is_displayed())
    dr.until(lambda the_driver: the_driver.find_element_by_xpath(required).is_displayed())
    print('用户信息已解析完成, 具体查看截图文件。')
    driver.get_screenshot_as_file('./test.png')
  except Exception as e:
    print('爬虫异常:', e)
    raise e
  rs = driver.page_source
  driver.quit()
  return rs

# 解析基本信息
def parse_user_info(src):
  # 查找元素
  soup = BeautifulSoup(src, 'lxml')
  regtime = soup.select('.regtime .text')[0].string.split(' ')[1]
  birthday = soup.select('.birthday .text')[0].string

  geo = soup.select('.geo .text')[0].string.split(' ')
  if len(geo)>=2:
    province = geo[0]
    city = geo[1]
  else:
    province = city = None

  follow = soup.select(".data-gz .quantity")[0].string
  fans = soup.select(".data-fs .quantity")[0].string
  follow_url = '/#!/fans/follow/{pn}'.format(pn=1)
  fans_url = '/#!/fans/fans/{pn}'.format(pn=1)

  # 解析为具体值
  print(regtime)
  print(birthday)
  print(province, city)
  print(follow)
  print(fans)
  return {
    'regtime': regtime,
    'birthday': birthday,
    'province': province,
    'city': city,
    'follow': follow,
    'fans': fans
  }

# 解析用户的[粉丝]和用户[关注]
def parse_friends(src, num):
  '''
  解析粉丝列表和跟随者列表, num为粉丝或者跟随者数目，用于判断分页数目
  '''
  soup =  BeautifulSoup(src, 'lxml')
  user_list = soup.select('#fans-list')
  print(soup)

if __name__ == '__main__':
  #src = fetch_valid_src(info_url, '//div[@class="item uid"]')
  #parse_user_info(src)
  #parse_friends('http://space.bilibili.com/21040155/#!/fans/follow/1')
  fetch_valid_src('http://space.bilibili.com/21040155/#!/fans/follow/1', '//div[@class="list-item clearfix"]')