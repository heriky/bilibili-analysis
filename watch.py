import pymongo
import time

client = pymongo.MongoClient('localhost', 27017)
db = client['bilibili']
user_table = db['user']

if __name__ == '__main__':
  while True:
    time.sleep(5)
    count = user_table.find({}).count()
    print('current count:{}'.format(count))

