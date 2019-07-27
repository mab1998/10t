import requests
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool as ThreadPool
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os, signal
import time
import json
import pymongo
from selenium.webdriver.support.ui import WebDriverWait
import logging
from pprint import pprint
# from seleniumwire import webdriver
import pickle
#logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
import json
import subprocess
import random

script="""
            (function(XHR) {
              "use strict";

              var element = document.createElement('div');
              element.id = "interceptedResponse";
              element.appendChild(document.createTextNode(""));
              document.body.appendChild(element);

              var open = XHR.prototype.open;
              var send = XHR.prototype.send;

              XHR.prototype.open = function(method, url, async, user, pass) {
                this._url = url; // want to track the url requested
                open.call(this, method, url, async, user, pass);
              };

              XHR.prototype.send = function(data) {
                var self = this;
                var oldOnReadyStateChange;
                var url = this._url;

                function onReadyStateChange() {
                  if(self.status === 200 && self.readyState == 4 /* complete */) {
                    document.getElementById("interceptedResponse").innerHTML +=
                      '*****'+ self.responseText;
                  }
                  if(oldOnReadyStateChange) {
                    oldOnReadyStateChange();
                  }
                }

                if(this.addEventListener) {
                  this.addEventListener("readystatechange", onReadyStateChange,
                    false);
                } else {
                  oldOnReadyStateChange = this.onreadystatechange;
                  this.onreadystatechange = onReadyStateChange;
                }
                send.call(this, data);
              }
            })(XMLHttpRequest);
            """
def check_kill_process(pstring):
    p = subprocess.Popen("taskkill /im {} /F".format(pstring), stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    # print("Command output : ", output)
    # print("Command exit status/return code : ", p_status)
def get_data(url):
    try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-images")

            client = pymongo.MongoClient("mongodb://localhost:27017/",username='admin',password='123456')
            db = client["10times"]
            print('process:{}'.format(url))

            driver = webdriver.Chrome(chrome_options=chrome_options,executable_path="./chromedriver",)

            wait = WebDriverWait(driver, 10)
            driver.get(url)
            cook=db.cookies.find({'status': 'Success'})
            cc=random.randint(0,cook.count())
            # cookies = pickle.load(open("cookies_{}.pkl".format('6'), "rb"))
            cookies=cook[cc]
            for cookie in cookies['cookies']:
                driver.add_cookie(cookie)

            driver.execute_script(script=script)

            # del driver.requests
            driver.find_element_by_css_selector('a.btn.btn-xs.btn-default.x-ob-cd').click()


            wait.until(lambda driver: driver.execute_script("return jQuery.active == 0"))


            data=driver.find_element_by_css_selector('#interceptedResponse').text.split('*****')



            for dd in data:
                if 'company_contacts' in dd:
                    break
                    # pprint(dict(request.headers))
            data_ = dd
            data = json.loads(data_)
            # event_website=''
            # db.info.update_one({'url': url}, {'$set': {'event_website': event_website}})
            event_website=data['event_website']
            i=1
            dict={}
            contact={}
            for contact in data['contacts']:

                # dict[i-1]={'name_{}'.format(i):contact['name'],'designation_{}'.format(i): contact['designation'],'email_{}'.format(i): contact['email']}
                db.info.update_one({'url': url}, {'$set': {'event_website':event_website,'name_{}'.format(i):contact['name'],'designation_{}'.format(i): contact['designation'],'email_{}'.format(i): contact['email']}}, upsert=False)
                i=i+1
            # print(db.info.find({'url': url})[0])
            # db.cookies.update_one({'cookies': cookies}, {'$set': {'status': 'Success'}})
    except Exception as e:
            # print("error 1",e)
            db.cookies.update_one({'cookies': cookies}, {'$set': {'status':'Fault'}})
            try:
                driver.quit()

                # get_data(url)
            except Exception as e:
                de=e
                # print("error 2",e)
    try:
        db.info.find({'url': url})[0]['email_1']
        db.info.update_one({'url': url}, {'$set': {'status': 'Success'}})
    except:
        print('Faild  : {}'.format(url))
    #             get_data(url)

    print('progress processing    {}/{}'.format(db.info.find({'status': 'Success'}).count(),db.info.find().count()))

    return


if __name__ == "__main__":

        # urls=np.loadtxt('domain-names.txt',delimiter=',',dtype='|U60')
        client = pymongo.MongoClient("mongodb://40.117.94.106:27017/")
        db = client["10times"]


        #data_url = db.info.find({'status': 'Fault'})
        #data_url.count()
        #rows = []
        #for dd in data_url:
        #    rows.append(dd['url'])


        #print(len(rows))
        # url=rows[2]
        # rows=rows[21:30]
        # for url in rows:
        #     print(db.info.find({'url': url})[0])

        data_url = db.info.find({'status': 'Fault'}).limit(16000)
        #data_url = db.info.find({'status': 'Fault'}).skip(16000).limit(16000)

        print(data_url.count())
        rows = []
        for dd in data_url:
            rows.append(dd['url'])
        len(rows)
        status=True
        k=0
        while status :
            print('killing process chrome and start again')
            check_kill_process('chrome')
            check_kill_process('chromedriver')

            a=k*80
            b=(k+1)*80
            row=rows[a+1:b]
            if k>=197:
                status = False

            try:
                pool = ThreadPool(4)
                results = pool.map(get_data, row)
                pool.close()
                pool.join()


            except Exception as e:
                print('erro:{}'.format(e))
                time.sleep(10)
                pass
           # print('killing process chrome and start again')
            #check_kill_process('chrome')
            #check_kill_process('chromedriver')
            #k=k+1
        print('==================================================================================')
        print('==================================================================================')

        print('====================      scraping domains data was Done !     ====================')






#
# cook = db.cookies.find()
#
# for cookie in cook:
#     db.cookies.update_one({'cookies': cookie['cookies'][0]}, {'$set': {'status': 'Success'}})
#
# db.cookies.find({'cookies': cookie['cookies']})[0]['status']

