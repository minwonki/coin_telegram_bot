# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from coins import Coin
from telegram import testCall

import jinja2
import webapp2

import os
import urllib
import urllib2
import json
import logging
import re
import math

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END imports]

coinKeys = ['btc','bcc','eth','etc','xrp','qtum','neo','ltc','btg','dash']
hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6)'}
noti_site = 'https://crix-api-endpoint.upbit.com/v1/crix/candles/minutes/1?code=CRIX.UPBIT.KRW-'
cal_site = 'https://crix-api-endpoint.upbit.com/v1/crix/candles/days?code=CRIX.UPBIT.KRW-'

openKey = 'openingPrice'
highKey = 'highPrice'
lowKey = 'lowPrice'
lastKey = 'tradePrice'

class MainPage(webapp2.RequestHandler):
    def get(self):
        coins = Coin.query().order(-Coin.date).fetch(len(coinKeys))
        template_values = {
            'coins': coins,
        }
        testCall("mwk")
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

class Notice(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        coins = Coin.query().order(-Coin.date).fetch(len(coinKeys))
        for coin in coins:
	  site = noti_site + coin.name + '&count=1'
          req = urllib2.Request(site, headers=hdr)
          body = json.load(urllib2.urlopen(req))
          obj = body[0]

          if int(obj[lastKey]) > coin.buy and coin.notice == False:
              noise_coins = Coin.query(Coin.name == str(coin.name)).order(-Coin.date).fetch(30)
              noise = 0.0
              for noise_coin in noise_coins:
                  noise = noise + noise_coin.noise
              msg = "Buy:" + coin.name + ", Price:" + str(coin.buy) + ", Noise:" + str(noise/len(noise_coins))
              coin.notice = True
              coin.put()
              logging.info(msg)
              #broadcast("Buy:" + coin.name + ",price:" + str(coin.buy) + ", Noise:" + str(noise/len(noise_coins)))

class Calculate(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        coins = Coin.query().order(-Coin.date).fetch(len(coinKeys))

        for coin in coins:
          if coin.notice:
	    site = noti_site + coin.name + '&count=1'
            req = urllib2.Request(site, headers=hdr)
            body = json.load(urllib2.urlopen(req))
            obj = body[0]
            msg = coin.name + " -> return:" + str((float(obj[lastKey])/float(coin.buy) - 1)*100) + "%"
            #broadcase(msg)
            logging.info(msg)

        for key in coinKeys:
	  site = cal_site + key + '&count=2'
          req = urllib2.Request(site, headers=hdr)
          body = json.load(urllib2.urlopen(req))
          obj = body[1]

          logging.info("key:"+key+",last:"+str(obj[lastKey]))
          buy = float(obj[lastKey]) + 0.5 * (float(obj[highKey]) - float(obj[lowKey]))
          noise = 1 - math.fabs(float(obj[openKey]) - float(obj[lastKey])) / (float(obj[highKey]) - float(obj[lowKey]))
          coin = Coin(name=key, buy=int(buy), noise=float(noise))
          coin.put()
          
class AddPage(webapp2.RequestHandler):
    def post(self):
        coin_name = self.request.get('name')
        coin_buy = self.request.get('buy')
        coin_noise = self.request.get('noise')
        coin = Coin(name=coin_name, buy=int(coin_buy), noise=float(coin_noise))
        coin.put()
        self.redirect('/')

class DelPage(webapp2.RequestHandler):
    def post(self):
        urlsafe = self.request.get('urlsafe')
        coin_key = ndb.Key(urlsafe=urlsafe)
        coin = coin_key.get()
        coin.key.delete() 
        self.redirect('/')
       
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/task/add', AddPage),
    ('/task/delete', DelPage),
    ('/task/calc', Calculate),
    ('/task/notice', Notice),
], debug=True)
