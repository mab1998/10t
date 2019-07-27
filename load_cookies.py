import pickle
import pymongo
import numpy as np
import os
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["10times"]


data = db.info.find()
for dd in data:
    db.info.update_one({'url': dd['url']}, {'$set': {'status': 'Fault'}})









